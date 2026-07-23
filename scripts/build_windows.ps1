param(
    [switch]$SkipQuality,
    [switch]$SmokeInstaller,
    [switch]$KeepWork
)

$ErrorActionPreference = "Stop"
$SourceRoot = Split-Path -Parent $PSScriptRoot
$BuildRoot = Join-Path $env:TEMP ("AlwaysTrackWatchdog-build-" + [guid]::NewGuid().ToString("N"))
$VenvRoot = Join-Path $BuildRoot ".venv"
$Python = Join-Path $VenvRoot "Scripts\python.exe"
$WorkRoot = Join-Path $BuildRoot "work"
$DistRoot = Join-Path $BuildRoot "dist"
$BundleRoot = Join-Path $DistRoot "AlwaysTrackWatchdog"
$InstallerRoot = Join-Path $DistRoot "installer"
$RepoDistRoot = Join-Path $SourceRoot "dist"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$FilePath failed with exit code $LASTEXITCODE"
    }
}

function Resolve-InnoCompiler {
    $Command = Get-Command iscc -ErrorAction SilentlyContinue
    if ($null -ne $Command) {
        return $Command.Source
    }

    $Candidates = @(
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
        (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe")
    )
    foreach ($Candidate in $Candidates) {
        if ($Candidate -and (Test-Path $Candidate -PathType Leaf)) {
            return $Candidate
        }
    }
    throw "Inno Setup 6 is required to produce the transferable Setup.exe."
}

try {
    New-Item -ItemType Directory -Path $BuildRoot, $WorkRoot, $DistRoot, $InstallerRoot -Force |
        Out-Null

    $BasePython = (Get-Command python -ErrorAction Stop).Source
    Invoke-Checked $BasePython "-c" "import sys; assert sys.version_info[:2] == (3, 12), sys.version"
    Invoke-Checked $BasePython "-m" "venv" $VenvRoot
    Invoke-Checked $Python "-m" "pip" "install" "--disable-pip-version-check" "-e" "$SourceRoot[dev]"

    if (-not $SkipQuality) {
        Push-Location $SourceRoot
        try {
            Invoke-Checked $Python "-m" "ruff" "check" $SourceRoot
            Invoke-Checked $Python "-m" "ruff" "format" "--check" $SourceRoot
            # The coverage threshold is enforced by quality.yml on Linux. Two
            # fail-closed tests are intentionally skipped on Windows, so the
            # native packaging gate runs the complete platform suite itself.
            Invoke-Checked $Python "-m" "pytest" $SourceRoot
        }
        finally {
            Pop-Location
        }
    }

    $Version = (& $Python -c "import watchdog; print(watchdog.__version__)").Trim()
    if ($LASTEXITCODE -ne 0 -or $Version -notmatch "^\d+\.\d+\.\d+(\.\d+)?$") {
        throw "The application version '$Version' is not valid for Windows packaging."
    }

    Invoke-Checked $Python "-m" "PyInstaller" "--clean" "--noconfirm" `
        "--workpath" $WorkRoot "--distpath" $DistRoot `
        (Join-Path $SourceRoot "packaging\watchdog.spec")

    $AppExe = Join-Path $BundleRoot "AlwaysTrackWatchdog.exe"
    if (-not (Test-Path $AppExe -PathType Leaf)) {
        throw "PyInstaller did not produce $AppExe"
    }

    $InnoCompiler = Resolve-InnoCompiler
    $InstallerScript = Join-Path $SourceRoot "packaging\installer.iss"
    Invoke-Checked $InnoCompiler "/DMyAppVersion=$Version" `
        "/DMySourceDir=$BundleRoot" "/DMyOutputDir=$InstallerRoot" $InstallerScript

    $Installer = Join-Path $InstallerRoot "AlwaysTrackWatchdog-$Version-Setup.exe"
    if (-not (Test-Path $Installer -PathType Leaf)) {
        throw "Inno Setup did not produce $Installer"
    }

    $Hash = Get-FileHash $Installer -Algorithm SHA256
    $HashManifest = Join-Path $InstallerRoot "SHA256SUMS.txt"
    "$($Hash.Hash.ToLowerInvariant())  $([IO.Path]::GetFileName($Installer))" |
        Set-Content -Path $HashManifest -Encoding ascii

    if ($SmokeInstaller) {
        & (Join-Path $PSScriptRoot "smoke_installer_windows.ps1") `
            -InstallerPath $Installer -EnableAutostart
        if ($LASTEXITCODE -ne 0) {
            throw "Installer smoke failed with exit code $LASTEXITCODE"
        }
    }

    New-Item -ItemType Directory -Path $RepoDistRoot -Force | Out-Null
    foreach ($Name in @("AlwaysTrackWatchdog", "installer")) {
        $Destination = Join-Path $RepoDistRoot $Name
        if (Test-Path $Destination) {
            Remove-Item -LiteralPath $Destination -Recurse -Force
        }
        Copy-Item -Path (Join-Path $DistRoot $Name) -Destination $Destination -Recurse
    }

    Write-Host ""
    Write-Host "Transferable installer:"
    Write-Host (Join-Path $RepoDistRoot "installer\AlwaysTrackWatchdog-$Version-Setup.exe")
    Get-Content (Join-Path $RepoDistRoot "installer\SHA256SUMS.txt")
}
finally {
    if (-not $KeepWork -and (Test-Path $BuildRoot)) {
        Remove-Item -LiteralPath $BuildRoot -Recurse -Force
    }
    elseif ($KeepWork) {
        Write-Host "Build work retained at $BuildRoot"
    }
}
