# NSPD to NSP Repack Tool

This guide explains how to use `NSPDRepackGUI.exe` to convert an extracted NSPD directory into an installable NSP file.

## What You Need

You only need these two items:

```text
NSPDRepackGUI.exe
your_game.nspd\
```

The EXE already contains the base package, `hacpack`, `hactool`, encryption keys, and the repacking script. Do not copy or modify the internal tools.

The NSPD folder must be an extracted NSPD directory. It should contain folders such as:

```text
program0.ncd\code\
program0.ncd\logo\
control0.ncd\data\
meta0.ncd\data\
```

## Repack an NSPD Folder

1. Double-click `NSPDRepackGUI.exe`.
2. Click `Browse...` and select the extracted `.nspd` folder.
3. Confirm that the selected path points to the folder containing `program0.ncd` and `control0.ncd`.
4. Click `Start repack`.
5. Wait until the status changes to `Completed`.
6. Click `Open output folder`, or open the `outputs` folder next to the EXE.

You can also drag an NSPD folder onto the EXE to open the tool with that folder preselected.

## Output Files

Each run creates a timestamped directory under `outputs`:

```text
outputs\RepackWorkflow-your_game.nspd-YYYYMMDD_HHMMSS\
  nsp\0100b00b51230000.nsp
  ncas\
  logs\
  manifest.json
```

The file you normally need is:

```text
nsp\0100b00b51230000.nsp
```

The `logs` folder contains the command output for each packing stage. `manifest.json` records the source and output paths for that run.

## How the Tool Works

The tool copies the embedded base package to a temporary work directory, then replaces:

- the base ExeFS with `program0.ncd\code` from the selected NSPD;
- the base logo partition with `program0.ncd\logo`;
- the base Control RomFS with `control0.ncd\data`.

The base RomFS is preserved so that the resulting Program NCA retains the required game resource structure. The tool then creates Program, Control, and Meta NCAs, packs them into an NSP, and stores the intermediate files and logs in the run directory.

## Troubleshooting

### `Invalid folder`

Select the actual extracted NSPD directory, not a compressed archive and not a parent folder containing unrelated files. If you select a parent folder, it must contain exactly one `.nspd` subfolder with `program0.ncd\code`.

### Required files are missing

Check that the NSPD contains:

```text
program0.ncd\code\main
program0.ncd\code\main.npdm
program0.ncd\code\rtld
program0.ncd\code\sdk
program0.ncd\code\subsdk0 ... subsdk3
program0.ncd\logo\
control0.ncd\data\
```

### Repack failed

Read the latest log files under `outputs\...\logs`. Common causes include an incomplete NSPD extraction, insufficient free disk space, or a file being locked by another program.

The tool needs temporary space for a copy of the base package and the generated NCAs. Keep at least several hundred megabytes free on the system drive and the drive containing the EXE.

### The EXE starts slowly

The single-file EXE extracts its embedded resources to a temporary directory when it starts. This is expected, especially on the first launch.

## Building the EXE Again

This section is only for developers. Install Python 3.10 or newer, then run PowerShell from the `RepackWorkflow` directory:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1 -Clean
```

The script installs PyInstaller if necessary and creates:

```text
dist\NSPDRepackGUI.exe
```

The build script expects the original project layout, including the base package under the parent `NSGTA` directory and the tools under `NSGTA\Tools`.

## Safety Notes

- The selected NSPD directory is read as input; the tool does not modify it.
- Each run uses a separate timestamped work and output directory.
- Existing output directories are not deleted automatically.
- Only install or test the generated NSP on hardware and software where you have the necessary rights and authorization.
