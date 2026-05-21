# Suite de Pruebas — FermentAI

Documentación completa de la infraestructura de pruebas para la plataforma FermentAI.

---

## Estructura

```
tests/
├── conftest.py                        # Fixtures compartidos (tokens, clientes HTTP)
├── requirements-test.txt              # Dependencias Python para pruebas
├── pytest.ini                         # Configuración de pytest
├── run_all_tests.ps1                  # Script maestro de ejecución
├── README_PRUEBAS.md                  # Este archivo
│
├── 01_exploratorias/
│   └── checklist_exploratorio.md      # Checklist manual de exploración
│
├── 02_w3c/
│   └── test_w3c_validation.py         # Validación HTML contra W3C Nu Validator
│
├── 03_accesibilidad/
│   └── test_accesibilidad.py          # WCAG 2.1 con Playwright + axe-core
│
├── 04_disponibilidad/
│   └── test_disponibilidad.py         # Uptime, health checks, estabilidad
│
├── 05_latencia/
│   └── test_latencia.py               # P50/P95/P99 por endpoint
│
├── 06_conectividad/
│   └── tracert_checks.ps1             # tracert, DNS, puertos, latencia HTTP
│
├── 07_rendimiento/
│   └── test_rendimiento.py            # Concurrencia, throughput, escalabilidad
│
├── 08_carga/
│   └── locustfile.py                  # Pruebas de carga con Locust
│
├── 09_funcionales/
│   ├── test_auth.py                   # Login, registro, /me
│   ├── test_fermentaciones.py         # Listado y filtros de datasets
│   ├── test_aportes.py                # Subida de ZIPs, mis aportes
│   ├── test_notificaciones.py         # Listado y marcar como leída
│   └── test_revisar.py                # Aprobar/rechazar aportes (investigador)
│
├── 10_usabilidad/
│   └── checklist_usabilidad.md        # 10 heurísticas de Nielsen
│
├── 11_compatibilidad/
│   └── test_compatibilidad.py         # Chromium, Firefox, WebKit + viewports
│
├── 12_seguridad/
│   ├── test_seguridad.py              # OWASP Top 10 básico
│   └── run_bandit.ps1                 # Análisis estático con Bandit + Safety
│
└── reports/                           # Generado automáticamente
    ├── reporte_pruebas.html
    ├── locust_report_*.html
    ├── bandit_report_*.json
    └── conectividad_report_*.txt
```

---

## Requisitos previos

### 1. Servicios levantados
```powershell
docker-compose up -d
```
Esperar ~30 segundos a que todos los contenedores estén saludables.

### 2. Instalar dependencias de prueba
```powershell
cd c:\Users\Javier\Desktop\FermentAI
pip install -r tests\requirements-test.txt
playwright install     # instala chromium, firefox, webkit
```

---

## Ejecución

### Todas las pruebas automáticas
```powershell
.\tests\run_all_tests.ps1
```

### Solo una categoría
```powershell
.\tests\run_all_tests.ps1 -Solo funcional
.\tests\run_all_tests.ps1 -Solo seguridad
.\tests\run_all_tests.ps1 -Solo latencia
```

### Omitir suites lentas
```powershell
# Sin carga ni compatibilidad multi-browser
.\tests\run_all_tests.ps1 -SkipCarga -SkipCompatibilidad
```

### Por separado con pytest
```powershell
# Funcionales
pytest tests/09_funcionales/ -v -m funcional

# Disponibilidad
pytest tests/04_disponibilidad/ -v -m disponibilidad -s

# Latencia (con output)
pytest tests/05_latencia/ -v -m latencia -s

# Seguridad
pytest tests/12_seguridad/test_seguridad.py -v -m seguridad

# W3C
pytest tests/02_w3c/ -v -m w3c

# Accesibilidad
pytest tests/03_accesibilidad/ -v -m accesibilidad

# Compatibilidad
pytest tests/11_compatibilidad/ -v -m compatibilidad

# Rendimiento
pytest tests/07_rendimiento/ -v -m rendimiento -s
```

### Prueba de carga (Locust)
```powershell
# Modo headless (50 usuarios, 30 segundos)
locust -f tests/08_carga/locustfile.py `
    --headless --users 50 --spawn-rate 5 --run-time 30s `
    --host http://localhost:8000 `
    --html tests/reports/locust_report.html

# Modo UI web (abrir http://localhost:8089)
locust -f tests/08_carga/locustfile.py --host http://localhost:8000
```

### Conectividad y tracert
```powershell
.\tests\06_conectividad\tracert_checks.ps1
```

### Análisis de seguridad estático
```powershell
.\tests\12_seguridad\run_bandit.ps1
```

### Pruebas manuales
Completar con papel/lápiz o en la aplicación:
- [01_exploratorias/checklist_exploratorio.md](01_exploratorias/checklist_exploratorio.md)
- [10_usabilidad/checklist_usabilidad.md](10_usabilidad/checklist_usabilidad.md)

---

## Métricas SLA objetivo

| Métrica | Objetivo |
|---------|----------|
| Disponibilidad | ≥ 99% |
| Health check P95 | < 500 ms |
| API endpoints P50 | < 200 ms |
| API endpoints P95 | < 500 ms |
| API endpoints P99 | < 1000 ms |
| Tasa de error (carga) | ≤ 1% |
| P95 bajo carga (50 usuarios) | < 2000 ms |
| Violaciones WCAG críticas | 0 |
| Errores W3C críticos | 0 |
| Vulnerabilidades OWASP críticas | 0 |

---

## Variables de entorno

| Variable | Valor por defecto |
|----------|------------------|
| `FERMENTAI_API_URL` | `http://localhost:8000` |
| `FERMENTAI_FRONTEND_URL` | `http://localhost:3000` |

---

## Tipos de prueba y cobertura

| # | Tipo | Herramienta | Automatizada |
|---|------|-------------|--------------|
| 01 | Exploratorias | Checklist manual | No |
| 02 | Validación W3C | Nu HTML Validator API | Sí |
| 03 | Accesibilidad WCAG 2.1 | Playwright + axe-core | Sí |
| 04 | Disponibilidad / Uptime | httpx | Sí |
| 05 | Latencia / Tiempos de respuesta | httpx + statistics | Sí |
| 06 | Conectividad (tracert, DNS) | PowerShell nativo | Sí |
| 07 | Rendimiento (concurrencia) | threading + httpx | Sí |
| 08 | Carga (usuarios concurrentes) | Locust | Sí |
| 09 | Funcionales (API REST) | pytest + httpx | Sí |
| 10 | Usabilidad (Nielsen) | Checklist manual | No |
| 11 | Compatibilidad multi-browser | Playwright | Sí |
| 12 | Seguridad OWASP básica | pytest + Bandit + Safety | Sí |
