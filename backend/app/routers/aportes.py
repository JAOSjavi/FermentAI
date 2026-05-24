import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas
from app.services.zip_validator import validate_zip
from app.services.csv_parser import parse_metadata_csv
from app.services import notificaciones as notif_svc
from app import minio_client

router = APIRouter(prefix="/api/aportes", tags=["aportes"])

RATE_LIMIT_PER_HOUR = 5


def _check_rate_limit(user_id: int, db: Session):
    from datetime import timedelta
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    count = db.query(models.Aporte).filter(
        models.Aporte.usuario_id == user_id,
        models.Aporte.fecha_subida >= one_hour_ago,
    ).count()
    if count >= RATE_LIMIT_PER_HOUR:
        raise HTTPException(status_code=429, detail="Límite de 5 subidas por hora alcanzado")


@router.post("/subir", response_model=schemas.AporteOut, status_code=status.HTTP_201_CREATED)
async def subir_aporte(
    file: UploadFile = File(...),
    descripcion: Optional[str] = Form(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_rate_limit(current_user.id, db)

    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .zip")

    # Guardar temporalmente
    tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    try:
        content = await file.read()
        zip_size = len(content)
        tmp.write(content)
        tmp.flush()
        tmp.close()

        # Validar
        result = validate_zip(tmp.name, zip_size)
        if not result.valid:
            raise HTTPException(status_code=400, detail={"errores": result.errors})

        ferm_code = result.ferm_code

        # Buscar o crear fermentación
        ferm = db.query(models.Fermentacion).filter(
            models.Fermentacion.codigo == ferm_code
        ).first()
        if not ferm:
            ferm = models.Fermentacion(codigo=ferm_code)
            db.add(ferm)
            db.flush()

        # Determinar estado según rol
        estado = (
            models.EstadoAporteEnum.aprobado
            if current_user.rol == models.RolEnum.investigador
            else models.EstadoAporteEnum.pendiente_revision
        )
        folder = "approved" if estado == models.EstadoAporteEnum.aprobado else "pending"

        aporte = models.Aporte(
            usuario_id=current_user.id,
            fermentacion_id=ferm.id,
            estado=estado,
            descripcion=descripcion,
        )
        db.add(aporte)
        db.flush()

        ruta_base = f"{folder}/{aporte.id}/{ferm_code}/imagenes"
        aporte.ruta_minio = ruta_base

        # Parsear CSV
        img_prefix = f"{ferm_code}/imagenes/"
        csv_path_in_zip = f"{ferm_code}/{ferm_code}_metadata.csv"
        zf = zipfile.ZipFile(tmp.name)
        csv_bytes = zf.read(csv_path_in_zip)
        rows = parse_metadata_csv(csv_bytes)

        # Subir imágenes a MinIO
        minio_client.ensure_bucket()
        for entry in zf.namelist():
            if entry.startswith(img_prefix) and not entry.endswith("/"):
                img_data = zf.read(entry)
                filename = entry.split("/")[-1]
                object_key = f"{ruta_base}/{filename}"
                minio_client.upload_bytes(img_data, object_key)

        # Guardar metadatos
        row_map = {r["imagen"]: r for r in rows}
        for entry in zf.namelist():
            if entry.startswith(img_prefix) and not entry.endswith("/"):
                filename = entry.split("/")[-1]
                row = row_map.get(filename, {})
                meta = models.MetadatoImagen(
                    aporte_id=aporte.id,
                    imagen=filename,
                    **{k: v for k, v in row.items() if k != "imagen"},
                )
                db.add(meta)

        # Notificar si es colaborador
        if current_user.rol == models.RolEnum.colaborador:
            notif_svc.notificar_investigadores(
                db, aporte.id,
                f"Nuevo aporte pendiente de revisión de {current_user.nombre} para {ferm_code}",
            )

        db.commit()
        db.refresh(aporte)
        return aporte

    finally:
        os.unlink(tmp.name)


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
        prefix = f"{'approved' if aporte.estado == models.EstadoAporteEnum.aprobado else 'pending'}/{aporte_id}/"
        minio_client.delete_prefix(prefix)

    notif_svc.crear_notificacion(
        db, current_user.id,
        models.TipoNotificacionEnum.aporte_eliminado,
        f"Eliminaste el aporte #{aporte_id} (Fermentación: {ferm_code}). Motivo: {body.motivo}",
        aporte_id=None,
    )

    notif_svc.hard_delete_aporte(db, aporte)
    db.commit()

    return {"ok": True, "id": aporte_id}
