from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from pathlib import Path

from app.core.filesystem_detector import detect_filesystem


@dataclass
class TargetAnalysis:
    path: str
    exists: bool
    target_type: str
    size_bytes: int
    extension: str
    last_modified: float
    filesystem: str
    files_count: int = 0
    folders_count: int = 0
    hidden_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


class Analyzer:
    def analyze_path(self, target_path: Path) -> TargetAnalysis:
        exists = target_path.exists()
        target_type = "missing"
        size = 0
        extension = target_path.suffix.lower()
        last_modified = 0.0
        files_count = 0
        folders_count = 0
        hidden_count = 0

        if exists and target_path.is_file():
            target_type = "file"
            size = target_path.stat().st_size
            last_modified = target_path.stat().st_mtime
            hidden_count = 1 if self._is_hidden(target_path) else 0
        elif exists and target_path.is_dir():
            target_type = "folder"
            for root, dirs, files in os.walk(target_path):
                folders_count += len(dirs)
                files_count += len(files)
                for name in files:
                    fp = Path(root) / name
                    try:
                        size += fp.stat().st_size
                        if self._is_hidden(fp):
                            hidden_count += 1
                    except OSError:
                        continue
        filesystem = detect_filesystem(target_path)
        return TargetAnalysis(
            path=str(target_path),
            exists=exists,
            target_type=target_type,
            size_bytes=size,
            extension=extension,
            last_modified=last_modified,
            filesystem=filesystem,
            files_count=files_count,
            folders_count=folders_count,
            hidden_count=hidden_count,
        )

    def _is_hidden(self, path: Path) -> bool:
        return path.name.startswith(".")
