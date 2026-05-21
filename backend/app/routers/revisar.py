from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_investigador
from app import models, schemas
from app.services import notificaciones as notif_svc
from app import minio_client

router = APIRouter(prefix="/api/revisar", tags=["revision"])


@router.get("/pendientes", response_model=list[schemas.AporteOut])
def listar_pendientes(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_investigador),
):
    return (
        db.query(models.Aporte)
        .filter(models.Aporte.estado == models.EstadoAporteEnum.pendiente_revision)
        .order_by(models.Aporte.fecha_subida.asc())
        .all()
    )


@router.get("/{aporte_id}/revisar", response_model=schemas.AporteDetalle)
def detalle_revision(
    aporte_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_investigador),
):
    aporte = _get_or_404(aporte_id, db)
    detalle = schemas.AporteDetalle.model_validate(aporte)
    if aporte.ruta_minio:
        for meta_out in detalle.metadatos:
            meta_out.url_imagen = minio_client.presigned_url(
                f"{aporte.ruta_minio}/{meta_out.imagen}"
            )
    return detalle


@router.put("/{aporte_id}/aprobar", response_model=schemas.AporteOut)
def aprobar(
    aporte_id: int,
    db: Session = Depends(get_db),
    investigador: models.User = Depends(require_investigador),
):
    aporte = _get_or_404(aporte_id, db)
    _assert_revisable(aporte)

    old_prefix = f"pending/{aporte_id}/"
    new_prefix = f"approved/{aporte_id}/"
    minio_client.copy_prefix(old_prefix, new_prefix)
    minio_client.delete_prefix(old_prefix)

    aporte.ruta_minio = aporte.ruta_minio.replace("pending/", "approved/", 1) if aporte.ruta_minio else None
    aporte.estado = models.EstadoAporteEnum.aprobado
    aporte.fecha_revision = datetime.utcnow()
    aporte.revisado_por = investigador.id

    notif_svc.crear_notificacion(
        db, aporte.usuario_id,
        models.TipoNotificacionEnum.aporte_aprobado,
        f"Tu aporte #{aporte_id} ha sido aprobado.",
        aporte_id,
    )
    db.commit()
    db.refresh(aporte)
    return aporte


@router.put("/{aporte_id}/rechazar", response_model=schemas.AporteOut)
def rechazar(
    aporte_id: int,
    body: schemas.RevisionRequest,
    db: Session = Depends(get_db),
    investigador: models.User = Depends(require_investigador),
):
    aporte = _get_or_404(aporte_id, db)
    _assert_revisable(aporte)

    if aporte.ruta_minio:
        minio_client.delete_prefix(f"pending/{aporte_id}/")

    aporte.estado = models.EstadoAporteEnum.rechazado
    aporte.observaciones = body.observaciones
    aporte.fecha_revision = datetime.utcnow()
    aporte.revisado_por = investigador.id

    notif_svc.crear_notificacion(
        db, aporte.usuario_id,
        models.TipoNotificacionEnum.aporte_rechazado,
        f"Tu aporte #{aporte_id} fue rechazado. Observaciones: {body.observaciones}",
        aporte_id,
    )
    db.commit()
    db.refresh(aporte)
    return aporte


@router.put("/{aporte_id}/solicitar-correcciones", response_model=schemas.AporteOut)
def solicitar_correcciones(
    aporte_id: int,
    body: schemas.RevisionRequest,
    db: Session = Depends(get_db),
    investigador: models.User = Depends(require_investigador),
):
    aporte = _get_or_404(aporte_id, db)
    _assert_revisable(aporte)

    aporte.estado = models.EstadoAporteEnum.correcciones_solicitadas
    aporte.observaciones = body.observaciones
    aporte.fecha_revision = datetime.utcnow()
    aporte.revisado_por = investigador.id

    notif_svc.crear_notificacion(
        db, aporte.usuario_id,
        models.TipoNotificacionEnum.correcciones_solicitadas,
        f"Tu aporte #{aporte_id} requiere correcciones: {body.observaciones}",
        aporte_id,
    )
    db.commit()
    db.refresh(aporte)
    return aporte


def _get_or_404(aporte_id: int, db: Session) -> models.Aporte:
    aporte = db.query(models.Aporte).filter(models.Aporte.id == aporte_id).first()
    if not aporte:
        raise HTTPException(status_code=404, detail="Aporte no encontrado")
    return aporte


def _assert_revisable(aporte: models.Aporte):
    if aporte.estado not in (
        models.EstadoAporteEnum.pendiente_revision,
        models.EstadoAporteEnum.correcciones_solicitadas,
    ):
        raise HTTPException(status_code=400, detail=f"No se puede revisar un aporte en estado '{aporte.estado}'")
