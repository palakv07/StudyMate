# Register Coral sources: local sheets CSV + Notion API
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$CoralExe = Join-Path $ProjectRoot "backend\coral\coral.exe"
$DataDir = Join-Path $ProjectRoot "backend\coral\data"
$SheetsYaml = Join-Path $ProjectRoot "backend\coral\sources\sheets.yaml"
$EnvFile = Join-Path $ProjectRoot "backend\.env"

if (-not (Test-Path $CoralExe)) {
    Write-Host "Run scripts\install_coral.ps1 first." -ForegroundColor Red
    exit 1
}

# Patch sheets.yaml with absolute file:// path for Coral
$absData = (Resolve-Path $DataDir).Path.Replace("\", "/")
$yamlContent = Get-Content $SheetsYaml -Raw
$yamlContent = $yamlContent -replace "file:///CORAL_DATA_DIR/", "file:///$absData/"
$patchedYaml = Join-Path $ProjectRoot "backend\coral\sources\sheets.patched.yaml"
$yamlContent | Set-Content $patchedYaml -Encoding UTF8

Write-Host "Adding sheets file source..."
& $CoralExe source add --file $patchedYaml 2>&1 | Out-Host

if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $val = $matches[2].Trim()
            if ($val) { Set-Item -Path "env:$name" -Value $val }
        }
    }
}

if ($env:NOTION_API_KEY) {
    Write-Host "Adding Notion source (interactive may prompt if not in env)..."
    $env:NOTION_API_KEY = $env:NOTION_API_KEY
    & $CoralExe source add notion --interactive 2>&1 | Out-Host
} else {
    Write-Host "Skip Notion Coral source — set NOTION_API_KEY in backend\.env first." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Test with:" -ForegroundColor Cyan
Write-Host "  backend\coral\coral.exe sql `"SHOW TABLES;`""
Write-Host "  backend\coral\coral.exe sql `"SELECT * FROM sheets.leetcode_progress LIMIT 5;`""
