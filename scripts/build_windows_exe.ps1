param(
    [switch]$OneFile = $false,
    [string]$Icon = "",
    [string]$Name = "FLL-Sim"
)

$ErrorActionPreference = "Stop"

# Ensure PyInstaller is available
python - << 'PY'
import sys
try:
import PyInstaller  # noqa: F401
except Exception:
sys.exit(1)
PY

if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller not found. Installing..."
    pip install --upgrade pip PyInstaller pyinstaller-hooks-contrib
}

# Build command
$spec = "packaging\fll_sim.spec"
if (Test-Path $spec) {
    Write-Host "Building from spec: $spec"
    pyinstaller $spec
}
else {
    $args = @("--name=$Name", "--windowed")
    if ($OneFile) { $args += "--onefile" }
    if ($Icon -ne "") { $args += "--icon=$Icon" }
    $args += @(
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets"
    )
    $entry = "src\fll_sim\cli.py"
    Write-Host "Building from entry: $entry"
    pyinstaller @args $entry
}

Write-Host "Build complete. See dist\\$Name"
