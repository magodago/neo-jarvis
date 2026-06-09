# subir-tweet-web.ps1 - Publica tweets usando Edge (tu sesion ya logueada)
# REQUISITOS: Tener Microsoft Edge WebDriver
# O mejor: usa la consola de JavaScript

param(
    [string]$texto = ""
)

if (-not $texto) {
    # Menu interactivo
    Write-Host "=== PUBLICAR TWEET VIA WEB ===" -ForegroundColor Cyan
    Write-Host "Escribe el texto del tweet (Enter para publicar):" -ForegroundColor Yellow
    $texto = Read-Host
    if (-not $texto) { exit }
}

# Escapar caracteres especiales para URL
$textoUrl = [uri]::EscapeDataString($texto)

# Opcion 1: Abrir Edge con la URL de composer de Twitter
Write-Host "Abriendo Twitter en Edge..." -ForegroundColor Green
Start-Process "ms-edge" "https://x.com/intent/post?text=$textoUrl"

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Twitter abierto con el texto listo!" -ForegroundColor Green
Write-Host "  Solo tienes que hacer clic en Postear" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Opcion 2: Si tienes el Edge WebDriver configurado, descomenta:
# Usar Selenium para automatico completo (opcional)
# Install-Module -Name Selenium -Force -Scope CurrentUser
# $Driver = Start-SeEdge
# Enter-SeUrl "https://x.com/login" -Driver $Driver
# ...
