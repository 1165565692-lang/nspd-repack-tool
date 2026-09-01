# NSGTA NSPD 重打包工具

将解压后的 NSPD 目录直接打成 NSP，不再依赖底包模板，Program romfs 为空。

## 原理

1. 从 NSPD 包里取 `program0.ncd\code`、`program0.ncd\logo`、`control0.ncd\data`。
2. 创建全新的工作目录结构：
   - `program/exefs/` ← NSPD code
   - `program/romfs/` ← 空（不保留任何底包数据）
   - `program/section2_pfs0/` ← NSPD logo（可选）
   - `control/romfs/` ← NSPD control data（可选）
3. 用 `hacpack` + `prod.keys` 重新生成 Program / Control / Meta NCA。
4. 封成 NSP，用 `hactool` 校验。
5. 输出 `manifest.json` 记录本次运行信息。

不再需要底包模板，NSP 的 Program RomFS 为空。如果游戏需要特定 RomFS 资源，请通过 LayeredFS 或 Mod 挂载。

## 目录结构

```
RepackWorkflow/
├── src/
│   ├── __init__.py          # 包标记
│   ├── repack.py            # 核心重打包逻辑 (跨平台 Python)
│   └── gui.py               # Tkinter 图形界面 (跨平台)
├── scripts/
│   └── Repack-FromNspdCode.ps1  # Windows PowerShell 版 (备用)
├── nsp_repack_gui.py        # 入口 shim (向后兼容)
├── Drag-NSPD-Here.cmd       # Windows 拖放入口
├── build_exe.ps1            # Windows PyInstaller 构建脚本
├── pyproject.toml           # Python 包定义
├── requirements.txt         # 依赖 (仅 pyinstaller)
├── .gitignore               # 忽略运行产物
├── README.md
└── USAGE_EN.md
```

运行时输出目录：

- `outputs/` — 每次打包生成的 NSP、NCA、日志、manifest.json
- `work/` — 每次打包的临时底包副本

## 使用方法

### 图形界面 (推荐)

运行构建好的 `NSPDRepackGUI.exe`，选择解压后的 `.nspd` 目录，点击 Start repack。

### 命令行

```bash
# 跨平台 (Python)
python src/repack.py -NspdPath "path/to/game.nspd"

# Windows (PowerShell 备用)
powershell -ExecutionPolicy Bypass -File scripts\Repack-FromNspdCode.ps1 -NspdPath "path\to\game.nspd"
```

### 拖放 (Windows)

把 `.nspd` 文件夹拖到 `Drag-NSPD-Here.cmd` 上。

## 构建 EXE

```powershell
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1 -Clean
```

工具 (hacpack/hactool/prod.keys) 需要放在项目上级目录：

```
<ProjectRoot>/
├── RepackWorkflow/
│   └── ...
├── Tools/
│   ├── hacpack-v1.36_r2_GUI/hacpack.exe
│   ├── hactool.exe
│   └── keys 21.2.0/prod.keys
```

## 跨平台说明

- 核心逻辑 (`src/repack.py`) 使用纯 Python + `pathlib`，支持 Windows / Linux / macOS。
- GUI (`src/gui.py`) 使用 Tkinter，三大平台均可运行。
- 外部工具 (hacpack / hactool) 为 Windows 原生程序，Linux/macOS 用户需自行编译或使用 Wine。
- 可通过 `pip install .` 安装为系统命令：`nspd-repack` (命令行) / `nspd-repack-gui` (界面)。

## 输出内容

```
outputs/<NSPD名>-<时间戳>/
├── nsp/0100b00b51230000.nsp    ← 最终产物
├── ncas/*.nca
├── logs/*.log
└── manifest.json
```

## 校验标准

- NSP 是 PFS0，包含 3 个 NCA
- Program NCA Content Type 为 `Program`，包含 ExeFS / RomFS / PFS0(Logo) 三段
- Control 和 Meta NCA 可被 hactool 正常读取

## 实机测试注意

如果 Ryujinx 能跑、实机仍然 `std::abort()`，优先检查 SD 卡上的 LayeredFS 配置、Mod 冲突、以及 Atmosphere crash report 的 Program ID。