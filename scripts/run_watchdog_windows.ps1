param(
    [switch]$Once,
    [switch]$Headless
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $env:LOCALAPPDATA "AlwaysTrack\Watchdog-dev\.venv\Scripts\python.exe"
$Watchdog = Join-Path $env:LOCALAPPDATA "AlwaysTrack\Watchdog-dev\.venv\Scripts\watchdog.exe"

if (-not (Test-Path $Watchdog) -or -not (Test-Path $Python)) {
    throw "Watchdog development environment not found at $Watchdog"
}

$SpikeOutput = Join-Path $env:TEMP "watchdog-uia-launcher.json"
try {
    & $Python (Join-Path $ProjectRoot "scripts\inspect_slack_uia.py") `
        --output $SpikeOutput `
        --max-depth 0 `
        --navigate-automation-id activity-inbox
    if ($LASTEXITCODE -ne 0) {
        throw "Slack Activity could not be opened. Confirm that Slack Desktop is running."
    }
}
finally {
    Remove-Item -LiteralPath $SpikeOutput -Force -ErrorAction SilentlyContinue
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
