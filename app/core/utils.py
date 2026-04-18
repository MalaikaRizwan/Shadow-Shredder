from __future__ import annotations

import logging
import os
import platform
import uuid
from datetime import datetime, timezone
from pathlib import Path


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_operation_id() -> str:
    return str(uuid.uuid4())


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_windows() -> bool:
    return platform.system().lower() == "windows"


def safe_unlink(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except Exception:
        logging.exception("Failed to unlink %s", path)


def human_size(size_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size_bytes)
    idx = 0
    while value >= 1024 and idx < len(units) - 1:
        value /= 1024
        idx += 1
    return f"{value:.2f} {units[idx]}"


def get_username_fallback() -> str:
    return os.environ.get("USERNAME") or os.environ.get("USER") or "Unknown Operator"
