from __future__ import annotations

from typing import Any

METADATA_MODES = ["Basic", "Enhanced", "Forensic-aware"]

_MODE_HINTS = {
    "Basic": "Fast deletion, minimal metadata handling",
    "Enhanced": "Balanced sanitization",
    "Forensic-aware": "Maximum forensic awareness (slower)",
}

_MODE_SUMMARIES = {
    "Basic": "basic sanitization with minimal metadata handling",
    "Enhanced": "balanced sanitization with practical metadata minimization",
    "Forensic-aware": "enhanced sanitization with forensic awareness",
}


def metadata_mode_hint(mode: str) -> str:
    return _MODE_HINTS.get(mode, _MODE_HINTS["Enhanced"])


def metadata_mode_summary(mode: str) -> str:
    summary = _MODE_SUMMARIES.get(mode, _MODE_SUMMARIES["Enhanced"])
    return f"Metadata Handling Mode: {mode} ({summary})"


def build_metadata_mode_config(mode: str, ui_values: dict[str, Any]) -> dict:
    selected = mode if mode in METADATA_MODES else "Enhanced"
    rename_rounds = int(ui_values.get("rename_rounds", 0) or 0)

    if selected == "Basic":
        return {
            "overwrite": True,
            "rename_rounds": 0,
            "truncate": False,
            "sha256_pre_wipe": False,
            "forensic_notes": False,
            "suggest_free_space_wipe": False,
        }
    if selected == "Forensic-aware":
        return {
            "overwrite": True,
            "rename_rounds": rename_rounds,
            "truncate": True,
            "sha256_pre_wipe": True,
            "forensic_notes": True,
            "suggest_free_space_wipe": True,
        }
    return {
        "overwrite": True,
        "rename_rounds": rename_rounds,
        "truncate": True,
        "sha256_pre_wipe": False,
        "forensic_notes": False,
        "suggest_free_space_wipe": False,
    }
