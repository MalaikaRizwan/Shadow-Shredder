from __future__ import annotations

import platform
import shutil
from dataclasses import dataclass, asdict
from pathlib import Path

import psutil

from app.core.filesystem_detector import detect_filesystem


@dataclass
class DriveInfo:
    mount_point: str
    device: str
    filesystem: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    kind: str
    likely_system: bool

    def to_dict(self) -> dict:
        return asdict(self)


class PartitionWiper:
    def list_drives(self) -> list[DriveInfo]:
        drives: list[DriveInfo] = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = shutil.disk_usage(part.mountpoint)
            except OSError:
                continue
            likely_system = self._is_system_drive(part.mountpoint)
            kind = "removable" if "removable" in part.opts.lower() else "fixed"
            drives.append(
                DriveInfo(
                    mount_point=part.mountpoint,
                    device=part.device,
                    filesystem=part.fstype or detect_filesystem(Path(part.mountpoint)),
                    total_bytes=usage.total,
                    used_bytes=usage.used,
                    free_bytes=usage.free,
                    kind=kind,
                    likely_system=likely_system,
                )
            )
        return drives

    def _is_system_drive(self, mount_point: str) -> bool:
        if platform.system().lower() == "windows":
            return mount_point.lower().startswith("c:")
        return mount_point == "/"
