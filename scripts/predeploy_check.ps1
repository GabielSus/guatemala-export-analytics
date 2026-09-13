$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host ""
Write-Host "============================================================"
Write-Host " EA-400 - Pre-deploy check"
Write-Host "============================================================"
Write-Host ""

$RequiredFiles = @(
    "data\raw\exportaciones_banguat.csv",
    "data\raw\sac.pdf",
    "Dockerfile.production",
    "render.yaml",
    "frontend\vercel.json"
)

foreach ($File in $RequiredFiles) {
    if (-not (Test-Path (Join-Path $ProjectRoot $File))) {
        throw "Missing deploy file: $File"
    }
}

Write-Host "[1/5] Required deploy files OK."

Write-Host "[2/5] Backend tests..."
docker compose exec -T api python -m pytest
if ($LASTEXITCODE -ne 0) {
    throw "Backend tests failed."
}

Write-Host "[3/5] Frontend production build..."
docker compose exec -T frontend npm run build
if ($LASTEXITCODE -ne 0) {
    throw "Frontend build failed."
}

Write-Host "[4/5] Checking data file sizes..."
Get-Item `
    "data\raw\exportaciones_banguat.csv",
    "data\raw\sac.pdf" |
    Select-Object Name, Length |
    Format-Table -AutoSize

Write-Host "[5/5] Git status..."
git status --short

Write-Host ""
Write-Host "============================================================"
Write-Host " PRE-DEPLOY CHECK OK"
Write-Host "============================================================"
Write-Host ""
Write-Host "Next:"
Write-Host "  git add ."
Write-Host '  git commit -m "chore(EA-400): prepare production deployment"'
Write-Host "  git push"
