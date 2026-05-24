from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from app.models import RolEnum, EstadoAporteEnum, EstadoFermentacionEnum, TipoNotificacionEnum


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    nombre: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    nombre: str
    email: str
    rol: RolEnum
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Fermentaciones ─────────────────────────────────────────────────────────────

class FermentacionOut(BaseModel):
    id: int
    codigo: str
    descripcion: Optional[str]
    fecha_inicio: Optional[datetime]
    fecha_fin: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Metadatos ──────────────────────────────────────────────────────────────────

class MetadatoImagenOut(BaseModel):
    id: int
    aporte_id: int
    imagen: str
    timestamp: Optional[datetime]
    tiempo_horas: Optional[float]
    glucosa_g_l: Optional[float]
    fructosa_g_l: Optional[float]
    sacarosa_g_l: Optional[float]
    etanol_g_l: Optional[float]
    acido_lactico_g_l: Optional[float]
    acido_acetico_g_l: Optional[float]
    acido_citrico_g_l: Optional[float]
    acido_succinico_g_l: Optional[float]
    acido_malico_g_l: Optional[float]
    acido_oxalico_g_l: Optional[float]
    acido_formico_g_l: Optional[float]
    estado_fermentacion: Optional[EstadoFermentacionEnum]
    intervalo_incertidumbre_min: Optional[int]
    validado_asesor: bool
    observaciones: Optional[str]
    url_imagen: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Aportes ────────────────────────────────────────────────────────────────────

class AporteOut(BaseModel):
    id: int
    usuario_id: int
    fermentacion_id: int
    estado: EstadoAporteEnum
    observaciones: Optional[str]
    fecha_subida: datetime
    fecha_revision: Optional[datetime]
    revisado_por: Optional[int]
    ruta_minio: Optional[str]
    fermentacion: Optional[FermentacionOut] = None
    usuario: Optional[UserOut] = None

    model_config = {"from_attributes": True}


class AporteDetalle(AporteOut):
    metadatos: List[MetadatoImagenOut] = []


class RevisionRequest(BaseModel):
    observaciones: str


# ── Notificaciones ─────────────────────────────────────────────────────────────

class NotificacionOut(BaseModel):
    id: int
    usuario_id: int
    aporte_id: Optional[int]
    tipo: TipoNotificacionEnum
    mensaje: str
    leida: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Reset de contraseña ────────────────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    nueva_password: str


# ── Ajustes de cuenta ─────────────────────────────────────────────────────────

class CambiarEmailRequest(BaseModel):
    nuevo_email: EmailStr
    password_actual: str


class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nuevo: str
    password_nuevo_confirm: str


# ── Dataset público ────────────────────────────────────────────────────────────

class DatasetImagenOut(BaseModel):
    nombre: str
    url: str
    metadatos: Optional[MetadatoImagenOut] = None


class DatasetAporteOut(BaseModel):
    id: int
    fermentacion: FermentacionOut
    imagenes: List[DatasetImagenOut] = []
    total_imagenes: int

    model_config = {"from_attributes": True}
