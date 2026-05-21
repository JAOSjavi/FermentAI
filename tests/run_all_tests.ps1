# ============================================================
# Script Maestro de Pruebas — FermentAI
# Ejecuta toda la suite de pruebas en orden y genera reportes.
#
# Uso:
#   cd c:\Users\Javier\Desktop\FermentAI
#   .\tests\run_all_tests.ps1
#
# Opciones:
#   -Solo "funcional"      # Solo ejecutar pruebas funcionales
#   -Solo "seguridad"      # Solo pruebas de seguridad
#   -SkipCarga             # Omitir pruebas de carga (Locust)
#   -SkipCompatibilidad    # Omitir pruebas multi-navegador
#   -SkipAccesibilidad     # Omitir pruebas de accesibilidad
# ============================================================

param(
    [string]$Solo = "",
    [switch]$SkipCarga,
    [switch]$SkipCompatibilidad,
    [switch]$SkipAccesibilidad,
    [int]$LocustUsers = 20,
    [int]$LocustSpawnRate = 5,
    [int]$LocustDuration = 30,
    [string]$ApiUrl = "http://localhost:8000",
    [string]$FrontendUrl = "http://localhost:3000"
)

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$reportDir = "tests\reports"
$logFile   = "$reportDir\master_log_$timestamp.txt"

# Asegurar directorio de reportes
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

$resultados = [ordered]@{}
$tiempoInicio = Get-Date

function Write-Banner($text) {
    $sep = "═" * 58
    Write-Host "`n$sep" -ForegroundColor Cyan
    Write-Host "  $text" -ForegroundColor Cyan
    Write-Host $sep -ForegroundColor Cyan
    Add-Content $logFile "`n$sep`n  $text`n$sep"
}

function Run-Suite($nombre, $marker, $paths) {
    if ($Solo -ne "" -and $Solo -ne $marker) { return }

    Write-Banner "$nombre"
    $t = Measure-Command {
        $output = python -m pytest $paths `
            -v `
            -m $marker `
            --tb=short `
            --html="$reportDir\report_${marker}_$timestamp.html" `
            --self-contained-html `
            --no-header `
            2>&1
        $output | Tee-Object -Append -FilePath $logFile
        $script:lastExitCode = $LASTEXITCODE
    }

    $estado = if ($script:lastExitCode -eq 0) { "PASS" } else { "FAIL" }
    $color  = if ($estado -eq "PASS") { "Green" } else { "Red" }
    Write-Host "`n  $nombre : [$estado] — $([math]::Round($t.TotalSeconds, 1))s" -ForegroundColor $color
    $resultados[$nombre] = @{ Estado = $estado; Tiempo = $t.TotalSeconds }
}

# ──────────────────────────────────────────────────────────────
# VERIFICAR QUE LOS SERVICIOS ESTÉN LEVANTADOS
# ──────────────────────────────────────────────────────────────
Write-Banner "VERIFICACIÓN DE SERVICIOS"
Write-Host "  API:      $ApiUrl/health" -ForegroundColor Gray
Write-Host "  Frontend: $FrontendUrl" -ForegroundColor Gray

try {
    $healthR = Invoke-WebRequest -Uri "$ApiUrl/health" -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
    Write-Host "  [OK] API Backend responde: $($healthR.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] API no disponible en $ApiUrl" -ForegroundColor Red
    Write-Host "  Ejecutar primero: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

try {
    $frontR = Invoke-WebRequest -Uri $FrontendUrl -UseBasicParsing -TimeoutSec 15 -ErrorAction Stop
    Write-Host "  [OK] Frontend responde: $($frontR.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Frontend no disponible en $FrontendUrl" -ForegroundColor Yellow
    Write-Host "  Algunas pruebas de UI serán omitidas." -ForegroundColor Yellow
}

# ──────────────────────────────────────────────────────────────
# INSTALAR DEPENDENCIAS SI FALTAN
# ──────────────────────────────────────────────────────────────
Write-Banner "INSTALACIÓN DE DEPENDENCIAS"
$pipCheck = python -m pip show pytest 2>&1
if ($pipCheck -notmatch "Version") {
    Write-Host "  Instalando dependencias de prueba..." -ForegroundColor Yellow
    python -m pip install -r tests\requirements-test.txt -q
    playwright install chromium firefox webkit 2>&1 | Out-Null
} else {
    Write-Host "  [OK] Dependencias ya instaladas." -ForegroundColor Green
}

# ──────────────────────────────────────────────────────────────
# EJECUCIÓN DE SUITES
# ──────────────────────────────────────────────────────────────

# 1. Pruebas Funcionales (siempre se ejecutan)
Run-Suite "Pruebas Funcionales" "funcional" `
    "tests/09_funcionales/test_auth.py" `
    "tests/09_funcionales/test_fermentaciones.py" `
    "tests/09_funcionales/test_aportes.py" `
    "tests/09_funcionales/test_notificaciones.py" `
    "tests/09_funcionales/test_revisar.py"

# 2. Disponibilidad
Run-Suite "Disponibilidad" "disponibilidad" "tests/04_disponibilidad/test_disponibilidad.py"

# 3. Latencia
Run-Suite "Latencia y Tiempos de Respuesta" "latencia" "tests/05_latencia/test_latencia.py"

# 4. Rendimiento
Run-Suite "Rendimiento" "rendimiento" "tests/07_rendimiento/test_rendimiento.py"

# 5. Seguridad
Run-Suite "Seguridad OWASP" "seguridad" "tests/12_seguridad/test_seguridad.py"

# 6. W3C
if (-not $SkipCompatibilidad) {
    Run-Suite "Validación W3C" "w3c" "tests/02_w3c/test_w3c_validation.py"
}

# 7. Accesibilidad
if (-not $SkipAccesibilidad) {
    Run-Suite "Accesibilidad WCAG" "accesibilidad" "tests/03_accesibilidad/test_accesibilidad.py"
}

# 8. Compatibilidad
if (-not $SkipCompatibilidad) {
    Run-Suite "Compatibilidad Multi-Navegador" "compatibilidad" "tests/11_compatibilidad/test_compatibilidad.py"
}

# 9. Conectividad (PowerShell independiente)
if ($Solo -eq "" -or $Solo -eq "conectividad") {
    Write-Banner "Conectividad y Tracert"
    $t = Measure-Command {
        .\tests\06_conectividad\tracert_checks.ps1 2>&1 | Tee-Object -Append -FilePath $logFile
        $script:lastExitCode = $LASTEXITCODE
    }
    $estado = if ($script:lastExitCode -eq 0) { "PASS" } else { "FAIL" }
    $color  = if ($estado -eq "PASS") { "Green" } else { "Yellow" }
    Write-Host "`n  Conectividad : [$estado] — $([math]::Round($t.TotalSeconds, 1))s" -ForegroundColor $color
    $resultados["Conectividad"] = @{ Estado = $estado; Tiempo = $t.TotalSeconds }
}

# 10. Análisis estático de seguridad (Bandit)
if ($Solo -eq "" -or $Solo -eq "bandit") {
    Write-Banner "Análisis Estático Bandit"
    $t = Measure-Command {
        .\tests\12_seguridad\run_bandit.ps1 2>&1 | Tee-Object -Append -FilePath $logFile
        $script:lastExitCode = $LASTEXITCODE
    }
    $estado = if ($script:lastExitCode -eq 0) { "PASS" } else { "WARN" }
    $color  = if ($estado -eq "PASS") { "Green" } else { "Yellow" }
    Write-Host "`n  Bandit : [$estado] — $([math]::Round($t.TotalSeconds, 1))s" -ForegroundColor $color
    $resultados["Bandit"] = @{ Estado = $estado; Tiempo = $t.TotalSeconds }
}

# 11. Pruebas de Carga (Locust) — requiere más tiempo
if (-not $SkipCarga -and ($Solo -eq "" -or $Solo -eq "carga")) {
    Write-Banner "Pruebas de Carga (Locust — ${LocustDuration}s)"
    $locustReport = "$reportDir\locust_report_$timestamp.html"
    $t = Measure-Command {
        locust -f tests/08_carga/locustfile.py `
            --headless `
            --users $LocustUsers `
            --spawn-rate $LocustSpawnRate `
            --run-time "${LocustDuration}s" `
            --host $ApiUrl `
            --html $locustReport `
            2>&1 | Tee-Object -Append -FilePath $logFile
        $script:lastExitCode = $LASTEXITCODE
    }
    $estado = if ($script:lastExitCode -eq 0) { "PASS" } else { "FAIL" }
    $color  = if ($estado -eq "PASS") { "Green" } else { "Red" }
    Write-Host "`n  Carga : [$estado] — $([math]::Round($t.TotalSeconds, 1))s" -ForegroundColor $color
    Write-Host "  Reporte Locust: $locustReport" -ForegroundColor Cyan
    $resultados["Carga (Locust)"] = @{ Estado = $estado; Tiempo = $t.TotalSeconds }
}

# ──────────────────────────────────────────────────────────────
# RESUMEN FINAL
# ──────────────────────────────────────────────────────────────
$tiempoTotal = (Get-Date) - $tiempoInicio
Write-Banner "RESUMEN FINAL — FermentAI Test Suite"

$pasadas  = ($resultados.Values | Where-Object { $_.Estado -eq "PASS" }).Count
$fallidas = ($resultados.Values | Where-Object { $_.Estado -eq "FAIL" }).Count
$advertencias = ($resultados.Values | Where-Object { $_.Estado -eq "WARN" }).Count
$total    = $resultados.Count

Write-Host "`n  Suite                                Estado    Tiempo" -ForegroundColor White
Write-Host "  $('─'*54)" -ForegroundColor Gray
foreach ($suite in $resultados.Keys) {
    $r = $resultados[$suite]
    $color = switch ($r.Estado) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        default { "Yellow" }
    }
    $nombre_pad = $suite.PadRight(40)
    $estado_pad = $r.Estado.PadRight(8)
    $tiempo = "$([math]::Round($r.Tiempo, 1))s"
    Write-Host "  $nombre_pad [$estado_pad] $tiempo" -ForegroundColor $color
}

Write-Host "`n  $('═'*54)" -ForegroundColor Cyan
Write-Host "  TOTAL: $total suites | $pasadas PASS | $fallidas FAIL | $advertencias WARN" -ForegroundColor $(if ($fallidas -gt 0) { "Red" } elseif ($advertencias -gt 0) { "Yellow" } else { "Green" })
Write-Host "  Tiempo total: $([math]::Round($tiempoTotal.TotalMinutes, 1)) min" -ForegroundColor White
Write-Host "  Reportes en: $reportDir" -ForegroundColor Cyan
Write-Host "  Log: $logFile`n" -ForegroundColor Cyan

# Recordatorio de pruebas manuales
Write-Host "  Pruebas manuales pendientes:" -ForegroundColor Yellow
Write-Host "    - Exploratorias: tests\01_exploratorias\checklist_exploratorio.md" -ForegroundColor Gray
Write-Host "    - Usabilidad:    tests\10_usabilidad\checklist_usabilidad.md" -ForegroundColor Gray

if ($fallidas -gt 0) { exit 1 } else { exit 0 }
