"""Secure Shredder application entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.gui.main_window import MainWindow


def main() -> int:
    """Launch the Shadow Shredder GUI."""
    app = QApplication(sys.argv)
    app.setApplicationName("Shadow Shredder")
    app.setOrganizationName("Academic Digital Forensics Lab")

    project_root = Path(__file__).resolve().parent
    window = MainWindow(project_root=project_root)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
