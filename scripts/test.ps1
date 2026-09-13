$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

docker compose exec -T api python -m pytest
docker compose exec -T frontend npm run build
