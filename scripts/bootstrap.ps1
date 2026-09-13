$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "=== Guatemala Export Analytics MVP bootstrap ==="
Write-Host "[1/6] Building and starting containers..."
docker compose up -d --build

Write-Host "[2/6] Waiting for PostgreSQL and API..."
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $health = Invoke-RestMethod "http://127.0.0.1:8000/health" -TimeoutSec 2
        if ($health.status -eq "ok") { $ready = $true; break }
    } catch {}
    Start-Sleep -Seconds 2
}
if (-not $ready) {
    docker compose ps
    docker compose logs --tail=100 api
    throw "API did not become ready."
}

Write-Host "[3/6] Checking database contents..."
$countText = docker compose exec -T db psql -U export_user -d export_analytics -tAc "SELECT COUNT(*) FROM export_values;"
$count = [int64]$countText.Trim()

if ($count -eq 0) {
    Write-Host "Database is empty. Running validated ETL..."
    docker compose exec -T api python -m app.infrastructure.etl.inspect_dataset
    docker compose exec -T api python -m app.infrastructure.etl.load_exports
} else {
    Write-Host "Database already contains $count export observations. ETL skipped."
}

Write-Host "[4/6] Running backend tests..."
docker compose exec -T api python -m pytest

Write-Host "[5/6] Building frontend as verification..."
docker compose exec -T frontend npm run build

Write-Host "[6/6] Verifying analytics API..."
Invoke-RestMethod "http://127.0.0.1:8000/analytics/summary" | ConvertTo-Json

Write-Host ""
Write-Host "MVP READY"
Write-Host "Dashboard: http://127.0.0.1:5173"
Write-Host "Swagger:   http://127.0.0.1:8000/docs"
