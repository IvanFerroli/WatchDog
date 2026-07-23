param(
    [Parameter(Mandatory = $true)]
    [string]$InstallerPath,
    [switch]$EnableAutostart,
    [switch]$KeepInstalled
)

$ErrorActionPreference = "Stop"
$InstallerPath = (Resolve-Path $InstallerPath).Path
$InstallRoot = Join-Path $env:LOCALAPPDATA "Programs\AlwaysTrack\Watchdog"
$AppExe = Join-Path $InstallRoot "AlwaysTrackWatchdog.exe"
$DesktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "AlwaysTrack Watchdog.lnk"
$StartMenuShortcut = Join-Path $env:APPDATA `
    "Microsoft\Windows\Start Menu\Programs\AlwaysTrack Watchdog\AlwaysTrack Watchdog.lnk"
$StartupShortcut = Join-Path ([Environment]::GetFolderPath("Startup")) "AlwaysTrack Watchdog.lnk"

function Resolve-Shortcut {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path $Path -PathType Leaf)) {
        throw "Expected shortcut was not created: $Path"
    }
    $Shell = New-Object -ComObject WScript.Shell
    return $Shell.CreateShortcut($Path)
}

function Assert-AppShortcut {
    param([Parameter(Mandatory = $true)][string]$Path)

    $Shortcut = Resolve-Shortcut $Path
    if (-not [string]::Equals($Shortcut.TargetPath, $AppExe, [StringComparison]::OrdinalIgnoreCase)) {
        throw "$Path points to '$($Shortcut.TargetPath)' instead of '$AppExe'."
    }
    if (-not $Shortcut.IconLocation.StartsWith($AppExe, [StringComparison]::OrdinalIgnoreCase)) {
        throw "$Path does not use the packaged AlwaysTrack icon: '$($Shortcut.IconLocation)'."
    }
    if ($Shortcut.TargetPath -match "powershell|wsl|python") {
        throw "$Path depends on a development runtime."
    }
}

$Tasks = if ($EnableAutostart) { "autostart" } else { "" }
$Arguments = @(
    "/VERYSILENT",
    "/SUPPRESSMSGBOXES",
    "/NORESTART",
    "/CLOSEAPPLICATIONS",
    "/TASKS=$Tasks"
)

try {
    $Process = Start-Process -FilePath $InstallerPath -ArgumentList $Arguments -Wait -PassThru
    if ($Process.ExitCode -ne 0) {
        throw "Installer failed with exit code $($Process.ExitCode)."
    }
    if (-not (Test-Path $AppExe -PathType Leaf)) {
        throw "Installed executable was not found at $AppExe."
    }
    $VersionProcess = Start-Process -FilePath $AppExe -ArgumentList "--version" -Wait -PassThru
    if ($VersionProcess.ExitCode -ne 0) {
        throw "Installed executable failed its --version probe with exit code $($VersionProcess.ExitCode)."
    }

    Assert-AppShortcut $DesktopShortcut
    Assert-AppShortcut $StartMenuShortcut
    if ($EnableAutostart) {
        Assert-AppShortcut $StartupShortcut
    }
    elseif (Test-Path $StartupShortcut) {
        throw "Autostart shortcut exists even though the task was not selected."
    }

    Add-Type -AssemblyName System.Drawing
    $Icon = [System.Drawing.Icon]::ExtractAssociatedIcon($AppExe)
    if ($null -eq $Icon) {
        throw "The packaged executable has no extractable AlwaysTrack icon."
    }
    $Icon.Dispose()
    Write-Host "Installer smoke passed: EXE, icon, Desktop, Start Menu and autostart."
}
finally {
    if (-not $KeepInstalled) {
        $Uninstaller = Join-Path $InstallRoot "unins000.exe"
        if (Test-Path $Uninstaller -PathType Leaf) {
            $Uninstall = Start-Process -FilePath $Uninstaller `
                -ArgumentList @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART") `
                -Wait -PassThru
            if ($Uninstall.ExitCode -ne 0) {
                Write-Warning "Uninstaller returned exit code $($Uninstall.ExitCode)."
            }
        }
        foreach ($ShortcutPath in @($DesktopShortcut, $StartMenuShortcut, $StartupShortcut)) {
            if (Test-Path $ShortcutPath) {
                throw "Uninstall left a shortcut behind: $ShortcutPath"
            }
        }
        if (Test-Path $AppExe) {
            throw "Uninstall left the application executable behind: $AppExe"
        }
        Write-Host "Uninstall smoke passed: executable and shortcuts removed."
    }
}
