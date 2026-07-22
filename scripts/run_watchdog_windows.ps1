param(
    [switch]$Once,
    [switch]$Headless
)

$ErrorActionPreference = "Stop"
$Watchdog = Join-Path $env:LOCALAPPDATA "AlwaysTrack\Watchdog-dev\.venv\Scripts\watchdog.exe"

if (-not (Test-Path $Watchdog)) {
    throw "Watchdog development environment not found at $Watchdog"
}

$Arguments = @(
    "--activity-title", "Menções",
    "--activity-control-type", "List",
    "--item-control-type", "ListItem",
    "--direct-item-automation-id-prefix", "at_user-",
    "--group-item-automation-id-prefix", "at_user_group-",
    "--item-name-as-body"
)

if ($Once) {
    $Arguments += "--once"
    & $Watchdog @Arguments
    exit $LASTEXITCODE
}

if ($Headless) {
    $Arguments += "--headless"
}

$Process = Start-Process -FilePath $Watchdog -ArgumentList $Arguments -PassThru
Write-Output "AlwaysTrack Watchdog started with process id $($Process.Id)."
