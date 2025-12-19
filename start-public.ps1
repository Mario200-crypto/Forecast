# Script para iniciar con acceso desde red local (Windows PowerShell)

Write-Host "=== Configuración para Acceso desde Red Local ===" -ForegroundColor Cyan

# Obtener IP local
$ipAddresses = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    $_.InterfaceAlias -notlike "*Loopback*" -and 
    $_.IPAddress -notlike "169.254.*" -and
    $_.IPAddress -notlike "127.*"
}

if ($ipAddresses.Count -eq 0) {
    Write-Host "No se pudo encontrar una IP local válida" -ForegroundColor Red
    exit 1
}

$ip = $ipAddresses[0].IPAddress
Write-Host "`nTu IP local es: $ip" -ForegroundColor Green
Write-Host "Accede desde otros dispositivos en: http://$ip:3000" -ForegroundColor Yellow
Write-Host "`nAsegúrate de que los dispositivos estén en la misma red WiFi`n" -ForegroundColor Cyan

# Configurar variable de entorno
$env:REACT_APP_API_URL = "http://$ip:8000"

Write-Host "Iniciando servicios con API URL: $env:REACT_APP_API_URL" -ForegroundColor Green
Write-Host "`nPresiona Ctrl+C para detener los servicios`n" -ForegroundColor Gray

# Iniciar docker-compose
docker-compose -f docker-compose.dev.yml up --build

