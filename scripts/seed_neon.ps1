$ErrorActionPreference = "Stop"

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
Write-Host " Guatemala Export Analytics - Seed Neon v2"
Write-Host "============================================================"
Write-Host ""
Write-Host "Usa la connection string DIRECT de Neon."
Write-Host "El hostname DIRECT no debe contener '-pooler'."
Write-Host "La cadena no se mostrará ni se guardará."
Write-Host ""

$SecureUrl = Read-Host "Pega la nueva DIRECT connection string de Neon y presiona Enter" -AsSecureString
$Bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureUrl)

try {
    $DatabaseUrl = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Bstr)
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Bstr)
}

if (
    -not $DatabaseUrl.StartsWith("postgresql://") -and
    -not $DatabaseUrl.StartsWith("postgres://")
) {
    throw "La cadena no parece una PostgreSQL connection string."
}

if ($DatabaseUrl -match "-pooler\.") {
    throw "La URL parece ser POOLED (-pooler). Para migraciones/seed usa DIRECT en Neon."
}

Write-Host "[1/5] Docker..."
docker info *> $null
Assert-NativeSuccess "Docker"

Write-Host "[2/5] API local..."
docker compose up -d api
Assert-NativeSuccess "docker compose up -d api"

Write-Host "[3/5] Migraciones en Neon con psycopg v3..."
docker compose exec -T `
    -e "DATABASE_URL=$DatabaseUrl" `
    api python -m alembic upgrade head
Assert-NativeSuccess "Neon migrations"

Write-Host "[4/5] Cargando dataset + SAC en Neon..."
docker compose exec -T `
    -e "DATABASE_URL=$DatabaseUrl" `
    api python -m app.infrastructure.etl.bootstrap_production
Assert-NativeSuccess "Neon bootstrap"

Write-Host "[5/5] Verificando Neon..."
docker compose exec -T `
    -e "DATABASE_URL=$DatabaseUrl" `
    api python -c "from app.core.database import SessionLocal; from app.infrastructure.repositories.sqlalchemy_export_repository import SQLAlchemyExportRepository; db=SessionLocal(); s=SQLAlchemyExportRepository(db).get_summary(); print({'first_year':s.first_year,'latest_year':s.latest_year,'latest_year_total_usd':s.latest_year_total_usd,'tariff_items':s.tariff_items,'observations':s.observations}); db.close()"
Assert-NativeSuccess "Neon verification"

$DatabaseUrl = $null
$SecureUrl = $null

Write-Host ""
Write-Host "============================================================"
Write-Host " NEON SEED OK"
Write-Host "============================================================"
