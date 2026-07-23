param(
    [switch]$Once,
    [switch]$Headless
)

$ErrorActionPreference = "Stop"
$Pythonw = Join-Path $env:LOCALAPPDATA "AlwaysTrack\Watchdog-dev\.venv\Scripts\pythonw.exe"

if (-not (Test-Path $Pythonw)) {
    throw "Watchdog development environment not found at $Pythonw"
}

$Arguments = @(
    "-m", "watchdog.application.cli",
    "--activity-title", "Menções",
    "--activity-control-type", "List",
    "--item-control-type", "ListItem",
    "--direct-item-automation-id-prefix", "at_user-",
    "--group-item-automation-id-prefix", "at_user_group-",
    "--item-name-as-body"
)

if ($Once) {
    $Arguments += "--once"
    $Python = Join-Path $env:LOCALAPPDATA "AlwaysTrack\Watchdog-dev\.venv\Scripts\python.exe"
    & $Python @Arguments
    exit $LASTEXITCODE
}

if ($Headless) {
    $Arguments += "--headless"
}

$Process = Start-Process -FilePath $Pythonw -ArgumentList $Arguments -WindowStyle Hidden -PassThru
Write-Output "AlwaysTrack Watchdog started with process id $($Process.Id)."
