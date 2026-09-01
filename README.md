# NSGTA NSPD to NSP Repack Tool

Convert an unpacked NSPD directory directly to an installable NSP, no base template required, Program romfs is left empty.

## How it works

1. Extract `program0.ncd\code`, `program0.ncd\logo`, and `control0.ncd\data` from the NSPD.
2. Create a fresh working directory structure:
   - `program/exefs/` ← NSPD code
   - `program/romfs/` ← **empty** (no base romfs retained)
   - `program/section2_pfs0/` ← NSPD logo (optional)
   - `control/romfs/` ← NSPD control data (optional)
3. Regenerate Program / Control / Meta NCAs using `hacpack` + `prod.keys`.
4. Pack into a single NSP and verify with `hactool`.
5. Output `manifest.json` with run information.

No base unpacked template is needed anymore. Program RomFS is left empty. If your game requires specific RomFS assets, mount them via LayeredFS or a mod.

## Project Structure

```
RepackWorkflow/
├── Tools/                       # External tools (hacpack, hactool, prod.keys)
│   ├── hacpack-v1.36_r2_GUI/
│   ├── keys 21.2.0/
│   └── hactool.exe
├── src/
│   ├── __init__.py              # Package marker
│   ├── repack.py                # Core repacking logic (cross-platform Python)
│   └── gui.py                   # Tkinter GUI (cross-platform)
├── scripts/
│   └── Repack-FromNspdCode.ps1  # Windows PowerShell version (fallback)
├── nsp_repack_gui.py            # Entry point shim (backward compatible)
├── Drag-NSPD-Here.cmd           # Windows drag-and-drop entry
├── build_exe.ps1                # PyInstaller build script
├── pyproject.toml               # Python package definition
├── requirements.txt             # Dependencies (only pyinstaller)
├── .gitignore                   # Ignore runtime outputs
├── README.md                    # This file
└── USAGE_EN.md                  # (legacy English usage doc)
```

Runtime outputs:

- `outputs/` — Generated NSP, NCAs, logs, manifest.json per run
- `work/` — Temporary working directory per run

## Usage

### GUI (Recommended)

Run the pre-built `dist/NSPDRepackGUI.exe`, select your unpacked `.nspd` directory, click "Start repack".

### Command Line

```bash
# Cross-platform (Python)
python src/repack.py -NspdPath "path/to/game.nspd"

# Windows (PowerShell fallback)
powershell -ExecutionPolicy Bypass -File scripts\Repack-FromNspdCode.ps1 -NspdPath "path\to\game.nspd"
```

### Drag & Drop (Windows)

Drag the `.nspd` folder onto `Drag-NSPD-Here.cmd`.

## Build EXE

```powershell
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```

All required external tools (hacpack, hactool, prod.keys) are already included under `Tools/` in this repository. No extra setup needed.

## Cross-Platform Notes

- Core logic (`src/repack.py`) is pure Python with `pathlib`, works on Windows / Linux / macOS.
- GUI (`src/gui.py`) uses Tkinter, works on all three platforms.
- External tools (hacpack / hactool) are Windows native; Linux/macOS users need to compile or use Wine.
- Can be installed as a system command via `pip install .`: `nspd-repack` (CLI) / `nspd-repack-gui` (GUI).

## Output Structure

```
outputs/<NSPD-name>-<timestamp>/
├── nsp/0100b00b51230000.nsp    ← Final output
├── ncas/*.nca
├── logs/*.log
└── manifest.json
```

## Verification

- NSP is a valid PFS0 containing 3 NCAs
- Program NCA has Content Type `Program` with ExeFS / RomFS / PFS0(Logo) sections
- Control and Meta NCAs can be read by hactool

## Console Note

If it runs on Ryujinx but crashes with `std::abort()` on console, check your LayeredFS config, mod conflicts, and verify the Program ID in the Atmosphere crash report first.