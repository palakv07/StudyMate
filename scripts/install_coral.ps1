# Install Coral SQL CLI into backend/coral/ (Windows x64)
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$CoralDir = Join-Path $ProjectRoot "backend\coral"
$ZipName = "coral-x86_64-pc-windows-msvc.zip"
$ZipPath = Join-Path $CoralDir $ZipName
$ExePath = Join-Path $CoralDir "coral.exe"
$DownloadUrl = "https://github.com/withcoral/coral/releases/latest/download/coral-x86_64-pc-windows-msvc.zip"

Write-Host "AI StudyMate — Installing Coral..." -ForegroundColor Cyan

if (-not (Test-Path $CoralDir)) {
    New-Item -ItemType Directory -Path $CoralDir -Force | Out-Null
}

if (Test-Path $ExePath) {
    $version = & $ExePath --version 2>$null
    Write-Host "Coral already installed at $ExePath ($version)" -ForegroundColor Green
    exit 0
}

Write-Host "Downloading Coral from GitHub releases..."
try {
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $ZipPath -UseBasicParsing
} catch {
    Write-Host "Download failed: $_" -ForegroundColor Red
    Write-Host "Manual install: $DownloadUrl" -ForegroundColor Yellow
    exit 1
}

Write-Host "Extracting..."
Expand-Archive -Path $ZipPath -DestinationPath $CoralDir -Force

# Zip may contain coral.exe at root or in subfolder
$found = Get-ChildItem -Path $CoralDir -Filter "coral.exe" -Recurse | Select-Object -First 1
if ($found -and $found.FullName -ne $ExePath) {
    Copy-Item $found.FullName $ExePath -Force
}

Remove-Item $ZipPath -Force -ErrorAction SilentlyContinue

if (Test-Path $ExePath) {
    & $ExePath --version
    Write-Host "Coral installed: $ExePath" -ForegroundColor Green
} else {
    Write-Host "coral.exe not found after extract." -ForegroundColor Red
    exit 1
}
