# Quick helper: run Coral SQL REPL-style one-shot
param(
    [string]$Query = "SHOW TABLES;"
)
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$CoralExe = Join-Path $ProjectRoot "backend\coral\coral.exe"
if (-not (Test-Path $CoralExe)) {
    Write-Host "Install Coral: scripts\install_coral.ps1"
    exit 1
}
& $CoralExe sql $Query
