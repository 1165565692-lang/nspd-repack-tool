# NSGTA NSPD to NSP Repack Tool

Convert an unpacked NSPD directory to an installable NSP. Program romfs is pre-populated from a working base NSP — included in the project so no extra setup is required.

## How it works

1. Extract `program0.ncd\code`, `program0.ncd\logo`, and `control0.ncd\data` from the NSPD.
2. Create a fresh working directory structure:
   - `program/exefs/` ← NSPD code
   - `program/romfs/` ← **pre-populated from `Tools/romfs_base/`** (extracted from a working NSP)
   - `program/section2_pfs0/` ← NSPD logo (optional)
   - `control/romfs/` ← NSPD control data (optional)
3. Regenerate Program / Control / Meta NCAs using `hacpack` + `prod.keys`.
4. Pack into a single NSP and verify with `hactool`.
5. Output `manifest.json` with run information.

No external base template is needed. The romfs skeleton is already bundled under `Tools/romfs_base/`.

## Project Structure

```
RepackWorkflow/
├── Tools/                       # External tools + bundled romfs
│   ├── hacpack-v1.36_r2_GUI/
│   │   └── hacpack.exe
│   ├── keys 21.2.0/
│   │   └── prod.keys
│   ├── hactool.exe
│   └── romfs_base/              # RomFS extracted from a working NSP
│       ├── common.rpf
│       ├── switch/
│       │   ├── switcha.rpf ... switchw.rpf
│       │   └── audio/
│       └── update/
│           ├── update.rpf
│           └── update2.rpf
├── src/
│   ├── __init__.py
│   ├── repack.py                # Core repacking logic (cross-platform Python)
│   └── gui.py                   # Tkinter GUI (cross-platform)
├── scripts/
│   └── Repack-FromNspdCode.ps1  # Windows PowerShell fallback
├── nsp_repack_gui.py            # Entry point shim
├── Drag-NSPD-Here.cmd           # Windows drag-and-drop
├── build_exe.ps1                # PyInstaller build script
├── pyproject.toml
├── requirements.txt
├── .gitignore
└── README.md
```

Runtime outputs:

- `outputs/` — Generated NSP, NCAs, logs, and manifest.json per run
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

All required tools (hacpack, hactool, prod.keys, and romfs_base) are included under `Tools/`. No extra setup needed.

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