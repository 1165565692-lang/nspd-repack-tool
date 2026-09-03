"""
NSPD to NSP Repack - Cross-platform GUI
"""

import os
import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional

VERSION = "1.2"


def _get_app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _get_resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "embedded"  # type: ignore[attr-defined]
    return _get_app_dir().parent


def _get_script_path() -> Path:
    app_dir = _get_app_dir()
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "embedded" / "scripts" / "Repack-FromNspdCode.ps1"  # type: ignore[attr-defined]
    return app_dir / "scripts" / "Repack-FromNspdCode.ps1"


def _get_repack_py() -> Path:
    app_dir = _get_app_dir()
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "embedded" / "src" / "repack.py"  # type: ignore[attr-defined]
    return app_dir / "src" / "repack.py"


APP_DIR = _get_app_dir()
FROZEN = getattr(sys, "frozen", False)
RESOURCE_ROOT = _get_resource_root()
SCRIPT = _get_script_path()
REPACK_PY = _get_repack_py()

if FROZEN:
    HACPACK_PATH = RESOURCE_ROOT / "Tools" / "hacpack.exe"
    HACTOOL_PATH = RESOURCE_ROOT / "Tools" / "hactool.exe"
    KEYS_PATH = RESOURCE_ROOT / "Tools" / "prod.keys"
    ROMFS_BASE_PATH = RESOURCE_ROOT / "Tools" / "romfs_base"
else:
    HACPACK_PATH = APP_DIR / "Tools" / "hacpack-v1.36_r2_GUI" / "hacpack.exe"
    HACTOOL_PATH = APP_DIR / "Tools" / "hactool.exe"
    KEYS_PATH = APP_DIR / "Tools" / "keys 21.2.0" / "prod.keys"
    ROMFS_BASE_PATH = APP_DIR / "Tools" / "romfs_base"


def project_root() -> Path:
    return APP_DIR.parent


class RepackApp(tk.Tk):
    def __init__(self, initial_path: Optional[str] = None):
        super().__init__()
        self.title(f"NSPD to NSP Repack Tool v{VERSION}")
        self.geometry("760x520")
        self.minsize(680, 440)
        self.configure(bg="#f5f6f8")
        self.path_var = tk.StringVar(value=initial_path or "")
        self.status_var = tk.StringVar(value="Select an extracted .nspd folder")
        self.output_path: Optional[Path] = None
        self.events: queue.Queue[tuple[str, str]] = queue.Queue()
        self.worker: Optional[threading.Thread] = None
        self._build_ui()
        self.after(100, self._poll_events)

    def _build_ui(self):
        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 17, "bold"))
        style.configure("Hint.TLabel", foreground="#596273")
        style.configure("Accent.TButton", font=("Microsoft YaHei UI", 10, "bold"))

        outer = ttk.Frame(self, padding=24)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text=f"Repack NSPD to NSP  v{VERSION}", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text="Select an extracted .nspd folder. The tools will create an installable NSP.",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(6, 18))

        path_box = ttk.LabelFrame(outer, text=" NSPD folder ", padding=12)
        path_box.pack(fill="x")
        row = ttk.Frame(path_box)
        row.pack(fill="x")
        self.path_entry = ttk.Entry(row, textvariable=self.path_var)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.browse_button = ttk.Button(row, text="Browse...", command=self.choose_folder)
        self.browse_button.pack(side="right")
        ttk.Label(path_box, text="You can also drop a folder onto the EXE to launch it.", style="Hint.TLabel").pack(anchor="w", pady=(8, 0))

        action_row = ttk.Frame(outer)
        action_row.pack(fill="x", pady=(16, 10))
        self.pack_button = ttk.Button(action_row, text="Start repack", style="Accent.TButton", command=self.start_pack)
        self.pack_button.pack(side="left")
        self.open_button = ttk.Button(action_row, text="Open output folder", command=self.open_output, state="disabled")
        self.open_button.pack(side="left", padx=(8, 0))
        ttk.Label(action_row, textvariable=self.status_var, style="Hint.TLabel").pack(side="right")

        log_box = ttk.LabelFrame(outer, text=" Log ", padding=8)
        log_box.pack(fill="both", expand=True)
        self.log = tk.Text(log_box, wrap="word", state="disabled", font=("Consolas", 9), bg="#10151c", fg="#d7e0ea")
        scrollbar = ttk.Scrollbar(log_box, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=scrollbar.set)
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def choose_folder(self):
        selected = filedialog.askdirectory(title="Select extracted NSPD folder")
        if selected:
            self.path_var.set(selected)

    def append_log(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", text.rstrip() + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start_pack(self):
        if self.worker and self.worker.is_alive():
            return
        nspd = Path(self.path_var.get().strip().strip('"'))
        if not nspd.is_dir():
            messagebox.showwarning("Invalid folder", "Please select an existing NSPD folder.")
            return

        if not REPACK_PY.exists() and not SCRIPT.exists():
            messagebox.showerror("Missing file", f"Repack script was not found:\n{REPACK_PY}")
            return

        self.output_path = None
        self.open_button.configure(state="disabled")
        self.pack_button.configure(state="disabled")
        self.browse_button.configure(state="disabled")
        self.status_var.set("Repacking...")
        self.append_log(f"NSPD: {nspd}")
        self.worker = threading.Thread(target=self._run_pack, args=(nspd,), daemon=True)
        self.worker.start()

    def _run_pack(self, nspd: Path):
        try:
            if getattr(sys, "frozen", False):
                # Frozen EXE: import and run Repacker in-process
                # (subprocess would try to run the EXE itself with a .py arg)
                self._run_pack_inprocess(nspd)
            else:
                # Dev mode: spawned subprocess has real python.exe
                if REPACK_PY.exists():
                    self._run_pack_subprocess_python(nspd)
                elif SCRIPT.exists():
                    self._run_pack_subprocess_powershell(nspd)

            self.events.put(("done", "0"))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def _run_pack_inprocess(self, nspd: Path):
        """Run repack directly in the current process (frozen EXE)"""
        from src.repack import Repacker

        # Redirect print output to the log queue
        import io
        old_stdout = sys.stdout
        buf = io.StringIO()

        class TeeIO:
            def __init__(self, evt_queue, *streams):
                self.events = evt_queue
                self.streams = [s for s in streams if s is not None]
            def write(self, text):
                for s in self.streams:
                    s.write(text)
                if text.strip():
                    self.flush()
            def flush(self):
                val = buf.getvalue()
                if val:
                    for line in val.rstrip().splitlines():
                        self.events.put(("log", line.rstrip()))
                    buf.truncate(0)
                    buf.seek(0)

        tee = TeeIO(self.events, sys.stdout, buf)
        sys.stdout = tee

        try:
            repacker = Repacker(
                nspd_path=nspd,
                workflow_root=APP_DIR,
                hacpack_path=HACPACK_PATH,
                hactool_path=HACTOOL_PATH,
                keys_path=KEYS_PATH,
                romfs_base=ROMFS_BASE_PATH,
                no_verify=False,
            )
            repacker.run()
        finally:
            sys.stdout = old_stdout

    def _run_pack_subprocess_python(self, nspd: Path) -> bool:
        """Run repack using Python subprocess (dev mode)"""
        import subprocess as sp

        cmd = [
            sys.executable, str(REPACK_PY),
            "-NspdPath", str(nspd),
            "-Hacpack", str(HACPACK_PATH),
            "-Hactool", str(HACTOOL_PATH),
            "-Keys", str(KEYS_PATH),
            "-WorkflowRoot", str(APP_DIR),
        ]

        creationflags = getattr(sp, "CREATE_NO_WINDOW", 0)
        process = sp.Popen(
            cmd, cwd=str(APP_DIR),
            stdout=sp.PIPE, stderr=sp.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            creationflags=creationflags,
        )
        assert process.stdout is not None
        for line in process.stdout:
            self.events.put(("log", line.rstrip()))
        code = process.wait()
        if code != 0:
            raise RuntimeError(f"Repack subprocess exited with code {code}")

    def _run_pack_subprocess_powershell(self, nspd: Path) -> bool:
        """Fallback: run repack using PowerShell (Windows only)"""
        import subprocess as sp

        cmd = [
            "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(SCRIPT), "-NspdPath", str(nspd),
            "-Hacpack", str(HACPACK_PATH),
            "-Hactool", str(HACTOOL_PATH),
            "-Keys", str(KEYS_PATH),
            "-WorkflowRoot", str(APP_DIR),
        ]

        creationflags = getattr(sp, "CREATE_NO_WINDOW", 0)
        process = sp.Popen(
            cmd, cwd=str(APP_DIR),
            stdout=sp.PIPE, stderr=sp.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            creationflags=creationflags,
        )
        assert process.stdout is not None
        for line in process.stdout:
            self.events.put(("log", line.rstrip()))
        code = process.wait()
        if code != 0:
            raise RuntimeError(f"PowerShell repack exited with code {code}")

    def _poll_events(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "log":
                    self.append_log(value)
                    if value.startswith("NSP="):
                        self.output_path = Path(value[4:].strip()).parent
                elif kind == "done":
                    success = value == "0"
                    self.pack_button.configure(state="normal")
                    self.browse_button.configure(state="normal")
                    self.status_var.set("Completed" if success else "Failed")
                    if success:
                        self.open_button.configure(state="normal")
                        messagebox.showinfo("Completed", "The NSP was created.\nSee the log for the output path.")
                    else:
                        messagebox.showerror("Repack failed", "The repack process returned an error. See the log.")
                elif kind == "error":
                    self.append_log("ERROR: " + value)
                    self.pack_button.configure(state="normal")
                    self.browse_button.configure(state="normal")
                    self.status_var.set("Launch failed")
                    messagebox.showerror("Launch failed", value)
        except queue.Empty:
            pass
        self.after(100, self._poll_events)

    def open_output(self):
        if self.output_path and self.output_path.exists():
            os.startfile(str(self.output_path))


def main():
    initial = sys.argv[1] if len(sys.argv) > 1 else None
    RepackApp(initial).mainloop()


if __name__ == "__main__":
    main()