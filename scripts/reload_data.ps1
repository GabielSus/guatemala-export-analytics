$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

docker compose exec -T api python -m app.infrastructure.etl.inspect_dataset
docker compose exec -T api python -m app.infrastructure.etl.load_exports
