from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
import enum
from app.database import Base



class RolEnum(str, enum.Enum):
    colaborador = "colaborador"
    investigador = "investigador"


class EstadoAporteEnum(str, enum.Enum):
    pendiente_revision = "pendiente_revision"
    aprobado = "aprobado"
    rechazado = "rechazado"
    correcciones_solicitadas = "correcciones_solicitadas"


class TipoNotificacionEnum(str, enum.Enum):
    aporte_aprobado = "aporte_aprobado"
    aporte_rechazado = "aporte_rechazado"
    correcciones_solicitadas = "correcciones_solicitadas"
    nuevo_aporte_pendiente = "nuevo_aporte_pendiente"
    aporte_eliminado = "aporte_eliminado"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(SAEnum(RolEnum), nullable=False, default=RolEnum.colaborador)
    created_at = Column(DateTime, default=datetime.utcnow)

    aportes = relationship("Aporte", back_populates="usuario", foreign_keys="Aporte.usuario_id")
    revisiones = relationship("Aporte", back_populates="revisor", foreign_keys="Aporte.revisado_por")
    notificaciones = relationship("Notificacion", back_populates="usuario")


class Fermentacion(Base):
    __tablename__ = "fermentaciones"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    descripcion = Column(Text)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    aportes = relationship("Aporte", back_populates="fermentacion")


class Aporte(Base):
    __tablename__ = "aportes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fermentacion_id = Column(Integer, ForeignKey("fermentaciones.id"), nullable=False)
    estado = Column(SAEnum(EstadoAporteEnum), nullable=False, default=EstadoAporteEnum.pendiente_revision)
    observaciones = Column(Text)
    fecha_subida = Column(DateTime, default=datetime.utcnow)
    fecha_revision = Column(DateTime)
    revisado_por = Column(Integer, ForeignKey("users.id"))
    ruta_minio = Column(String(500))
    descripcion = Column(Text)
    solicitud_eliminacion = Column(Boolean, default=False)
    motivo_eliminacion = Column(Text)
    eliminado = Column(Boolean, default=False)

    usuario = relationship("User", back_populates="aportes", foreign_keys=[usuario_id])
    revisor = relationship("User", back_populates="revisiones", foreign_keys=[revisado_por])
    fermentacion = relationship("Fermentacion", back_populates="aportes")
    metadatos = relationship("MetadatoImagen", back_populates="aporte", cascade="all, delete-orphan")
    notificaciones = relationship("Notificacion", back_populates="aporte")


class MetadatoImagen(Base):
    __tablename__ = "metadatos_imagenes"

    id = Column(Integer, primary_key=True, index=True)
    aporte_id = Column(Integer, ForeignKey("aportes.id"), nullable=False)
    imagen = Column(String(255), nullable=False)
    timestamp = Column(DateTime)
    tiempo_horas = Column(Float)
    glucosa_g_l = Column(Float)
    fructosa_g_l = Column(Float)
    sacarosa_g_l = Column(Float)
    etanol_g_l = Column(Float)
    acido_lactico_g_l = Column(Float)
    acido_acetico_g_l = Column(Float)
    acido_citrico_g_l = Column(Float)
    acido_succinico_g_l = Column(Float)
    acido_malico_g_l = Column(Float)
    acido_oxalico_g_l = Column(Float)
    acido_formico_g_l = Column(Float)
    intervalo_incertidumbre_min = Column(Integer)
    validado_asesor = Column(Boolean, default=False)
    observaciones = Column(Text)

    aporte = relationship("Aporte", back_populates="metadatos")


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    aporte_id = Column(Integer, ForeignKey("aportes.id"))
    tipo = Column(SAEnum(TipoNotificacionEnum), nullable=False)
    mensaje = Column(Text, nullable=False)
    leida = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("User", back_populates="notificaciones")
    aporte = relationship("Aporte", back_populates="notificaciones")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(36), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
