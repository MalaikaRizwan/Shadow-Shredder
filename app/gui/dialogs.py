from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QLineEdit, QScrollArea, QTextEdit, QVBoxLayout, QWidget


FORENSIC_NOTES = """
Shadow Shredder - Forensic Notes / Artifact Awareness

1) NTFS:
- MFT entries and metadata structures can persist despite content overwrite.
- USN journal and other system artifacts may preserve operation traces.

2) FAT/FAT32:
- Directory entries and deletion markers can retain historical references.

3) General limitations:
- Journaling, caches, snapshots, and shadow copies may keep recoverable traces.
- Slack space and unallocated clusters may retain residuals.
- SSD wear-leveling and TRIM reduce deterministic overwrite guarantees.
- Locked files and privilege boundaries may block complete sanitization.

Legal/Ethical: For authorized and lawful use only.
"""


class TypedConfirmationDialog(QDialog):
    def __init__(self, expected: str, warning: str, parent=None) -> None:
        super().__init__(parent)
        self.expected = expected
        self.setWindowTitle("Destructive Action Confirmation")
        self._entry = QLineEdit()
        self._entry.setPlaceholderText(f"Type '{expected}' to continue")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(warning))
        layout.addWidget(self._entry)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def is_valid(self) -> bool:
        return self._entry.text().strip() == self.expected


class ForensicNotesDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Forensic Notes")
        self.setModal(True)
        self.setMinimumWidth(640)
        self.setMinimumHeight(420)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Review these notes before using the application."))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        notes_box = QTextEdit()
        notes_box.setReadOnly(True)
        notes_box.setPlainText(FORENSIC_NOTES)
        notes_box.setMinimumHeight(280)
        container_layout.addWidget(notes_box)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
