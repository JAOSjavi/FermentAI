from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas

router = APIRouter(prefix="/api/notificaciones", tags=["notificaciones"])


@router.get("/me", response_model=list[schemas.NotificacionOut])
def mis_notificaciones(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Notificacion)
        .filter(models.Notificacion.usuario_id == current_user.id)
        .order_by(models.Notificacion.created_at.desc())
        .limit(50)
        .all()
    )


@router.put("/{notif_id}/leer", response_model=schemas.NotificacionOut)
def marcar_leida(
    notif_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notif = db.query(models.Notificacion).filter(
        models.Notificacion.id == notif_id,
        models.Notificacion.usuario_id == current_user.id,
    ).first()
    if not notif:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    notif.leida = True
    db.commit()
    db.refresh(notif)
    return notif


@router.put("/me/leer-todas")
def leer_todas(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(models.Notificacion).filter(
        models.Notificacion.usuario_id == current_user.id,
        models.Notificacion.leida == False,
    ).update({"leida": True})
    db.commit()
    return {"ok": True}
