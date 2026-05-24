from sqlalchemy.orm import Session
from app import models


def hard_delete_aporte(db: Session, aporte: models.Aporte):
    fermentacion_id = aporte.fermentacion_id

    db.query(models.Notificacion).filter(
        models.Notificacion.aporte_id == aporte.id
    ).update({"aporte_id": None})
    db.flush()

    db.delete(aporte)
    db.flush()

    # Si la fermentación ya no tiene aportes, eliminarla también
    restantes = db.query(models.Aporte).filter(
        models.Aporte.fermentacion_id == fermentacion_id
    ).count()
    if restantes == 0:
        db.query(models.Fermentacion).filter(
            models.Fermentacion.id == fermentacion_id
        ).delete()


def crear_notificacion(
    db: Session,
    usuario_id: int,
    tipo: models.TipoNotificacionEnum,
    mensaje: str,
    aporte_id: int | None = None,
):
    notif = models.Notificacion(
        usuario_id=usuario_id,
        aporte_id=aporte_id,
        tipo=tipo,
        mensaje=mensaje,
    )
    db.add(notif)
    db.flush()
    return notif


def notificar_investigadores(db: Session, aporte_id: int, mensaje: str):
    investigadores = db.query(models.User).filter(
        models.User.rol == models.RolEnum.investigador
    ).all()
    for inv in investigadores:
        crear_notificacion(
            db, inv.id,
            models.TipoNotificacionEnum.nuevo_aporte_pendiente,
            mensaje,
            aporte_id,
        )
