import io
import re
import zipfile
from dataclasses import asdict
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas
from app import minio_client
from app.services import notificaciones as notif_svc
from app.pipeline import ejecutar_pipeline, PipelineError

router = APIRouter(prefix="/api/aportes", tags=["aportes"])

RATE_LIMIT_PER_HOUR = 5
MAX_ZIP_BYTES = 2 * 1024 * 1024 * 1024
_FERM_CODE_RE = re.compile(r"^FERM(0[1-9]|1[0-2])$")


def _check_rate_limit(user_id: int, db: Session):
    from datetime import timedelta
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    count = db.query(models.Aporte).filter(
        models.Aporte.usuario_id == user_id,
        models.Aporte.fecha_subida >= one_hour_ago,
    ).count()
    if count >= RATE_LIMIT_PER_HOUR:
        raise HTTPException(status_code=429, detail="Límite de 5 subidas por hora alcanzado")


def _extract_ferm_code(names: list[str]) -> str | None:
    for name in names:
        parts = name.split("/")
        if len(parts) >= 2 and _FERM_CODE_RE.match(parts[0]):
            return parts[0]
    return None


@router.post("/subir", response_model=schemas.AporteSubidaOut, status_code=status.HTTP_201_CREATED)
async def subir_aporte(
    file: UploadFile = File(...),
    descripcion: Optional[str] = Form(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_rate_limit(current_user.id, db)

    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .zip")

    content = await file.read()

    if len(content) > MAX_ZIP_BYTES:
        raise HTTPException(status_code=400, detail="El ZIP supera el límite de 2 GB")

    # Extraer ferm_code antes de lanzar el pipeline (necesario para la FK de Fermentacion)
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            ferm_code = _extract_ferm_code(zf.namelist())
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="El archivo no es un ZIP válido")

    if not ferm_code:
        raise HTTPException(status_code=422, detail="No se encontró carpeta FERM01–FERM12 en el ZIP")

    # Crear o reutilizar Fermentacion
    ferm = db.query(models.Fermentacion).filter(
        models.Fermentacion.codigo == ferm_code
    ).first()
    if not ferm:
        ferm = models.Fermentacion(codigo=ferm_code)
        db.add(ferm)
        db.flush()

    estado = (
        models.EstadoAporteEnum.aprobado
        if current_user.rol == models.RolEnum.investigador
        else models.EstadoAporteEnum.pendiente_revision
    )

    aporte = models.Aporte(
        usuario_id=current_user.id,
        fermentacion_id=ferm.id,
        estado=estado,
        descripcion=descripcion,
    )
    db.add(aporte)
    db.flush()  # Obtener aporte.id antes de lanzar el pipeline

    # Ejecutar pipeline de depuración
    try:
        reporte_pipeline = ejecutar_pipeline(content, aporte.id)
    except PipelineError as exc:
        raise HTTPException(status_code=422, detail=exc.message)

    if not reporte_pipeline.rutas_processed:
        raise HTTPException(status_code=422, detail="No quedaron imágenes tras el procesamiento")

    # Subir CSV original a MinIO para el endpoint de descarga
    csv_key_in_zip = f"{ferm_code}/{ferm_code}_metadata.csv"
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        csv_bytes = zf.read(csv_key_in_zip)
    minio_client.upload_bytes(
        csv_bytes,
        f"processed/{aporte.id}/{ferm_code}_metadata.csv",
        content_type="text/csv",
    )

    # Crear MetadatoImagen por cada imagen procesada
    for ruta in reporte_pipeline.rutas_processed:
        filename = ruta.split("/")[-1]
        db.add(models.MetadatoImagen(aporte_id=aporte.id, imagen=filename))

    aporte.ruta_minio = f"processed/{aporte.id}"

    if current_user.rol == models.RolEnum.colaborador:
        notif_svc.notificar_investigadores(
            db, aporte.id,
            f"Nuevo aporte pendiente de revisión de {current_user.nombre} para {ferm_code}",
        )

    db.commit()
    db.refresh(aporte)

    result = schemas.AporteSubidaOut.model_validate(aporte)
    result.reporte = schemas.ReporteDepuracionOut(**asdict(reporte_pipeline))
    return result


@router.get("/me", response_model=list[schemas.AporteOut])
def mis_aportes(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Aporte)
        .filter(models.Aporte.usuario_id == current_user.id)
        .order_by(models.Aporte.fecha_subida.desc())
        .all()
    )


@router.get("/{aporte_id}/descargar-dataset")
def descargar_dataset(
    aporte_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    aporte = db.query(models.Aporte).filter(models.Aporte.id == aporte_id).first()
    if not aporte:
        raise HTTPException(status_code=404, detail="Aporte no encontrado")
    if aporte.estado != models.EstadoAporteEnum.aprobado:
        raise HTTPException(status_code=403, detail="Solo se pueden descargar aportes aprobados")

    ferm_code = aporte.fermentacion.codigo

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Imágenes procesadas
        for key in minio_client.list_objects(f"processed/{aporte_id}/"):
            if key.lower().endswith((".jpg", ".jpeg")):
                try:
                    data = minio_client.get_bytes(key)
                    zf.writestr(key.split("/")[-1], data)
                except Exception:
                    pass

        # CSV original
        csv_key = f"processed/{aporte_id}/{ferm_code}_metadata.csv"
        try:
            csv_data = minio_client.get_bytes(csv_key)
            zf.writestr(f"{ferm_code}_metadata.csv", csv_data)
        except Exception:
            pass

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{ferm_code}_dataset.zip"'
        },
    )


@router.get("/{aporte_id}", response_model=schemas.AporteDetalle)
def detalle_aporte(
    aporte_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    aporte = db.query(models.Aporte).filter(models.Aporte.id == aporte_id).first()
    if not aporte:
        raise HTTPException(status_code=404, detail="Aporte no encontrado")
    if aporte.usuario_id != current_user.id and current_user.rol != models.RolEnum.investigador:
        raise HTTPException(status_code=403, detail="Sin permiso")

    detalle = schemas.AporteDetalle.model_validate(aporte)
    if aporte.ruta_minio:
        for meta_out in detalle.metadatos:
            meta_out.url_imagen = minio_client.presigned_url(
                f"{aporte.ruta_minio}/{meta_out.imagen}"
            )
    return detalle


@router.put("/{aporte_id}/descripcion", response_model=schemas.AporteOut)
def editar_descripcion(
    aporte_id: int,
    body: schemas.EditarDescripcionRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    aporte = db.query(models.Aporte).filter(models.Aporte.id == aporte_id).first()
    if not aporte:
        raise HTTPException(status_code=404, detail="Aporte no encontrado")
    if aporte.usuario_id != current_user.id and current_user.rol != models.RolEnum.investigador:
        raise HTTPException(status_code=403, detail="Sin permiso")
    if aporte.eliminado:
        raise HTTPException(status_code=400, detail="No se puede editar un aporte eliminado")

    aporte.descripcion = body.descripcion
    db.commit()
    db.refresh(aporte)
    return aporte


@router.post("/{aporte_id}/solicitar-eliminacion", response_model=schemas.AporteOut)
def solicitar_eliminacion(
    aporte_id: int,
    body: schemas.SolicitarEliminacionRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    aporte = db.query(models.Aporte).filter(models.Aporte.id == aporte_id).first()
    if not aporte:
        raise HTTPException(status_code=404, detail="Aporte no encontrado")
    if aporte.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="Solo puedes solicitar la eliminación de tus propios aportes")
    if aporte.eliminado:
        raise HTTPException(status_code=400, detail="El aporte ya fue eliminado")
    if aporte.solicitud_eliminacion:
        raise HTTPException(status_code=400, detail="Ya existe una solicitud de eliminación pendiente")

    aporte.solicitud_eliminacion = True
    aporte.motivo_eliminacion = body.motivo
    notif_svc.notificar_investigadores(
        db, aporte.id,
        f"El colaborador {current_user.nombre} solicita eliminar el aporte #{aporte_id}. Motivo: {body.motivo}",
    )

    db.commit()
    db.refresh(aporte)
    return aporte


@router.post("/{aporte_id}/eliminar", status_code=200)
def eliminar_aporte(
    aporte_id: int,
    body: schemas.SolicitarEliminacionRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.rol != models.RolEnum.investigador:
        raise HTTPException(status_code=403, detail="Solo investigadores pueden eliminar aportes directamente")

    aporte = db.query(models.Aporte).filter(models.Aporte.id == aporte_id).first()
    if not aporte:
        raise HTTPException(status_code=404, detail="Aporte no encontrado")
    if aporte.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="Solo puedes eliminar tus propios aportes")

    ferm_code = aporte.fermentacion.codigo if aporte.fermentacion else f"#{aporte_id}"

    if aporte.ruta_minio:
        # Cubrir rutas legacy (pre-pipeline) y rutas del pipeline
        minio_client.delete_prefix(f"approved/{aporte_id}/")
        minio_client.delete_prefix(f"pending/{aporte_id}/")
        minio_client.delete_prefix(f"raw/{aporte_id}/")
        minio_client.delete_prefix(f"processed/{aporte_id}/")

    notif_svc.crear_notificacion(
        db, current_user.id,
        models.TipoNotificacionEnum.aporte_eliminado,
        f"Eliminaste el aporte #{aporte_id} (Fermentación: {ferm_code}). Motivo: {body.motivo}",
        aporte_id=None,
    )

    notif_svc.hard_delete_aporte(db, aporte)
    db.commit()

    return {"ok": True, "id": aporte_id}
