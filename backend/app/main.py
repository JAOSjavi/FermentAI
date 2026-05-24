import time
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from app.config import settings
from app.database import engine, Base, SessionLocal
from app import models
from app.auth import hash_password
from app.routers import auth, aportes, revisar, fermentaciones, notificaciones, reset_password, ajustes

logger = logging.getLogger(__name__)

app = FastAPI(title="FermentAI API", version="1.0.0")

origins = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",")]
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

    db = SessionLocal()
    try:
        investigators = [
            {"nombre": "Jesús David Coral", "email": "jesus.coral@ucc.edu.co", "password": "investigador123"},
            {"nombre": "Daniel Fernando Coral", "email": "daniel.coral@ucc.edu.co", "password": "investigador123"},
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
