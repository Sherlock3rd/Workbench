param(
  [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$AppRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $AppRoot

if (-not $SkipInstall) {
  npm install
}

if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
  py -3 -m pip install pyinstaller
}

if (Test-Path "helper-dist") {
  Remove-Item "helper-dist" -Recurse -Force
}
if (Test-Path "helper-build") {
  Remove-Item "helper-build" -Recurse -Force
}

pyinstaller `
  --onefile `
  --name build_levelpoints_payload `
  --hidden-import openpyxl `
  --distpath helper-dist `
  --workpath helper-build `
  --specpath helper-build `
  "helper/build_levelpoints_payload.py"

npm run build
