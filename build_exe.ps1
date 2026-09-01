[CmdletBinding()]
param(
    [string]$Python = 'python',
    [switch]$Clean
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$dist = Join-Path $root 'dist'
$build = Join-Path $root 'build'

if ($Clean) {
    Remove-Item -LiteralPath $dist, $build -Recurse -Force -ErrorAction SilentlyContinue
}

# Check PyInstaller
$checkPreference = $ErrorActionPreference
$ErrorActionPreference = 'SilentlyContinue'
& $Python -c "import PyInstaller" 2>$null
$pyinstallerExit = $LASTEXITCODE
$ErrorActionPreference = $checkPreference
if ($pyinstallerExit -ne 0) {
    Write-Host 'PyInstaller not found; installing...'
    & $Python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) { throw 'Could not install PyInstaller.' }
}

# Build EXE (cross-platform: use ; on Windows, : on Unix)
$sep = if ($env:OS -eq 'Windows_NT') { ';' } else { ':' }

& $Python -m PyInstaller `
    --noconfirm --clean --onefile --windowed `
    --name 'NSPDRepackGUI' `
    --add-data "scripts${sep}embedded/scripts" `
    --add-data "src${sep}embedded/src" `
    --add-binary "Tools\hacpack-v1.36_r2_GUI\hacpack.exe${sep}embedded/Tools" `
    --add-binary "Tools\hactool.exe${sep}embedded/Tools" `
    --add-data "Tools\keys 21.2.0\prod.keys${sep}embedded/Tools" `
    --distpath $dist --workpath $build `
    (Join-Path $root 'nsp_repack_gui.py')
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed.' }

Copy-Item -LiteralPath (Join-Path $root 'README.md') -Destination (Join-Path $dist 'NSPDRepackGUI.exe.README.md') -Force
Write-Host "Built: $(Join-Path $dist 'NSPDRepackGUI.exe')"