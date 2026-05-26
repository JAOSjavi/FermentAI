import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.config import settings
from app.database import engine, Base, SessionLocal
from app import models
from app.auth import hash_password
from app.routers import auth, aportes, revisar, fermentaciones, notificaciones, reset_password, ajustes
from app import minio_client

logger = logging.getLogger(__name__)

app = FastAPI(title="FermentAI API", version="1.0.0")

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})

_cors_set = {o.strip().strip('"\'') for o in settings.BACKEND_CORS_ORIGINS.split(",") if o.strip()}
if settings.FRONTEND_URL:
    _cors_set.add(settings.FRONTEND_URL.strip().strip('"\'').rstrip("/"))
origins = list(_cors_set)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(aportes.router)
app.include_router(revisar.router)
app.include_router(fermentaciones.router)
app.include_router(notificaciones.router)
app.include_router(reset_password.router)
app.include_router(ajustes.router)


def _migrate_metadatos_imagenes():
    """Migración idempotente: timestamp→ferm_fecha_hora, elimina tiempo_horas."""
    with engine.begin() as conn:
        conn.execute(text("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='metadatos_imagenes' AND column_name='timestamp'
                ) AND NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='metadatos_imagenes' AND column_name='ferm_fecha_hora'
                ) THEN
                    ALTER TABLE metadatos_imagenes RENAME COLUMN "timestamp" TO ferm_fecha_hora;
                END IF;

                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='metadatos_imagenes' AND column_name='tiempo_horas'
                ) THEN
                    ALTER TABLE metadatos_imagenes DROP COLUMN tiempo_horas;
                END IF;
            END $$;
        """))


@app.on_event("startup")
def startup():
    # Esperar a que PostgreSQL esté listo (hasta 30 s)
    for attempt in range(15):
        try:
            with engine.connect():
                break
        except OperationalError:
            logger.warning(f"PostgreSQL no disponible, reintento {attempt + 1}/15...")
            time.sleep(2)
    else:
        raise RuntimeError("No se pudo conectar a PostgreSQL tras 30 segundos")

    Base.metadata.create_all(bind=engine)
    _migrate_metadatos_imagenes()
    minio_client.ensure_bucket()

    db = SessionLocal()
    try:
        investigators = [
            {"nombre": "Jesús David Coral", "email": "jesus.coral@ucc.edu.co", "password": "investigador123"},
            {"nombre": "Daniel Fernando Arteaga", "email": "daniel.arteaga@ucc.edu.co", "password": "investigador123"},
        ]
        for inv in investigators:
            if not db.query(models.User).filter(models.User.email == inv["email"]).first():
                db.add(models.User(
                    nombre=inv["nombre"],
                    email=inv["email"],
                    password_hash=hash_password(inv["password"]),
                    rol=models.RolEnum.investigador,
                ))
        db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}
