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
Write-Host " EA-300 - Forecasting Upgrade"
Write-Host "============================================================"
Write-Host ""

$StylesPath = Join-Path $ProjectRoot "frontend\src\styles.css"
$Styles = Get-Content $StylesPath -Raw

if ($Styles -notmatch 'forecast\.css') {
    Add-Content -Path $StylesPath -Value "`n@import `"./forecast.css`";"
    Write-Host "[0/6] Added forecast.css import."
} else {
    Write-Host "[0/6] forecast.css already imported."
}

Write-Host "[1/6] Building API with Statsmodels..."
docker compose build api
Assert-NativeSuccess "API build"

Write-Host "[2/6] Building frontend..."
docker compose build frontend
Assert-NativeSuccess "Frontend build"

Write-Host "[3/6] Starting/recreating services..."
docker compose up -d --force-recreate api frontend
Assert-NativeSuccess "Service recreation"

Write-Host "[4/6] Waiting for API..."
$Ready = $false
for ($i = 0; $i -lt 45; $i++) {
    try {
        $Health = Invoke-RestMethod `
            -Uri "http://127.0.0.1:8000/health" `
            -TimeoutSec 2
        if ($Health.status -eq "ok") {
            $Ready = $true
            break
        }
    } catch {}

    Start-Sleep -Seconds 2
}

if (-not $Ready) {
    docker compose logs --tail=100 api
    throw "API did not become ready."
}

Write-Host "[5/6] Running automated tests..."
docker compose exec -T api python -m pytest
Assert-NativeSuccess "pytest"

Write-Host "[6/6] Verifying real forecast endpoint..."
$Forecast = Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/forecast?horizon=3" `
    -TimeoutSec 30

$Forecast | ConvertTo-Json -Depth 6

if (-not $Forecast.selected_model -or $Forecast.forecast.Count -ne 3) {
    throw "Forecast response is incomplete."
}

Write-Host ""
Write-Host "============================================================"
Write-Host " SUCCESS - Forecasting is working"
Write-Host "============================================================"
Write-Host ""
Write-Host "Selected model: $($Forecast.selected_model)"
Write-Host "MAE: $($Forecast.mae)"
Write-Host "RMSE: $($Forecast.rmse)"
Write-Host ""
Write-Host "Dashboard:"
Write-Host "  http://127.0.0.1:5173"
Write-Host ""
Write-Host "Swagger:"
Write-Host "  http://127.0.0.1:8000/docs"
