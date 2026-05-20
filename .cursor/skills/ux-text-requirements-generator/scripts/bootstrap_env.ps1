$ErrorActionPreference = "Stop"

$skillRoot = Split-Path -Parent $PSScriptRoot
$requirementsPath = Join-Path $skillRoot "requirements.txt"

function Get-PythonCommand {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @("py", "-3")
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @("python")
    }
    return $null
}

$pythonCmd = Get-PythonCommand
if (-not $pythonCmd) {
    Write-Host "Python 3 is not installed." -ForegroundColor Yellow
    Write-Host "Install Python 3 first, then rerun this script." -ForegroundColor Yellow
    Write-Host "Suggested commands:" -ForegroundColor Yellow
    Write-Host "  winget install Python.Python.3.12"
    Write-Host "or download from https://www.python.org/downloads/"
    exit 1
}

Write-Host "Using Python command: $($pythonCmd -join ' ')" -ForegroundColor Cyan

$pythonExe = $pythonCmd[0]
$pythonBaseArgs = @()
if ($pythonCmd.Length -gt 1) {
    $pythonBaseArgs = $pythonCmd[1..($pythonCmd.Length - 1)]
}

& $pythonExe @($pythonBaseArgs + @("-m", "pip", "install", "--upgrade", "pip"))
& $pythonExe @($pythonBaseArgs + @("-m", "pip", "install", "-r", $requirementsPath))

Write-Host ""
Write-Host "Environment bootstrap complete." -ForegroundColor Green
Write-Host "You can now run the skill helper scripts." -ForegroundColor Green
