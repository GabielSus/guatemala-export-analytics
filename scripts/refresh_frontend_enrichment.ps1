$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host ""
Write-Host "============================================================"
Write-Host " EA-200 - Frontend Enrichment Refresh"
Write-Host "============================================================"
Write-Host ""

Write-Host "[1/4] Verifying API descriptions..."
$items = Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/analytics/top-items?year=2024&limit=3" `
    -TimeoutSec 10

if (-not $items -or -not $items[0].description) {
    Write-Host ""
    Write-Host "The API is not returning SAC descriptions yet."
    Write-Host "First run: .\scripts\load_catalog.ps1"
    throw "SAC descriptions are missing from the API."
}

Write-Host "API OK:"
$items | Select-Object rank, code, description | Format-Table -AutoSize

Write-Host "[2/4] Rebuilding frontend..."
docker compose build frontend
if ($LASTEXITCODE -ne 0) {
    throw "Frontend build failed."
}

Write-Host "[3/4] Recreating frontend container..."
docker compose up -d --force-recreate frontend
if ($LASTEXITCODE -ne 0) {
    throw "Frontend restart failed."
}

Write-Host "[4/4] Checking frontend container..."
docker compose ps frontend

Write-Host ""
Write-Host "SUCCESS - Frontend enrichment is active."
Write-Host "Open/refresh:"
Write-Host "  http://127.0.0.1:5173"
Write-Host ""
Write-Host "If the browser still shows the old UI, press Ctrl+F5 once."
