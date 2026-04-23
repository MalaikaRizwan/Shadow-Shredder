# Shadow Shredder

Shadow Shredder is a **Digital Forensics-aware Secure Sanitization Tool for Controlled Data Destruction and Artifact Minimization**.  
It provides academic-grade secure deletion workflows for files, folders, and drive free space with transparent forensic limitations.

## Key Features
- Secure deletion for single file and recursive folder targets.
- Free-space wipe workflow for selected volume.
- Multiple wipe methods: `0x00`, `0xFF`, random, alternating, custom byte, XOR, bit inversion, bit rotation.
- Configurable passes, chunk size, verification, secure rename rounds, and optional SHA-256 pre-wipe hash.
- Dry Run / Simulation mode (required safe classroom mode).
- Demo Safe Mode to block unsafe destructive operations.
- Forensic notes for NTFS/FAT awareness with explicit limitations.
- Operation reports: JSON, CSV, HTML, and text summary.
- Logging: app/activity/error streams under `app/logs`.
- PySide6 GUI with dashboard, shredder tab, partition/free-space tab, reports tab, and forensic-notes tab.

## Safety and Ethics
- For authorized and lawful use only.
- This tool does **not** claim guaranteed irrecoverability on modern systems.
- Residual artifacts can persist due to journaling, snapshots, slack space, SSD wear leveling, TRIM, and OS internals.

## Folder Layout
- Entry: `main.py`
- Core logic: `app/core`
- GUI: `app/gui`
- Reporting: `app/reporting`
- Documentation: `docs`
- Tests: `tests`
- Demo samples: `samples`

## Installation
1. Create virtual environment:
   - Windows: `python -m venv .venv && .venv\\Scripts\\activate`
   - Linux: `python -m venv .venv && source .venv/bin/activate`
2. Install dependencies:
   - `pip install -r requirements.txt`

## Run
- `python main.py`

## Platform Compatibility
- Primary: Windows 10/11
- Secondary: Linux (best-effort for non-Windows-specific behavior)

## Troubleshooting
- Permission denied: run with elevated privileges where authorized.
- Locked files: close applications holding file handles.
- Free-space wipe interrupted: re-run cleanup or delete `.forensiwipe_temp.bin` if present.
- GUI fails to start: ensure PySide6 installed and Python version is 3.10+.

## Notes on Assets
- `app/assets/app_icon.png` and `app/assets/banner.png` are placeholders in this package build.
- Replace with real PNG assets for final submission UI polish.
