from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable

from app.core.wipe_methods import WipeMethod

ProgressCb = Callable[[int, int, str], None]


class FreeSpaceWiper:
    def wipe(
        self,
        drive_root: Path,
        method: WipeMethod,
        passes: int,
        chunk_size: int,
        dry_run: bool,
        progress_cb: ProgressCb | None = None,
        cancel_flag: Callable[[], bool] | None = None,
    ) -> tuple[int, list[str]]:
        notes: list[str] = []
        total_written = 0
        marker = drive_root / ".forensiwipe_temp.bin"
        if dry_run:
            free = shutil.disk_usage(drive_root).free
            notes.append(f"[DRY RUN] Would consume up to {free} bytes of free space.")
            if progress_cb:
                progress_cb(free, free, "Dry-run free-space wipe simulation complete")
            return free, notes

        for pass_idx in range(passes):
            free = shutil.disk_usage(drive_root).free
            target = int(free * 0.9)
            written_this_pass = 0
            try:
                with marker.open("wb") as f:
                    while written_this_pass < target:
                        if cancel_flag and cancel_flag():
                            notes.append("Operation cancelled by user; cleaning temp file.")
                            break
                        base = b"\x00" * min(chunk_size, target - written_this_pass)
                        chunk = method.transform(base, pass_idx)
                        f.write(chunk)
                        written_this_pass += len(chunk)
                        total_written += len(chunk)
                        if progress_cb:
                            progress_cb(total_written, target * passes, f"Free-space pass {pass_idx + 1}/{passes}")
            finally:
                marker.unlink(missing_ok=True)
        notes.append("Temporary free-space filler file cleaned.")
        return total_written, notes
