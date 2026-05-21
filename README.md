# FermentAI — Data Lake de Fermentación de Café

Plataforma web para la gestión de datasets científicos de imágenes de fermentación de café correlacionadas con datos fisicoquímicos HPLC.

## Stack

| Capa | Tecnología |
|---|---|
| Backend | FastAPI 0.115 · Python 3.11 · SQLAlchemy 2 · Alembic |
| Base de datos | PostgreSQL 15 |
| Almacenamiento | MinIO (S3-compatible) |
| Frontend | Next.js 14 · TypeScript · TailwindCSS · shadcn/ui |
| Contenedores | Docker · Docker Compose |

## Inicio rápido (desarrollo local)

### Prerrequisitos
- Docker y Docker Compose
- Node.js 20+ (solo para desarrollo frontend sin Docker)
- Python 3.11+ (solo para desarrollo backend sin Docker)

### Con Docker Compose

```bash
# Clonar y entrar al proyecto
cd FermentAI

# Copiar variables de entorno
cp backend/.env.example backend/.env

# Levantar todos los servicios
docker compose up --build

# La primera vez tarda ~3-5 min (descarga imágenes + build)
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
# Editar .env con tus credenciales locales de PostgreSQL y MinIO

uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
cp src/app/.env.local.example .env.local
# Editar NEXT_PUBLIC_API_URL si el backend no está en localhost:8000

npm run dev
```

## Usuarios pre-creados

Al iniciar el backend por primera vez se crean automáticamente:

| Nombre | Email | Contraseña | Rol |
|---|---|---|---|
| Jesús David Coral | jesus.coral@ucc.edu.co | investigador123 | Investigador |
| Daniel Fernando Coral | daniel.coral@ucc.edu.co | investigador123 | Investigador |

Los demás usuarios se registran públicamente como **Colaboradores**.

## Estructura del ZIP requerida

```
FERM01/
├── imagenes/
│   ├── FERM01_20240101_120000.jpg
│   └── FERM01_20240101_130000.jpg
└── FERM01_metadata.csv
```

El CSV debe tener **18 columnas**: `imagen`, `timestamp`, `tiempo_horas`, `glucosa_g_l`, `fructosa_g_l`, `sacarosa_g_l`, `etanol_g_l`, `acido_lactico_g_l`, `acido_acetico_g_l`, `acido_citrico_g_l`, `acido_succinico_g_l`, `acido_malico_g_l`, `acido_oxalico_g_l`, `acido_formico_g_l`, `estado_fermentacion`, `intervalo_incertidumbre_min`, `validado_asesor`, `observaciones`.

**Límites:** imágenes ≤ 20 MB · ZIP ≤ 2 GB · Solo `.jpg`/`.jpeg`

## Tests

```bash
cd backend
pytest -v
```

## Deployment en Railway

Crea 4 servicios en Railway:

1. **PostgreSQL** — servicio managed de Railway
2. **MinIO** — custom service con imagen `minio/minio`, volumen persistente 50 GB
3. **Backend** — conecta el repositorio, detecta `backend/Dockerfile` automáticamente
4. **Frontend** — conecta el repositorio, detecta Next.js automáticamente

**Variables de entorno en Backend:**
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=<genera una clave segura>
MINIO_ENDPOINT=${{MinIO.RAILWAY_PRIVATE_DOMAIN}}:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=<contraseña segura>
MINIO_BUCKET=fermentai-datasets
MINIO_SECURE=false
BACKEND_CORS_ORIGINS=https://<tu-frontend>.railway.app
```

**Variables de entorno en Frontend:**
```
NEXT_PUBLIC_API_URL=https://<tu-backend>.railway.app
```

## API Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/auth/register` | Registro de colaborador |
| POST | `/api/auth/login` | Login → JWT |
| GET | `/api/auth/me` | Perfil actual |
| POST | `/api/aportes/subir` | Subir ZIP |
| GET | `/api/aportes/me` | Mis aportes |
| GET | `/api/aportes/{id}` | Detalle aporte |
| GET | `/api/aportes/pendientes` | Pendientes (investigador) |
| PUT | `/api/aportes/{id}/aprobar` | Aprobar (investigador) |
| PUT | `/api/aportes/{id}/rechazar` | Rechazar con observaciones |
| PUT | `/api/aportes/{id}/solicitar-correcciones` | Solicitar correcciones |
| GET | `/api/fermentaciones` | Datasets aprobados con filtros |
| GET | `/api/notificaciones/me` | Mis notificaciones |
