$ErrorActionPreference = "Continue"

function Assert-NativeSuccess {
    param([string]$Step)
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE."
    }
}

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host ""
Write-Host "============================================================"
Write-Host " Guatemala Export Analytics - Docker Bootstrap"
Write-Host "============================================================"
Write-Host ""
Write-Host "This setup runs BOTH FastAPI and PostgreSQL inside Docker."
Write-Host "The backend will no longer connect to Windows localhost ports."
Write-Host ""

Write-Host "[1/8] Checking Docker Engine..."
docker info *> $null
Assert-NativeSuccess "Docker Engine check"

Write-Host "[2/8] Removing OLD project containers and database volume..."
docker compose down -v --remove-orphans
Assert-NativeSuccess "docker compose down"

Write-Host "[3/8] Building API image..."
docker compose build api
Assert-NativeSuccess "docker compose build api"

Write-Host "[4/8] Starting PostgreSQL + FastAPI..."
docker compose up -d
Assert-NativeSuccess "docker compose up"

Write-Host "[5/8] Waiting for the API container..."
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    $apiState = docker inspect --format='{{.State.Status}}' export-analytics-api 2>$null
    $dbHealth = docker inspect --format='{{.State.Health.Status}}' export-analytics-db 2>$null

    if ($apiState -eq "running" -and $dbHealth -eq "healthy") {
        try {
            $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2
            if ($response.status -eq "ok") {
                $ready = $true
                break
            }
        } catch {}
    }

    Start-Sleep -Seconds 2
}

if (-not $ready) {
    docker compose ps
    docker compose logs --tail=120 api
    docker compose logs --tail=120 db
    throw "Containers did not become ready."
}

Write-Host "API and PostgreSQL are ready."

Write-Host "[6/8] Inspecting and validating CSV inside API container..."
docker compose exec -T api python -m app.infrastructure.etl.inspect_dataset
Assert-NativeSuccess "dataset inspection"

Write-Host "[7/8] Loading validated dataset into PostgreSQL..."
docker compose exec -T api python -m app.infrastructure.etl.load_exports
Assert-NativeSuccess "ETL load"

Write-Host "[8/8] Verifying database counts and API analytics..."
docker compose exec -T db psql -U export_user -d export_analytics -c "SELECT COUNT(*) AS tariff_items FROM tariff_items;"
Assert-NativeSuccess "tariff_items verification"

docker compose exec -T db psql -U export_user -d export_analytics -c "SELECT COUNT(*) AS export_values FROM export_values;"
Assert-NativeSuccess "export_values verification"

Invoke-RestMethod -Uri "http://127.0.0.1:8000/analytics/summary" -TimeoutSec 10 |
    ConvertTo-Json -Depth 4

Write-Host ""
Write-Host "============================================================"
Write-Host " SUCCESS - THE PROJECT IS FULLY RUNNING"
Write-Host "============================================================"
Write-Host ""
Write-Host "Swagger: http://127.0.0.1:8000/docs"
Write-Host "Normal startup from now on: docker compose up -d"
