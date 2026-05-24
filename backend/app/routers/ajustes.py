from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.auth import verify_password, hash_password
from app.dependencies import get_current_user
from app.schemas import CambiarEmailRequest, CambiarPasswordRequest

router = APIRouter(prefix="/api/ajustes", tags=["ajustes"])


@router.put("/cambiar-email")
def cambiar_email(
    req: CambiarEmailRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(req.password_actual, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")

    if req.nuevo_email == current_user.email:
        raise HTTPException(status_code=400, detail="El nuevo email es igual al actual")

    existing = db.query(models.User).filter(models.User.email == req.nuevo_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está en uso")

    current_user.email = req.nuevo_email
    db.commit()

    return {"message": "Email actualizado exitosamente"}


@router.put("/cambiar-password")
def cambiar_password(
    req: CambiarPasswordRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(req.password_actual, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")

    if req.password_nuevo != req.password_nuevo_confirm:
        raise HTTPException(status_code=400, detail="Las contraseñas nuevas no coinciden")

    if len(req.password_nuevo) < 8:
        raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 8 caracteres")

    current_user.password_hash = hash_password(req.password_nuevo)
    db.commit()

    return {"message": "Contraseña actualizada exitosamente"}
