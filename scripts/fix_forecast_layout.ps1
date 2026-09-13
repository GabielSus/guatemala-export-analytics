$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$StylesPath = Join-Path $ProjectRoot "frontend\src\styles.css"

if (-not (Test-Path $StylesPath)) {
    throw "No se encontró frontend\src\styles.css"
}

$css = Get-Content $StylesPath -Raw

# CSS @import rules must appear before normal CSS rules.
# Remove any previous forecast import wherever it is and prepend it correctly.
$css = $css -replace '(?m)^\s*@import\s+["'']\./forecast\.css["''];?\s*\r?\n?', ''
$css = '@import "./forecast.css";' + [Environment]::NewLine + [Environment]::NewLine + $css.TrimStart()

Set-Content -Path $StylesPath -Value $css -Encoding UTF8

Write-Host "[1/3] forecast.css import corregido al inicio de styles.css."

Write-Host "[2/3] Reconstruyendo/recreando frontend..."
docker compose build frontend
if ($LASTEXITCODE -ne 0) {
    throw "Falló docker compose build frontend."
}

docker compose up -d --force-recreate frontend
if ($LASTEXITCODE -ne 0) {
    throw "Falló al recrear frontend."
}

Write-Host "[3/3] Estado del frontend:"
docker compose ps frontend

Write-Host ""
Write-Host "LISTO."
Write-Host "Abre http://127.0.0.1:5173 y presiona Ctrl+F5 una vez."
