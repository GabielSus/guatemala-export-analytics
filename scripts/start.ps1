$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

docker compose up -d --build
Write-Host ""
docker compose ps
Write-Host ""
Write-Host "Dashboard: http://127.0.0.1:5173"
Write-Host "Swagger:   http://127.0.0.1:8000/docs"
