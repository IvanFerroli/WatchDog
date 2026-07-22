$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

python -m pip install -e ".[dev]"
python -m ruff check .
python -m ruff format --check .
python -m pytest --cov --cov-report=term-missing
python -m PyInstaller --clean --noconfirm packaging/watchdog.spec

$Compiler = Get-Command iscc -ErrorAction SilentlyContinue
if ($null -ne $Compiler) {
    & $Compiler.Source packaging/installer.iss
} else {
    Write-Warning "Inno Setup não encontrado; executável gerado, instalador pendente."
}

Get-FileHash dist/AlwaysTrackWatchdog/AlwaysTrackWatchdog.exe -Algorithm SHA256
Get-ChildItem dist/installer/*.exe -ErrorAction SilentlyContinue | Get-FileHash -Algorithm SHA256
