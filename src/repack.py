"""
NSGTA NSPD to NSP Repack - Cross-platform core
Ported from original PowerShell script
"""

import os
import sys
import shutil
import datetime
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import subprocess
import logging

logger = logging.getLogger(__name__)


class Repacker:
    def __init__(
        self,
        nspd_path: Path,
        workflow_root: Path,
        title_id: str = "0100b00b51230000",
        hacpack_path: Optional[Path] = None,
        hactool_path: Optional[Path] = None,
        keys_path: Optional[Path] = None,
        no_verify: bool = False,
        base_unpacked: Optional[Path] = None,  # Kept for compatibility
    ):
        self.nspd_path = nspd_path
        self.workflow_root = workflow_root
        self.title_id = title_id
        self.no_verify = no_verify

        # Auto-resolve paths based on project structure
        # Tools are inside project directory: <project>/Tools/...
        if hacpack_path is None:
            hacpack_path = workflow_root / "Tools" / "hacpack-v1.36_r2_GUI" / "hacpack"
            if not hacpack_path.exists():
                hacpack_path = workflow_root / "Tools" / "hacpack-v1.36_r2_GUI" / "hacpack.exe"

        if hactool_path is None:
            hactool_path = workflow_root / "Tools" / "hactool"
            if not hactool_path.exists():
                hactool_path = workflow_root / "Tools" / "hactool.exe"

        if keys_path is None:
            keys_path = workflow_root / "Tools" / "keys 21.2.0" / "prod.keys"

        self.hacpack_path = hacpack_path.resolve()
        self.hactool_path = hactool_path.resolve()
        self.keys_path = keys_path.resolve()

        self._validate_paths()

    def _validate_paths(self) -> None:
        """Validate required paths and tools"""
        if not self.hacpack_path.exists():
            raise FileNotFoundError(f"hacpack not found: {self.hacpack_path}")
        if not self.hactool_path.exists():
            raise FileNotFoundError(f"hactool not found: {self.hactool_path}")
        if not self.keys_path.exists():
            raise FileNotFoundError(f"prod.keys not found: {self.keys_path}")

    def _resolve_nspd_root(self, path: Path) -> Path:
        """Find the actual .nspd directory containing program0.ncd/code"""
        if not path.exists():
            raise FileNotFoundError(f"NSPD path not found: {path}")
        if not path.is_dir():
            raise ValueError(f"NSPD path must be a directory: {path}")

        direct_code = path / "program0.ncd" / "code"
        if direct_code.exists():
            return path

        children = list(path.glob("*.nspd"))
        valid = [p for p in children if (p / "program0.ncd" / "code").exists()]

        if len(valid) == 1:
            return valid[0]

        if len(valid) == 0:
            raise ValueError(f"Could not find any NSPD directory with program0.ncd/code under: {path}")
        else:
            raise ValueError(f"Found multiple NSPD directories under: {path}")

    @staticmethod
    def _safe_name(name: str) -> str:
        """Replace unsafe filesystem characters"""
        for c in '\\/:*?"<>| ':
            name = name.replace(c, "_")
        return name

    def _logged_run(self, name: str, command: List[str], log_dir: Path) -> None:
        """Run a command and log output to file"""
        log_path = log_dir / f"{name}.log"
        print(f"RUN={name}")
        logger.info(f"Running: {' '.join(command)}")

        with open(log_path, "w", encoding="utf-8", errors="replace") as f:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            if process.stdout is None:
                raise RuntimeError(f"Could not capture output for {name}")

            for line in process.stdout:
                line = line.rstrip()
                print(line)
                f.write(line + "\n")

        exit_code = process.wait()
        if exit_code != 0:
            raise RuntimeError(f"{name} failed with exit code {exit_code}. See {log_path}")

    def run(self) -> Dict[str, Any]:
        """Execute the full repack process"""
        # Resolve NSPD root
        nspd_root = self._resolve_nspd_root(self.nspd_path)
        code_dir = nspd_root / "program0.ncd" / "code"
        logo_src_dir = nspd_root / "program0.ncd" / "logo"
        control_src_dir = nspd_root / "control0.ncd" / "data"

        # Check and warn about missing files, don't fail
        required_code_files = ["main", "main.npdm", "rtld", "sdk", "subsdk0", "subsdk1", "subsdk2", "subsdk3"]
        for fname in required_code_files:
            fpath = code_dir / fname
            if not fpath.exists():
                print(f"WARNING: Optional code file missing (will continue): {fpath}")

        if not logo_src_dir.exists():
            print(f"WARNING: NSPD logo directory missing (will skip logo replacement): {logo_src_dir}")
        if not control_src_dir.exists():
            print(f"WARNING: NSPD control data directory missing (will skip control replacement): {control_src_dir}")

        # Create output directories
        work_root = self.workflow_root / "work"
        output_root = self.workflow_root / "outputs"
        work_root.mkdir(parents=True, exist_ok=True)
        output_root.mkdir(parents=True, exist_ok=True)

        nspd_parent_name = nspd_root.parent.name
        nspd_leaf_name = nspd_root.name
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = self._safe_name(f"{nspd_parent_name}-{nspd_leaf_name}-{stamp}")
        work_dir = work_root / run_name
        output_dir = output_root / run_name
        nca_out = output_dir / "ncas"
        nsp_out = output_dir / "nsp"
        log_out = output_dir / "logs"

        for d in [nca_out, nsp_out, log_out]:
            d.mkdir(parents=True, exist_ok=True)

        print(f"NSPD={nspd_root}")
        print(f"WORK={work_dir}")
        print(f"OUT={output_dir}")

        # Create fresh work directory structure (no base template needed)
        exefs_dir = work_dir / "program" / "exefs"
        romfs_dir = work_dir / "program" / "romfs"
        logo_dir = work_dir / "program" / "section2_pfs0"
        control_romfs_dir = work_dir / "control" / "romfs"
        for d in [exefs_dir, romfs_dir, logo_dir, control_romfs_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Populate ExeFS from NSPD code
        for f in code_dir.iterdir():
            if f.is_file():
                shutil.copy2(f, exefs_dir / f.name)

        src_names = sorted([f.name for f in code_dir.iterdir() if f.is_file()])
        dst_names = sorted([f.name for f in exefs_dir.iterdir() if f.is_file()])
        if src_names != dst_names:
            print("WARNING: ExeFS file list mismatch (will continue).")

        # Populate logo (section2_pfs0) from NSPD if exists
        if logo_src_dir.exists():
            for f in logo_src_dir.iterdir():
                if f.is_file():
                    shutil.copy2(f, logo_dir / f.name)

        src_names_l = sorted([f.name for f in logo_src_dir.iterdir() if f.is_file()]) if logo_src_dir.exists() else []
        dst_names_l = sorted([f.name for f in logo_dir.iterdir() if f.is_file()])
        if src_names_l != dst_names_l:
            print("WARNING: Logo file list mismatch (will continue).")

        # Populate control romfs from NSPD if exists
        if control_src_dir.exists():
            for f in control_src_dir.iterdir():
                if f.is_file():
                    shutil.copy2(f, control_romfs_dir / f.name)

        src_names_c = sorted([f.name for f in control_src_dir.iterdir() if f.is_file()]) if control_src_dir.exists() else []
        dst_names_c = sorted([f.name for f in control_romfs_dir.iterdir() if f.is_file()])
        if src_names_c != dst_names_c:
            print("WARNING: Control romfs file list mismatch (will continue).")

        # Build Program NCA
        self._logged_run(
            "01_program_nca",
            [
                str(self.hacpack_path),
                "-k", str(self.keys_path),
                "-o", str(nca_out),
                "--tempdir", str(output_dir / "temp_program"),
                "--backupdir", str(output_dir / "backup_program"),
                "--type", "nca",
                "--ncatype", "program",
                "--titleid", self.title_id,
                "--keygeneration", "1",
                "--sdkversion", "000C1100",
                "--exefsdir", str(exefs_dir),
                "--romfsdir", str(romfs_dir),
                "--logodir", str(logo_dir),
            ],
            log_out,
        )

        # Build Control NCA
        self._logged_run(
            "02_control_nca",
            [
                str(self.hacpack_path),
                "-k", str(self.keys_path),
                "-o", str(nca_out),
                "--tempdir", str(output_dir / "temp_control"),
                "--backupdir", str(output_dir / "backup_control"),
                "--type", "nca",
                "--ncatype", "control",
                "--titleid", self.title_id,
                "--keygeneration", "1",
                "--sdkversion", "000C1100",
                "--romfsdir", str(control_romfs_dir),
            ],
            log_out,
        )

        # Find NCAs
        ncas = list(nca_out.glob("*.nca"))
        program_nca = sorted(
            [n for n in ncas if n.stat().st_size > 1024 * 1024 and not n.name.endswith(".cnmt.nca")],
            key=lambda n: -n.stat().st_size
        )[0] if any(n for n in ncas if n.stat().st_size > 1024 * 1024 and not n.name.endswith(".cnmt.nca")) else None

        control_nca = sorted(
            [n for n in ncas if n.stat().st_size < 1024 * 1024 and not n.name.endswith(".cnmt.nca")],
            key=lambda n: -n.stat().st_size
        )[0] if any(n for n in ncas if n.stat().st_size < 1024 * 1024 and not n.name.endswith(".cnmt.nca")) else None

        if program_nca is None:
            raise RuntimeError("Program NCA not found after packing.")
        if control_nca is None:
            raise RuntimeError("Control NCA not found after packing.")

        # Build Meta NCA
        self._logged_run(
            "03_meta_nca",
            [
                str(self.hacpack_path),
                "-k", str(self.keys_path),
                "-o", str(nca_out),
                "--tempdir", str(output_dir / "temp_meta"),
                "--backupdir", str(output_dir / "backup_meta"),
                "--type", "nca",
                "--ncatype", "meta",
                "--titletype", "application",
                "--titleid", self.title_id,
                "--titleversion", "00000000",
                "--keygeneration", "1",
                "--sdkversion", "000C1100",
                "--programnca", str(program_nca),
                "--controlnca", str(control_nca),
            ],
            log_out,
        )

        # Pack NSP
        self._logged_run(
            "04_nsp",
            [
                str(self.hacpack_path),
                "-k", str(self.keys_path),
                "-o", str(nsp_out),
                "--tempdir", str(output_dir / "temp_nsp"),
                "--backupdir", str(output_dir / "backup_nsp"),
                "--type", "nsp",
                "--titleid", self.title_id,
                "--ncadir", str(nca_out),
            ],
            log_out,
        )

        nsp_path = nsp_out / f"{self.title_id}.nsp"
        if not nsp_path.exists():
            raise RuntimeError(f"NSP not created: {nsp_path}")

        meta_nca = next((n for n in ncas if n.name.endswith(".cnmt.nca")), None)

        # Verification
        if not self.no_verify:
            self._logged_run(
                "05_verify_nsp_pfs0",
                [
                    str(self.hactool_path),
                    "--disablekeywarns",
                    "-k", str(self.keys_path),
                    "-t", "pfs0",
                    "-i", str(nsp_path),
                ],
                log_out,
            )

            # Verify Program NCA
            program_verify_log = log_out / f"06_verify_program_{program_nca.stem}.log"
            cmd = [
                str(self.hactool_path),
                "--disablekeywarns",
                "-k", str(self.keys_path),
                "-t", "nca",
                "-i", str(program_nca),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            program_text = result.stdout + result.stderr
            with open(program_verify_log, "w", encoding="utf-8") as f:
                f.write(program_text)

            if "Content Type:" not in program_text or "Program" not in program_text:
                raise RuntimeError("Program NCA verification failed: missing Program content type.")
            if "Partition Type:" not in program_text or "ExeFS" not in program_text:
                raise RuntimeError("Program NCA verification failed: missing ExeFS section.")
            if "Partition Type:" not in program_text or "RomFS" not in program_text:
                raise RuntimeError("Program NCA verification failed: missing RomFS section.")
            if "Partition Type:" not in program_text or "PFS0" not in program_text:
                raise RuntimeError("Program NCA verification failed: missing Logo/PFS0 section.")

            # Verify Control and Meta NCAs
            for nca in [control_nca, meta_nca]:
                if nca is None:
                    continue
                verify_log = log_out / f"06_verify_{nca.stem}.log"
                result = subprocess.run(
                    [
                        str(self.hactool_path),
                        "--disablekeywarns",
                        "-k", str(self.keys_path),
                        "-t", "nca",
                        "-i", str(nca),
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                with open(verify_log, "w", encoding="utf-8") as f:
                    f.write(result.stdout + result.stderr)
                if result.returncode != 0:
                    raise RuntimeError(f"NCA verification failed for {nca.name}. See {verify_log}")

        # Write manifest
        manifest: Dict[str, Any] = {
            "method": "nspd-direct",
            "createdAt": datetime.datetime.now().isoformat(),
            "titleId": self.title_id,
            "nspdRoot": str(nspd_root),
            "sourceCodeDir": str(code_dir),
            "sourceLogoDir": str(logo_src_dir),
            "sourceControlDir": str(control_src_dir),
            "workDir": str(work_dir),
            "outputDir": str(output_dir),
            "nspPath": str(nsp_path),
            "programNca": str(program_nca),
            "controlNca": str(control_nca),
            "metaNca": str(meta_nca) if meta_nca else None,
        }

        manifest_path = output_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        print("--- RESULT ---")
        print(f"NSP={nsp_path}")
        print(f"OUT={output_dir}")
        print(f"WORK={work_dir}")
        print(f"MANIFEST={manifest_path}")

        return manifest


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-NspdPath", required=True, help="Path to NSPD directory")
    parser.add_argument("-BaseUnpacked", help="(deprecated, no longer needed)")
    parser.add_argument("-WorkflowRoot", help="Workflow root directory")
    parser.add_argument("-ProjectRoot", help="Project root directory")
    parser.add_argument("-TitleId", default="0100b00b51230000", help="Title ID")
    parser.add_argument("-Hacpack", help="Path to hacpack executable")
    parser.add_argument("-Hactool", help="Path to hactool executable")
    parser.add_argument("-Keys", help="Path to prod.keys")
    parser.add_argument("-NoVerify", action="store_true", help="Skip verification")
    args = parser.parse_args()

    # Auto-resolve workflow root from script location
    script_path = Path(__file__).resolve()
    if args.WorkflowRoot is None:
        args.WorkflowRoot = script_path.parent.parent
    else:
        args.WorkflowRoot = Path(args.WorkflowRoot)

    if args.ProjectRoot is None:
        args.ProjectRoot = args.WorkflowRoot.parent
    else:
        args.ProjectRoot = Path(args.ProjectRoot)

    if args.BaseUnpacked is None:
        args.BaseUnpacked = args.ProjectRoot / "0100b00b51230000(1)_unpacked"
    else:
        args.BaseUnpacked = Path(args.BaseUnpacked)

    if args.Hacpack:
        args.Hacpack = Path(args.Hacpack)

    if args.Hactool:
        args.Hactool = Path(args.Hactool)

    if args.Keys:
        args.Keys = Path(args.Keys)

    nspd_path = Path(args.NspdPath)

    repacker = Repacker(
        nspd_path=nspd_path,
        workflow_root=args.WorkflowRoot,
        title_id=args.TitleId,
        hacpack_path=args.Hacpack,
        hactool_path=args.Hactool,
        keys_path=args.Keys,
        no_verify=args.NoVerify,
    )

    try:
        repacker.run()
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
