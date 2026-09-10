$ErrorActionPreference = "Continue"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

docker compose up -d
if ($LASTEXITCODE -ne 0) {
    throw "Could not start the project."
}

docker compose ps
Write-Host ""
Write-Host "Swagger: http://127.0.0.1:8000/docs"
