from __future__ import annotations

import hashlib
from pathlib import Path


class Verifier:
    @staticmethod
    def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def path_deleted(path: Path) -> bool:
        return not path.exists()
