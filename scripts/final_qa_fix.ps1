$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$AppPath = Join-Path $ProjectRoot "frontend\src\App.jsx"

if (-not (Test-Path $AppPath)) {
    throw "No se encontró frontend\src\App.jsx"
}

Write-Host ""
Write-Host "============================================================"
Write-Host " EA-390 - QA final del dashboard"
Write-Host "============================================================"
Write-Host ""

$source = Get-Content $AppPath -Raw

$oldBlock = @'
    const lastActual = recentActual[recentActual.length - 1];

    return [
      ...recentActual,
      {
        ...lastActual,
        predicted_usd: lastActual.actual_usd,
        lower_usd: lastActual.actual_usd,
        upper_usd: lastActual.actual_usd,
      },
      ...forecast.forecast.map((point) => ({
        year: point.year,
        actual_usd: null,
        predicted_usd: point.predicted_usd,
        lower_usd: point.lower_usd,
        upper_usd: point.upper_usd,
      })),
    ];
'@

$newBlock = @'
    const lastActual = recentActual[recentActual.length - 1];

    const actualWithForecastBridge = recentActual.map((row, index) => {
      if (index !== recentActual.length - 1) {
        return row;
      }

      return {
        ...row,
        predicted_usd: row.actual_usd,
        lower_usd: row.actual_usd,
        upper_usd: row.actual_usd,
      };
    });

    return [
      ...actualWithForecastBridge,
      ...forecast.forecast.map((point) => ({
        year: point.year,
        actual_usd: null,
        predicted_usd: point.predicted_usd,
        lower_usd: point.lower_usd,
        upper_usd: point.upper_usd,
      })),
    ];
'@

if ($source.Contains($oldBlock)) {
    $source = $source.Replace($oldBlock, $newBlock)
    Set-Content -Path $AppPath -Value $source -Encoding UTF8
    Write-Host "[1/5] Corregido año 2025 duplicado en la gráfica de forecast."
}
elseif ($source.Contains("const actualWithForecastBridge")) {
    Write-Host "[1/5] La corrección del 2025 duplicado ya estaba aplicada."
}
else {
    throw "No se encontró el bloque esperado de forecastChartData. No se modificó App.jsx."
}

Write-Host "[2/5] Ejecutando tests del backend..."
docker compose exec -T api python -m pytest
if ($LASTEXITCODE -ne 0) {
    throw "Los tests del backend fallaron."
}

Write-Host "[3/5] Compilando frontend..."
docker compose exec -T frontend npm run build
if ($LASTEXITCODE -ne 0) {
    throw "El build del frontend falló."
}

Write-Host "[4/5] Recreando frontend..."
docker compose up -d --force-recreate frontend
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo recrear el frontend."
}

Write-Host "[5/5] Verificando servicios y forecast..."
docker compose ps

$Forecast = Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/forecast?horizon=3" `
    -TimeoutSec 30

if (-not $Forecast.selected_model -or $Forecast.forecast.Count -ne 3) {
    throw "La verificación del forecast falló."
}

Write-Host ""
Write-Host "Forecast:"
Write-Host "  Modelo: $($Forecast.selected_model)"
Write-Host "  MAE:    $($Forecast.mae)"
Write-Host "  RMSE:   $($Forecast.rmse)"
Write-Host ""
Write-Host "============================================================"
Write-Host " QA FINAL OK"
Write-Host "============================================================"
Write-Host ""
Write-Host "Refresca una vez con Ctrl+F5:"
Write-Host "  http://127.0.0.1:5173"
Write-Host ""
Write-Host "Si visualmente todo está correcto, el siguiente paso es DEPLOY."
