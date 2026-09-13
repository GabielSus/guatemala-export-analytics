$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "Containers"
docker compose ps

Write-Host "`nDatabase counts"
docker compose exec -T db psql -U export_user -d export_analytics -c "SELECT COUNT(*) AS tariff_items FROM tariff_items;"
docker compose exec -T db psql -U export_user -d export_analytics -c "SELECT COUNT(*) AS export_values FROM export_values;"

Write-Host "`nAPI summary"
Invoke-RestMethod http://127.0.0.1:8000/analytics/summary | ConvertTo-Json
