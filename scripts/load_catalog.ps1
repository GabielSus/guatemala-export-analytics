$ErrorActionPreference = "Continue"

function Assert-NativeSuccess {
    param([string]$Step)

    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE."
    }
}

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$CatalogPath = Join-Path $ProjectRoot "data\raw\sac.pdf"
$CatalogUrl = "https://www.banguat.gob.gt/estaeco/ceie/sac.pdf"

Write-Host ""
Write-Host "============================================================"
Write-Host " EA-200 - Official SAC Catalog Loader (hotfix)"
Write-Host "============================================================"
Write-Host ""

# If the existing file is missing or is not a real PDF, fetch the exact
# official Banguat file. We do not overwrite an already-valid PDF.
$NeedDownload = $true

if (Test-Path $CatalogPath) {
    try {
        $stream = [System.IO.File]::OpenRead($CatalogPath)
        $bytes = New-Object byte[] 4
        [void]$stream.Read($bytes, 0, 4)
        $stream.Close()
        $signature = [System.Text.Encoding]::ASCII.GetString($bytes)

        if ($signature -eq "%PDF") {
            $NeedDownload = $false
            Write-Host "[0/6] Existing sac.pdf has a valid PDF signature."
        } else {
            Write-Host "[0/6] Existing sac.pdf is not a real PDF. It will be replaced."
        }
    } catch {
        Write-Host "[0/6] Could not validate existing sac.pdf. It will be replaced."
    }
}

if ($NeedDownload) {
    Write-Host "[0/6] Downloading the exact official Banguat SAC PDF..."
    Invoke-WebRequest `
        -Uri $CatalogUrl `
        -OutFile $CatalogPath `
        -Headers @{ "User-Agent" = "Mozilla/5.0" }

    if (-not (Test-Path $CatalogPath)) {
        throw "Could not download the official SAC PDF."
    }
}

Write-Host "[1/6] Rebuilding API image..."
docker compose build api
Assert-NativeSuccess "docker compose build api"

Write-Host "[2/6] Starting services..."
docker compose up -d
Assert-NativeSuccess "docker compose up"

Write-Host "[3/6] Applying database migrations..."
docker compose exec -T api python -m alembic upgrade head
Assert-NativeSuccess "alembic upgrade head"

Write-Host "[4/6] Parsing and loading official SAC nomenclature..."
docker compose exec -T api python -m app.infrastructure.etl.load_tariff_catalog
Assert-NativeSuccess "SAC catalog load"

Write-Host "[5/6] Running automated tests..."
docker compose exec -T api python -m pytest
Assert-NativeSuccess "pytest"

Write-Host "[6/6] Verifying catalog data..."
docker compose exec -T db psql -U export_user -d export_analytics -c "SELECT COUNT(*) AS catalog_rows FROM tariff_catalog;"
Assert-NativeSuccess "catalog count verification"

Write-Host ""
Write-Host "Checking a known official item (0901113000)..."
docker compose exec -T db psql -U export_user -d export_analytics -c "SELECT code, display_name FROM tariff_catalog WHERE code='0901113000';"
Assert-NativeSuccess "known code verification"

Write-Host ""
Write-Host "============================================================"
Write-Host " SUCCESS - SAC catalog enrichment is working"
Write-Host "============================================================"
Write-Host ""
Write-Host "Refresh dashboard:"
Write-Host "  http://127.0.0.1:5173"
