# FermentAI — Data Lake de Fermentación de Café

Plataforma web científica para la gestión colaborativa de datasets de imágenes de fermentación de café correlacionadas con datos fisicoquímicos HPLC.

## Stack

| Capa | Tecnología |
|---|---|
| Backend | FastAPI 0.115 · Python 3.11 · SQLAlchemy 2 |
| Base de datos | PostgreSQL 15 |
| Almacenamiento | MinIO (S3-compatible) |
| Frontend | Next.js 14 · TypeScript · TailwindCSS · shadcn/ui |
| Email | Resend HTTP API |
| Contenedores | Docker · Docker Compose |

## Inicio rápido (desarrollo local)

### Prerrequisitos
- Docker y Docker Compose
- Node.js 20+ (solo para desarrollo frontend sin Docker)
- Python 3.11+ (solo para desarrollo backend sin Docker)

### Con Docker Compose

```bash
cd FermentAI

# Copiar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env con tus claves (RESEND_API_KEY, etc.)

# Levantar todos los servicios
docker compose up --build
```

Servicios disponibles:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Docs API (Swagger)**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin / minioadmin123)

### Sin Docker (desarrollo)

**Backend:**
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Editar .env con credenciales locales

uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Usuarios pre-creados

Al iniciar el backend por primera vez se crean automáticamente:

| Nombre | Email | Contraseña | Rol |
|---|---|---|---|
| Jesús David Coral | jesus.coral@ucc.edu.co | investigador123 | Investigador |
| Daniel Fernando Arteaga | daniel.arteaga@ucc.edu.co | investigador123 | Investigador |

Los demás usuarios se registran públicamente como **Colaboradores**.

## Estructura del ZIP requerida

```
FERM01/
├── imagenes/
│   ├── imagen_001.jpg
│   └── imagen_002.jpg
└── FERM01_metadata.csv
```

**Requisitos del CSV — 14 columnas:**

| Columna | Tipo |
|---|---|
| tiempo_horas | numérico |
| glucosa_g_l | numérico |
| fructosa_g_l | numérico |
| sacarosa_g_l | numérico |
| etanol_g_l | numérico |
| acido_lactico_g_l | numérico |
| acido_acetico_g_l | numérico |
| acido_citrico_g_l | numérico |
| acido_succinico_g_l | numérico |
| acido_malico_g_l | numérico |
| acido_oxalico_g_l | numérico |
| acido_formico_g_l | numérico |
| validado_asesor | texto (Sí/No) |
| observaciones | texto |

**Límites:** imágenes mínimo 1280×720 px · solo `.jpg`/`.jpeg` · ZIP ≤ 2 GB · máx. 5 subidas por hora

## Pipeline de depuración de imágenes

Al subir un aporte, el backend ejecuta automáticamente:

1. **Validación CSV** — verifica las 14 columnas y que los valores numéricos sean válidos
2. **Estructura ZIP** — carpeta `FERM##/imagenes/` + `FERM##_metadata.csv`
3. **Magic bytes JPEG** — descarta archivos que no sean JPEG reales (`FF D8 FF`)
4. **Resolución mínima** — descarta imágenes menores a 1280×720 px
5. **Redimensionado** — escala a 1280×720 con LANCZOS + recorte centrado
6. **Normalización CLAHE** — mejora contraste (clipLimit=2.0, tileGridSize=8×8)

Las imágenes procesadas se guardan en MinIO bajo `processed/{aporte_id}/`.

## Tests

```bash
cd backend
pytest -v
```

## Deployment en Railway

Crea 4 servicios en Railway:

1. **PostgreSQL** — servicio managed de Railway
2. **MinIO** — custom service con imagen `minio/minio`, volumen persistente 50 GB
3. **Backend** — conecta el repositorio, usa `backend/Dockerfile`
4. **Frontend** — conecta el repositorio, detecta Next.js automáticamente

**Variables de entorno en Backend:**
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=<genera una clave segura>
MINIO_ENDPOINT=${{MinIO.RAILWAY_PRIVATE_DOMAIN}}:9000
MINIO_PUBLIC_ENDPOINT=<dominio-publico-minio>.railway.app
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=<contraseña segura>
MINIO_BUCKET=fermentai-datasets
MINIO_SECURE=false
BACKEND_CORS_ORIGINS=https://<tu-frontend>.railway.app
RESEND_API_KEY=<tu-clave-resend>
SMTP_FROM=onboarding@resend.dev
FRONTEND_URL=https://<tu-frontend>.railway.app
```

**Variables de entorno en Frontend:**
```
NEXT_PUBLIC_API_URL=https://<tu-backend>.railway.app
```

> **Nota:** Railway bloquea el puerto 587 (SMTP). El sistema usa la API HTTP de Resend para el envío de emails.

## API Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/auth/register` | Registro de colaborador |
| POST | `/api/auth/login` | Login → JWT |
| GET | `/api/auth/me` | Perfil actual |
| POST | `/api/auth/forgot-password` | Solicitar recuperación de contraseña |
| POST | `/api/auth/reset-password` | Restablecer contraseña con token |
| POST | `/api/aportes/subir` | Subir ZIP (ejecuta pipeline) |
| GET | `/api/aportes/me` | Mis aportes |
| GET | `/api/aportes/{id}` | Detalle de un aporte |
| GET | `/api/aportes/{id}/descargar-dataset` | Descargar dataset aprobado |
| PUT | `/api/aportes/{id}/descripcion` | Editar descripción |
| POST | `/api/aportes/{id}/solicitar-eliminacion` | Solicitar eliminación (colaborador) |
| POST | `/api/aportes/{id}/eliminar` | Eliminar aporte (investigador) |
| GET | `/api/revisar/pendientes` | Aportes pendientes (investigador) |
| PUT | `/api/revisar/{id}/aprobar` | Aprobar aporte |
| PUT | `/api/revisar/{id}/rechazar` | Rechazar con observaciones |
| PUT | `/api/revisar/{id}/solicitar-correcciones` | Solicitar correcciones |
| GET | `/api/fermentaciones` | Datasets aprobados |
| GET | `/api/notificaciones/me` | Mis notificaciones |
| PUT | `/api/ajustes/cambiar-email` | Cambiar email |
| PUT | `/api/ajustes/cambiar-password` | Cambiar contraseña |
