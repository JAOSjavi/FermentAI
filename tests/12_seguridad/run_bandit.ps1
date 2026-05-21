# ============================================================
# Análisis Estático de Seguridad — FermentAI
# Usa bandit para detectar vulnerabilidades en código Python.
#
# Ejecución:
#   cd c:\Users\Javier\Desktop\FermentAI
#   .\tests\12_seguridad\run_bandit.ps1
#
# Requisito: pip install bandit safety
# ============================================================

param(
    [string]$OutputDir = "tests\reports",
    [string]$BackendDir = "backend\app"
)

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$banditReport = "$OutputDir\bandit_report_$timestamp.json"
$banditHtml   = "$OutputDir\bandit_report_$timestamp.html"
$safetyReport = "$OutputDir\safety_report_$timestamp.txt"

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "  ANÁLISIS ESTÁTICO DE SEGURIDAD — FermentAI" -ForegroundColor Cyan
Write-Host "  Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Cyan

$exitCode = 0

# ──────────────────────────────────────────────────────────────
# 1. Bandit — análisis de seguridad en código Python
# ──────────────────────────────────────────────────────────────
Write-Host "  [1/3] Ejecutando Bandit en $BackendDir..." -ForegroundColor Yellow

$banditCheck = Get-Command bandit -ErrorAction SilentlyContinue
if (-not $banditCheck) {
    Write-Host "  [WARN] bandit no instalado. Instalar con: pip install bandit" -ForegroundColor Yellow
} else {
    # Ejecutar bandit con severidad media+
    $banditOutput = bandit -r $BackendDir `
        -f json `
        -o $banditReport `
        --severity-level medium `
        --confidence-level medium `
        2>&1

    if (Test-Path $banditReport) {
        $banditData = Get-Content $banditReport | ConvertFrom-Json
        $issues = $banditData.results
        $highSeverity = $issues | Where-Object { $_.issue_severity -eq "HIGH" }
        $medSeverity  = $issues | Where-Object { $_.issue_severity -eq "MEDIUM" }

        Write-Host "`n  ── Resultados Bandit ──" -ForegroundColor White
        Write-Host "  Total issues     : $($issues.Count)" -ForegroundColor White
        Write-Host "  Alta severidad   : $($highSeverity.Count)" -ForegroundColor $(if ($highSeverity.Count -gt 0) { "Red" } else { "Green" })
        Write-Host "  Media severidad  : $($medSeverity.Count)" -ForegroundColor $(if ($medSeverity.Count -gt 0) { "Yellow" } else { "Green" })

        if ($highSeverity.Count -gt 0) {
            Write-Host "`n  Problemas de ALTA severidad:" -ForegroundColor Red
            foreach ($issue in $highSeverity) {
                Write-Host "    [$($issue.test_id)] $($issue.issue_text)" -ForegroundColor Red
                Write-Host "      Archivo: $($issue.filename):$($issue.line_number)" -ForegroundColor Gray
            }
            $exitCode = 1
        }

        if ($medSeverity.Count -gt 0) {
            Write-Host "`n  Problemas de MEDIA severidad:" -ForegroundColor Yellow
            foreach ($issue in $medSeverity | Select-Object -First 5) {
                Write-Host "    [$($issue.test_id)] $($issue.issue_text)" -ForegroundColor Yellow
                Write-Host "      Archivo: $($issue.filename):$($issue.line_number)" -ForegroundColor Gray
            }
        }

        # Generar reporte HTML también
        bandit -r $BackendDir -f html -o $banditHtml --severity-level low 2>&1 | Out-Null
        Write-Host "`n  Reporte JSON : $banditReport" -ForegroundColor Cyan
        Write-Host "  Reporte HTML : $banditHtml" -ForegroundColor Cyan
    }
}

# ──────────────────────────────────────────────────────────────
# 2. Safety — verificar dependencias con vulnerabilidades conocidas
# ──────────────────────────────────────────────────────────────
Write-Host "`n  [2/3] Verificando dependencias con Safety..." -ForegroundColor Yellow

$safetyCheck = Get-Command safety -ErrorAction SilentlyContinue
if (-not $safetyCheck) {
    Write-Host "  [WARN] safety no instalado. Instalar con: pip install safety" -ForegroundColor Yellow
} else {
    $requirementsFile = "backend\requirements.txt"
    if (Test-Path $requirementsFile) {
        $safetyOutput = safety check -r $requirementsFile --output text 2>&1
        $safetyOutput | Set-Content $safetyReport
        $safetyOutput | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

        if ($LASTEXITCODE -ne 0) {
            Write-Host "`n  [FAIL] Se encontraron vulnerabilidades en dependencias." -ForegroundColor Red
            Write-Host "  Reporte: $safetyReport" -ForegroundColor Cyan
            $exitCode = 1
        } else {
            Write-Host "`n  [PASS] No se encontraron vulnerabilidades conocidas." -ForegroundColor Green
        }
    } else {
        Write-Host "  [WARN] No se encontró $requirementsFile" -ForegroundColor Yellow
    }
}

# ──────────────────────────────────────────────────────────────
# 3. Verificaciones manuales de configuración
# ──────────────────────────────────────────────────────────────
Write-Host "`n  [3/3] Verificaciones de configuración..." -ForegroundColor Yellow

$checks = @(
    @{
        Nombre = "SECRET_KEY no es el valor por defecto"
        Archivo = "docker-compose.yml"
        Patron = "change-this-in-production-please"
        EsProblema = $true
    },
    @{
        Nombre = "DEBUG no habilitado en producción"
        Archivo = "backend\app\main.py"
        Patron = "debug=True"
        EsProblema = $true
    },
    @{
        Nombre = "Credenciales hardcodeadas en código"
        Archivo = "backend\app"
        Patron = "password123|secret123|admin123"
        EsProblema = $true
    }
)

foreach ($check in $checks) {
    $found = $false
    if (Test-Path $check.Archivo) {
        $content = if ((Get-Item $check.Archivo).PSIsContainer) {
            Get-ChildItem -Recurse -Path $check.Archivo -Include "*.py" |
                Get-Content -Raw -ErrorAction SilentlyContinue
        } else {
            Get-Content $check.Archivo -Raw -ErrorAction SilentlyContinue
        }
        if ($content -match $check.Patron) {
            $found = $true
        }
    }

    if ($found -and $check.EsProblema) {
        Write-Host "  [WARN] $($check.Nombre) — patrón encontrado" -ForegroundColor Yellow
    } elseif (-not $found -and -not $check.EsProblema) {
        Write-Host "  [PASS] $($check.Nombre)" -ForegroundColor Green
    } elseif (-not $found -and $check.EsProblema) {
        Write-Host "  [PASS] $($check.Nombre)" -ForegroundColor Green
    }
}

# ──────────────────────────────────────────────────────────────
# RESUMEN
# ──────────────────────────────────────────────────────────────
Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "  RESUMEN ANÁLISIS DE SEGURIDAD" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "  Estado: APROBADO — sin vulnerabilidades críticas" -ForegroundColor Green
} else {
    Write-Host "  Estado: REVISAR — se encontraron problemas de seguridad" -ForegroundColor Red
}
Write-Host "  Reportes en: $OutputDir" -ForegroundColor Cyan
Write-Host ""

exit $exitCode
