# ============================================================
# Pruebas de Conectividad — FermentAI
# Valida rutas de red hacia los servicios usando tracert,
# Test-NetConnection y resolución DNS.
#
# Ejecución:
#   cd c:\Users\Javier\Desktop\FermentAI
#   .\tests\06_conectividad\tracert_checks.ps1
#
# Salida: tests\reports\conectividad_report.txt
# ============================================================

param(
    [string]$ApiHost = "localhost",
    [int]$ApiPort = 8000,
    [string]$FrontendHost = "localhost",
    [int]$FrontendPort = 3000,
    [string]$DbHost = "localhost",
    [int]$DbPort = 5432,
    [string]$MinioHost = "localhost",
    [int]$MinioPort = 9000,
    [string]$OutputDir = "tests\reports"
)

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$reportFile = "$OutputDir\conectividad_report_$timestamp.txt"

# Crear directorio de reportes si no existe
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$resultados = @()
$pasados = 0
$fallidos = 0

function Write-Section($titulo) {
    $sep = "=" * 60
    Write-Host "`n$sep" -ForegroundColor Cyan
    Write-Host "  $titulo" -ForegroundColor Cyan
    Write-Host $sep -ForegroundColor Cyan
    Add-Content $reportFile "`n$sep`n  $titulo`n$sep"
}

function Test-Puerto($host, $puerto, $nombre) {
    Write-Host "`n  Probando $nombre ($host`:$puerto)..." -ForegroundColor Yellow
    try {
        $conn = Test-NetConnection -ComputerName $host -Port $puerto -WarningAction SilentlyContinue
        if ($conn.TcpTestSucceeded) {
            Write-Host "  [PASS] $nombre — Puerto $puerto accesible" -ForegroundColor Green
            Add-Content $reportFile "  [PASS] $nombre — Puerto $puerto accesible"
            $script:pasados++
            return $true
        } else {
            Write-Host "  [FAIL] $nombre — Puerto $puerto NO accesible" -ForegroundColor Red
            Add-Content $reportFile "  [FAIL] $nombre — Puerto $puerto NO accesible"
            $script:fallidos++
            return $false
        }
    } catch {
        Write-Host "  [ERROR] $nombre — $_" -ForegroundColor Red
        Add-Content $reportFile "  [ERROR] $nombre — $_"
        $script:fallidos++
        return $false
    }
}

function Test-DNS($hostname) {
    Write-Host "`n  Resolución DNS: $hostname" -ForegroundColor Yellow
    if ($hostname -eq "localhost") {
        Write-Host "  [INFO] localhost no requiere resolución DNS externa" -ForegroundColor Cyan
        Add-Content $reportFile "  [INFO] localhost — loopback, no requiere DNS externo"
        return
    }
    try {
        $ips = [System.Net.Dns]::GetHostAddresses($hostname)
        Write-Host "  [PASS] $hostname resuelve a: $($ips.IPAddressToString -join ', ')" -ForegroundColor Green
        Add-Content $reportFile "  [PASS] DNS $hostname => $($ips.IPAddressToString -join ', ')"
        $script:pasados++
    } catch {
        Write-Host "  [FAIL] No se pudo resolver $hostname" -ForegroundColor Red
        Add-Content $reportFile "  [FAIL] DNS $hostname — sin resolución"
        $script:fallidos++
    }
}

function Test-Tracert($target) {
    if ($target -eq "localhost") {
        Write-Host "  [INFO] tracert a localhost: ruta directa (loopback)" -ForegroundColor Cyan
        Add-Content $reportFile "  [INFO] tracert localhost — ruta loopback directa"
        return
    }
    Write-Host "`n  tracert $target (máx 10 saltos)..." -ForegroundColor Yellow
    $output = tracert -h 10 $target 2>&1
    $lineas = $output | Where-Object { $_ -match "\d+\s+<?\d+" }
    Add-Content $reportFile "  Ruta tracert hacia $target`:`n$($output -join "`n")"
    Write-Host "  [INFO] Saltos detectados: $($lineas.Count)" -ForegroundColor Cyan
}

function Test-Latencia($url, $nombre) {
    Write-Host "`n  Midiendo latencia HTTP: $nombre" -ForegroundColor Yellow
    $tiempos = @()
    for ($i = 0; $i -lt 5; $i++) {
        try {
            $sw = [System.Diagnostics.Stopwatch]::StartNew()
            $null = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
            $sw.Stop()
            $tiempos += $sw.ElapsedMilliseconds
        } catch {
            $tiempos += 9999
        }
        Start-Sleep -Milliseconds 200
    }
    $exitosos = $tiempos | Where-Object { $_ -lt 9999 }
    if ($exitosos.Count -gt 0) {
        $avg = [math]::Round(($exitosos | Measure-Object -Average).Average, 1)
        $min = ($exitosos | Measure-Object -Minimum).Minimum
        $max = ($exitosos | Measure-Object -Maximum).Maximum
        Write-Host "  [INFO] Avg: ${avg}ms | Min: ${min}ms | Max: ${max}ms" -ForegroundColor Cyan
        Add-Content $reportFile "  Latencia $nombre — Avg: ${avg}ms | Min: ${min}ms | Max: ${max}ms"
        $script:pasados++
    } else {
        Write-Host "  [FAIL] $nombre no respondió" -ForegroundColor Red
        Add-Content $reportFile "  [FAIL] Latencia $nombre — sin respuesta"
        $script:fallidos++
    }
}

# ──────────────────────────────────────────────────────────────
# INICIO DEL REPORTE
# ──────────────────────────────────────────────────────────────
$header = @"
========================================================
  REPORTE DE CONECTIVIDAD — FermentAI
  Fecha: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
  Equipo: $env:COMPUTERNAME
  Usuario: $env:USERNAME
  OS: $(([System.Environment]::OSVersion).VersionString)
========================================================
"@
Write-Host $header -ForegroundColor White
Set-Content $reportFile $header

# ──────────────────────────────────────────────────────────────
# 1. INFORMACIÓN DE RED LOCAL
# ──────────────────────────────────────────────────────────────
Write-Section "1. INTERFACES DE RED ACTIVAS"
$adaptadores = Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -ne "127.0.0.1" } |
    Select-Object InterfaceAlias, IPAddress, PrefixLength
$adaptadores | Format-Table -AutoSize | Tee-Object -Append -FilePath $reportFile | Out-Null

# ──────────────────────────────────────────────────────────────
# 2. PRUEBAS DE PUERTOS
# ──────────────────────────────────────────────────────────────
Write-Section "2. PRUEBAS DE CONECTIVIDAD DE PUERTOS"
Test-Puerto $ApiHost $ApiPort "API Backend (FastAPI)"
Test-Puerto $FrontendHost $FrontendPort "Frontend (Next.js)"
Test-Puerto $DbHost $DbPort "Base de datos (PostgreSQL)"
Test-Puerto $MinioHost $MinioPort "MinIO (Object Storage)"
Test-Puerto $MinioHost 9001 "MinIO Console"

# ──────────────────────────────────────────────────────────────
# 3. RESOLUCIÓN DNS
# ──────────────────────────────────────────────────────────────
Write-Section "3. RESOLUCIÓN DNS"
Test-DNS $ApiHost
Test-DNS $FrontendHost
Test-DNS "google.com"  # Verificar conectividad externa

# ──────────────────────────────────────────────────────────────
# 4. TRACERT
# ──────────────────────────────────────────────────────────────
Write-Section "4. TRAZADO DE RUTA (TRACERT)"
Test-Tracert $ApiHost
Test-Tracert "8.8.8.8"  # Google DNS para verificar conectividad externa

# ──────────────────────────────────────────────────────────────
# 5. LATENCIA HTTP
# ──────────────────────────────────────────────────────────────
Write-Section "5. LATENCIA HTTP (5 muestras por servicio)"
Test-Latencia "http://$ApiHost`:$ApiPort/health" "API Health"
Test-Latencia "http://$FrontendHost`:$FrontendPort" "Frontend Home"
Test-Latencia "http://$ApiHost`:$ApiPort/openapi.json" "API OpenAPI Schema"

# ──────────────────────────────────────────────────────────────
# 6. TABLA ARP (caché de vecinos de red)
# ──────────────────────────────────────────────────────────────
Write-Section "6. TABLA ARP (vecinos de red)"
$arpOutput = arp -a 2>&1
Write-Host ($arpOutput | Select-Object -First 20 | Out-String) -ForegroundColor Gray
($arpOutput | Select-Object -First 20) | ForEach-Object { Add-Content $reportFile "  $_" }

# ──────────────────────────────────────────────────────────────
# 7. RESUMEN FINAL
# ──────────────────────────────────────────────────────────────
Write-Section "7. RESUMEN"
$total = $pasados + $fallidos
$pct = if ($total -gt 0) { [math]::Round($pasados / $total * 100, 1) } else { 0 }
$resumen = @"
  Total pruebas : $total
  Pasadas       : $pasados
  Fallidas      : $fallidos
  Éxito         : $pct%
  Reporte       : $reportFile
"@
Write-Host $resumen -ForegroundColor $(if ($fallidos -eq 0) { "Green" } else { "Yellow" })
Add-Content $reportFile $resumen

Write-Host "`n  Reporte guardado en: $reportFile`n" -ForegroundColor Cyan

if ($fallidos -gt 0) {
    Write-Host "  ADVERTENCIA: $fallidos prueba(s) fallaron. Revisar el reporte." -ForegroundColor Red
    exit 1
} else {
    Write-Host "  Todas las pruebas de conectividad pasaron." -ForegroundColor Green
    exit 0
}
