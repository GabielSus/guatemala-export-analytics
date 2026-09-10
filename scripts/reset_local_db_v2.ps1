$ErrorActionPreference = "Continue"

function Assert-NativeSuccess {
    param(
        [string]$Step
    )

    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE."
    }
}

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $ProjectRoot "backend"

Write-Host ""
Write-Host "=== Guatemala Export Analytics - Local DB Repair v2 ==="
Write-Host ""

Set-Location $ProjectRoot

Write-Host "[1/7] Removing old resources from THIS project..."
docker compose down -v --remove-orphans
Assert-NativeSuccess "docker compose down"

Write-Host ""
Write-Host "[2/7] Starting PostgreSQL on 127.0.0.1:55432..."
docker compose up -d db
Assert-NativeSuccess "docker compose up"

Write-Host ""
Write-Host "[3/7] Waiting for PostgreSQL health check..."
$healthy = $false

for ($i = 0; $i -lt 30; $i++) {
    $status = docker inspect --format='{{.State.Health.Status}}' export-analytics-db 2>$null

    if ($LASTEXITCODE -eq 0 -and $status -eq "healthy") {
        $healthy = $true
        break
    }

    Start-Sleep -Seconds 2
}

if (-not $healthy) {
    Write-Host ""
    Write-Host "PostgreSQL did not become healthy. Current status:"
    docker compose ps
    Write-Host ""
    Write-Host "Last PostgreSQL logs:"
    docker compose logs --tail=100 db
    throw "PostgreSQL did not become healthy."
}

Write-Host "PostgreSQL is healthy."

Write-Host ""
Write-Host "[4/7] Recreating backend/.env with synchronized credentials..."
@"
APP_NAME=Guatemala Export Analytics
APP_VERSION=0.1.1
DATABASE_URL=postgresql+psycopg://export_user:export_dev_password@127.0.0.1:55432/export_analytics
"@ | Set-Content -Encoding UTF8 (Join-Path $Backend ".env")

Set-Location $Backend

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "backend\.venv was not found. Create it first with: py -3.12 -m venv .venv"
}

Write-Host ""
Write-Host "[5/7] Checking the exact PostgreSQL instance reached by the backend..."
& ".\.venv\Scripts\python.exe" -m app.infrastructure.database.check_connection
Assert-NativeSuccess "database connection check"

Write-Host ""
Write-Host "[6/7] Applying Alembic migrations..."
& ".\.venv\Scripts\python.exe" -m alembic upgrade head
Assert-NativeSuccess "alembic upgrade head"

& ".\.venv\Scripts\python.exe" -m alembic current
Assert-NativeSuccess "alembic current"

Write-Host ""
Write-Host "[7/7] Running tests..."
& ".\.venv\Scripts\python.exe" -m pytest
Assert-NativeSuccess "pytest"

Write-Host ""
Write-Host "============================================================"
Write-Host "SUCCESS - PostgreSQL, Alembic and tests are working."
Write-Host "============================================================"
Write-Host ""
Write-Host "Next command:"
Write-Host "  .\.venv\Scripts\python.exe -m app.infrastructure.etl.inspect_dataset"
