# FermentAI — Pruebas de Carga JMeter

## Configuración global

| Parámetro | Valor |
|---|---|
| Base URL | `http://localhost:8000` |
| Content-Type (JSON) | `application/json` |
| Authorization | `Bearer ${token}` |

---

## Variables de usuario (User Defined Variables)

| Nombre | Valor por defecto |
|---|---|
| `host` | `localhost` |
| `port` | `8000` |
| `token_colaborador` | *(se llena con el extractor de la petición login)* |
| `token_investigador` | *(se llena con el extractor de la petición login)* |
| `aporte_id` | `1` |
| `notif_id` | `1` |

---

## 1. Health Check

| Campo | Valor |
|---|---|
| Método | `GET` |
| Path | `/health` |
| Auth | No |
| Body | — |

**Respuesta esperada:**
```json
{ "status": "ok" }
```

---

## 2. Auth — Registro de usuario

| Campo | Valor |
|---|---|
| Método | `POST` |
| Path | `/api/auth/register` |
| Content-Type | `application/json` |
| Auth | No |

**Body:**
```json
{
  "nombre": "Usuario Prueba ${__threadNum}",
  "email": "usuario_prueba_${__threadNum}@test.com",
  "password": "password123"
}
```

> Usar `${__threadNum}` para generar emails únicos por hilo y evitar el error 400 de email duplicado.

**Respuesta esperada (201):**
```json
{
  "id": 10,
  "nombre": "Usuario Prueba 1",
  "email": "usuario_prueba_1@test.com",
  "rol": "colaborador",
  "created_at": "2026-05-14T10:00:00"
}
```

---

## 3. Auth — Login colaborador

| Campo | Valor |
|---|---|
| Método | `POST` |
| Path | `/api/auth/login` |
| Content-Type | `application/json` |
| Auth | No |

**Body:**
```json
{
  "email": "usuario_prueba_1@test.com",
  "password": "password123"
}
```

**Extractor JSON — guardar token:**
- Variable: `token_colaborador`
- JSON Path: `$.access_token`

**Respuesta esperada (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 4. Auth — Login investigador

| Campo | Valor |
|---|---|
| Método | `POST` |
| Path | `/api/auth/login` |
| Content-Type | `application/json` |
| Auth | No |

**Body:**
```json
{
  "email": "jesus.coral@ucc.edu.co",
  "password": "investigador123"
}
```

**Extractor JSON — guardar token:**
- Variable: `token_investigador`
- JSON Path: `$.access_token`

---

## 5. Auth — Perfil propio

| Campo | Valor |
|---|---|
| Método | `GET` |
| Path | `/api/auth/me` |
| Header | `Authorization: Bearer ${token_colaborador}` |
| Body | — |

**Respuesta esperada (200):**
```json
{
  "id": 3,
  "nombre": "Usuario Prueba 1",
  "email": "usuario_prueba_1@test.com",
  "rol": "colaborador",
  "created_at": "2026-05-14T10:00:00"
}
```

---

## 6. Aportes — Subir dataset (multipart/form-data)

| Campo | Valor |
|---|---|
| Método | `POST` |
| Path | `/api/aportes/subir` |
| Content-Type | `multipart/form-data` |
| Header | `Authorization: Bearer ${token_colaborador}` |

**Configuración en JMeter (HTTP Request — Files Upload):**

| Nombre del parámetro | Ruta del archivo | MIME Type |
|---|---|---|
| `file` | `/ruta/local/FERM01.zip` | `application/zip` |

> El ZIP debe seguir la estructura: `FERM##/imagenes/*.jpg` + `FERM##/FERM##_metadata.csv`

**Respuesta esperada (201):**
```json
{
  "id": 1,
  "usuario_id": 3,
  "fermentacion_id": 1,
  "estado": "pendiente_revision",
  "observaciones": null,
  "fecha_subida": "2026-05-14T10:00:00",
  "fecha_revision": null,
  "revisado_por": null,
  "ruta_minio": "pending/1/FERM01/imagenes"
}
```

**Error posible (429):**
```json
{ "detail": "Límite de 5 subidas por hora alcanzado" }
```

---

## 7. Aportes — Mis aportes

| Campo | Valor |
|---|---|
| Método | `GET` |
| Path | `/api/aportes/me` |
| Header | `Authorization: Bearer ${token_colaborador}` |
| Body | — |

**Respuesta esperada (200):** Array de objetos `AporteOut`.

---

## 8. Aportes — Detalle de un aporte

| Campo | Valor |
|---|---|
| Método | `GET` |
| Path | `/api/aportes/${aporte_id}` |
| Header | `Authorization: Bearer ${token_colaborador}` |
| Body | — |

**Respuesta esperada (200):**
```json
{
  "id": 1,
  "usuario_id": 3,
  "fermentacion_id": 1,
  "estado": "pendiente_revision",
  "metadatos": [
    {
      "id": 1,
      "imagen": "IMG_001.jpg",
      "tiempo_horas": 0.0,
      "glucosa_g_l": 45.3,
      "etanol_g_l": 0.0,
      "estado_fermentacion": "inicio",
      "url_imagen": "http://localhost:9000/..."
    }
  ]
}
```

---

## 9. Revisar — Listar pendientes (investigador)

| Campo | Valor |
|---|---|
| Método | `GET` |
| Path | `/api/revisar/pendientes` |
| Header | `Authorization: Bearer ${token_investigador}` |
| Body | — |

**Respuesta esperada (200):** Array de `AporteOut` con estado `pendiente_revision`.

---

## 10. Revisar — Detalle para revisión (investigador)

| Campo | Valor |
|---|---|
| Método | `GET` |
| Path | `/api/revisar/${aporte_id}/revisar` |
| Header | `Authorization: Bearer ${token_investigador}` |
| Body | — |

**Respuesta esperada (200):** `AporteDetalle` con metadatos y URLs de imágenes.

---

## 11. Revisar — Aprobar aporte (investigador)

| Campo | Valor |
|---|---|
| Método | `PUT` |
| Path | `/api/revisar/${aporte_id}/aprobar` |
| Content-Type | `application/json` |
| Header | `Authorization: Bearer ${token_investigador}` |
| Body | — (sin body) |

**Respuesta esperada (200):**
```json
{
  "id": 1,
  "estado": "aprobado",
  "ruta_minio": "approved/1/FERM01/imagenes"
}
```

---

## 12. Revisar — Rechazar aporte (investigador)

| Campo | Valor |
|---|---|
| Método | `PUT` |
| Path | `/api/revisar/${aporte_id}/rechazar` |
| Content-Type | `application/json` |
| Header | `Authorization: Bearer ${token_investigador}` |

**Body:**
```json
{
  "observaciones": "El archivo CSV tiene columnas faltantes."
}
```

**Respuesta esperada (200):**
```json
{
  "id": 1,
  "estado": "rechazado",
  "observaciones": "El archivo CSV tiene columnas faltantes."
}
```

---

## 13. Revisar — Solicitar correcciones (investigador)

| Campo | Valor |
|---|---|
| Método | `PUT` |
| Path | `/api/revisar/${aporte_id}/solicitar-correcciones` |
| Content-Type | `application/json` |
| Header | `Authorization: Bearer ${token_investigador}` |

**Body:**
```json
{
  "observaciones": "Faltan imágenes correspondientes a las horas 24 y 48."
}
```

**Respuesta esperada (200):**
```json
{
  "id": 1,
  "estado": "correcciones_solicitadas",
  "observaciones": "Faltan imágenes correspondientes a las horas 24 y 48."
}
```

---

## 14. Fermentaciones — Listar datasets aprobados

| Campo | Valor |
|---|---|
| Método | `GET` |
| Path | `/api/fermentaciones` |
| Header | `Authorization: Bearer ${token_colaborador}` |
| Body | — |

**Query params opcionales:**

| Parámetro | Ejemplo |
|---|---|
| `codigo` | `FERM01` |
| `estado_fermentacion` | `inicio` / `medio` / `final` |
| `fecha_desde` | `2026-01-01T00:00:00` |
| `fecha_hasta` | `2026-12-31T23:59:59` |

**Path con filtros:**
```
/api/fermentaciones?codigo=FERM01&estado_fermentacion=inicio
```

**Respuesta esperada (200):**
```json
[
  {
    "id": 1,
    "fermentacion": { "id": 1, "codigo": "FERM01" },
    "imagenes": [...],
    "total_imagenes": 12
  }
]
```

---

## 15. Notificaciones — Mis notificaciones

| Campo | Valor |
|---|---|
| Método | `GET` |
| Path | `/api/notificaciones/me` |
| Header | `Authorization: Bearer ${token_colaborador}` |
| Body | — |

**Respuesta esperada (200):**
```json
[
  {
    "id": 1,
    "usuario_id": 3,
    "aporte_id": 1,
    "tipo": "aporte_aprobado",
    "mensaje": "Tu aporte #1 ha sido aprobado.",
    "leida": false,
    "created_at": "2026-05-14T10:05:00"
  }
]
```

---

## 16. Notificaciones — Marcar como leída

| Campo | Valor |
|---|---|
| Método | `PUT` |
| Path | `/api/notificaciones/${notif_id}/leer` |
| Content-Type | `application/json` |
| Header | `Authorization: Bearer ${token_colaborador}` |
| Body | — (sin body) |

**Respuesta esperada (200):** El objeto `NotificacionOut` con `leida: true`.

---

## 17. Notificaciones — Marcar todas como leídas

| Campo | Valor |
|---|---|
| Método | `PUT` |
| Path | `/api/notificaciones/me/leer-todas` |
| Header | `Authorization: Bearer ${token_colaborador}` |
| Body | — (sin body) |

**Respuesta esperada (200):**
```json
{ "ok": true }
```

---

## Escenarios de prueba recomendados

### Escenario 1 — Carga básica (endpoints de lectura)
- Hilos: 50 usuarios
- Ramp-up: 30 s
- Loop count: 10
- Endpoints: `GET /health`, `GET /api/auth/me`, `GET /api/aportes/me`, `GET /api/fermentaciones`, `GET /api/notificaciones/me`

### Escenario 2 — Flujo completo colaborador
1. `POST /api/auth/login` → extraer token
2. `GET /api/auth/me`
3. `POST /api/aportes/subir` (con ZIP)
4. `GET /api/aportes/me`
5. `GET /api/notificaciones/me`

### Escenario 3 — Flujo completo investigador
1. `POST /api/auth/login` (investigador) → extraer token
2. `GET /api/revisar/pendientes`
3. `GET /api/revisar/${aporte_id}/revisar`
4. `PUT /api/revisar/${aporte_id}/aprobar`

### Escenario 4 — Rate limit (subida de aportes)
- Hilos: 1 usuario
- Loop count: 6
- Verificar que el request 6 retorna **HTTP 429**

---

## Orden de ejecución recomendado en el Test Plan

```
Thread Group
├── HTTP Request Defaults (host, port)
├── User Defined Variables
├── [SETUP] POST /api/auth/register   ← crear usuario de prueba
├── [SETUP] POST /api/auth/login      ← extraer token_colaborador
├── [SETUP] POST /api/auth/login      ← extraer token_investigador
│
├── GET  /health
├── GET  /api/auth/me
├── POST /api/aportes/subir
├── GET  /api/aportes/me
├── GET  /api/aportes/${aporte_id}
├── GET  /api/revisar/pendientes
├── GET  /api/revisar/${aporte_id}/revisar
├── PUT  /api/revisar/${aporte_id}/aprobar
├── PUT  /api/revisar/${aporte_id}/rechazar
├── PUT  /api/revisar/${aporte_id}/solicitar-correcciones
├── GET  /api/fermentaciones
├── GET  /api/notificaciones/me
├── PUT  /api/notificaciones/${notif_id}/leer
└── PUT  /api/notificaciones/me/leer-todas
```
