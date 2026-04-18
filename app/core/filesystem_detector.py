from __future__ import annotations

import os
import platform
from pathlib import Path

import psutil


def detect_filesystem(path: Path) -> str:
    try:
        resolved = path.resolve()
        if platform.system().lower() == "windows":
            drive = resolved.drive.upper()
            for part in psutil.disk_partitions(all=True):
                if part.device.upper().startswith(drive):
                    return part.fstype or "unknown"
            return "unknown"
        best = "unknown"
        best_len = -1
        for part in psutil.disk_partitions(all=True):
            mount = os.path.realpath(part.mountpoint)
            target = os.path.realpath(str(resolved))
            if target.startswith(mount) and len(mount) > best_len:
                best = part.fstype or "unknown"
                best_len = len(mount)
        return best
    except Exception:
        return "unknown"
