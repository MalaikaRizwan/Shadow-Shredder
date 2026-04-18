from __future__ import annotations

import os
import random
import string
from pathlib import Path


class MetadataSanitizer:
    """Best-effort user-space metadata minimization helper."""

    @staticmethod
    def secure_rename(path: Path, rounds: int = 2) -> list[str]:
        names = []
        current = path
        for _ in range(rounds):
            rand_name = "".join(random.choices(string.ascii_letters + string.digits, k=16))
            new_path = current.with_name(rand_name)
            if current.suffix:
                new_path = new_path.with_suffix(current.suffix)
            current.rename(new_path)
            names.append(str(new_path))
            current = new_path
        return names

    @staticmethod
    def truncate(path: Path) -> None:
        with path.open("r+b") as f:
            f.truncate(0)

    @staticmethod
    def forensic_notes_for_fs(fs_name: str) -> list[str]:
        fs = (fs_name or "unknown").lower()
        notes = [
            "Best-effort sanitization performed in user-space only.",
            "Absolute forensic irrecoverability cannot be guaranteed.",
            "Residual artifacts may exist in caches, backups, and system journals.",
        ]
        if "ntfs" in fs:
            notes.extend(
                [
                    "NTFS note: MFT records, USN journal, and transactional metadata may persist.",
                    "Renaming and truncation reduce visible references but cannot purge all metadata internals.",
                ]
            )
        elif "fat" in fs:
            notes.extend(
                [
                    "FAT/FAT32 note: directory entries can retain deletion markers.",
                    "Overwrite + rename + deletion sequence minimizes practical recoverability in user-space scope.",
                ]
            )
        else:
            notes.append("Unknown filesystem: conservative artifact warning applied.")
        return notes

    @staticmethod
    def generic_limitations() -> list[str]:
        return [
            "Journaling subsystems may preserve operation traces.",
            "Slack space and unallocated sectors may keep remnants.",
            "Shadow copies / snapshots can retain historical content.",
            "SSD wear leveling and TRIM behavior may bypass deterministic overwrite assumptions.",
            "Locked files and permission boundaries can prevent full sanitization.",
        ]

    @staticmethod
    def can_open_exclusive(path: Path) -> bool:
        try:
            handle = os.open(path, os.O_RDONLY)
            os.close(handle)
            return True
        except OSError:
            return False
