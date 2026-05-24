import uuid
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.auth import hash_password
from app.config import settings
from app.schemas import ForgotPasswordRequest, ResetPasswordRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _send_reset_email(to_email: str, nombre: str, reset_url: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Recupera tu contraseña — FermentAI"
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email

        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head><meta charset="UTF-8"></head>
        <body style="margin:0;padding:0;background:#f8fafc;font-family:sans-serif;">
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;padding:40px 0;">
            <tr><td align="center">
              <table width="480" cellpadding="0" cellspacing="0"
                     style="background:#fff;border-radius:16px;border:1px solid #e2e8f0;overflow:hidden;">
                <tr>
                  <td style="background:linear-gradient(135deg,#7c3aed,#4f46e5);padding:32px;text-align:center;">
                    <span style="font-size:28px;font-weight:800;color:#fff;letter-spacing:-0.5px;">FermentAI</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:36px 40px 24px;">
                    <p style="color:#0f172a;font-size:16px;font-weight:600;margin:0 0 8px;">Hola, {nombre}</p>
                    <p style="color:#475569;font-size:15px;line-height:1.6;margin:0 0 28px;">
                      Recibimos una solicitud para restablecer la contraseña de tu cuenta en FermentAI.
                      El enlace es válido durante <strong>1 hora</strong>.
                    </p>
                    <div style="text-align:center;margin-bottom:28px;">
                      <a href="{reset_url}"
                         style="display:inline-block;background:linear-gradient(135deg,#7c3aed,#4f46e5);
                                color:#fff;font-size:15px;font-weight:700;text-decoration:none;
                                padding:14px 32px;border-radius:10px;
                                box-shadow:0 4px 14px rgba(124,58,237,0.35);">
                        Restablecer contraseña
                      </a>
                    </div>
                    <p style="color:#94a3b8;font-size:13px;line-height:1.5;margin:0;">
                      Si no solicitaste este cambio, puedes ignorar este correo. Tu contraseña no cambiará.
                    </p>
                  </td>
                </tr>
                <tr>
                  <td style="padding:16px 40px 24px;border-top:1px solid #f1f5f9;text-align:center;">
                    <p style="color:#cbd5e1;font-size:12px;margin:0;">FermentAI · Universidad Cooperativa de Colombia</p>
                  </td>
                </tr>
              </table>
            </td></tr>
          </table>
        </body>
        </html>
        """
        msg.attach(MIMEText(html, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())
        return True
    except Exception:
        return False


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user:
        return {"message": "Si el correo existe, recibirás un enlace de recuperación.", "email_sent": True}

    token_str = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=1)

    reset_token = models.PasswordResetToken(
        user_id=user.id,
        token=token_str,
        expires_at=expires_at,
    )
    db.add(reset_token)
    db.commit()

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token_str}"
    email_sent = _send_reset_email(user.email, user.nombre, reset_url)

    return {
        "message": "Si el correo existe, recibirás un enlace de recuperación.",
        "email_sent": email_sent,
    }


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_obj = (
        db.query(models.PasswordResetToken)
        .filter(
            models.PasswordResetToken.token == req.token,
            models.PasswordResetToken.used == False,  # noqa: E712
            models.PasswordResetToken.expires_at > datetime.utcnow(),
        )
        .first()
    )

    if not token_obj:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    user = db.query(models.User).filter(models.User.id == token_obj.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    user.password_hash = hash_password(req.nueva_password)
    token_obj.used = True
    db.commit()

    return {"message": "Contraseña actualizada exitosamente"}
