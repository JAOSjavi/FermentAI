from sqlalchemy.orm import Session
from app import models


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
