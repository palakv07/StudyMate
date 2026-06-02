# Example Coral SQL queries for AI StudyMate
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$CoralExe = Join-Path $ProjectRoot "backend\coral\coral.exe"

if (-not (Test-Path $CoralExe)) {
    Write-Host "Install Coral first: scripts\install_coral.ps1" -ForegroundColor Red
    exit 1
}

$queries = @(
    "SHOW TABLES;",
    "SELECT topic, AVG(weakness_score) AS avg_weak FROM sheets.leetcode_progress GROUP BY topic ORDER BY avg_weak DESC;",
    "SELECT problem, difficulty FROM sheets.leetcode_progress WHERE status != 'Solved' ORDER BY weakness_score DESC LIMIT 5;"
)

foreach ($q in $queries) {
    Write-Host "`n=== $q ===" -ForegroundColor Cyan
    & $CoralExe sql $q
}
