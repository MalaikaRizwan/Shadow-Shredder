from __future__ import annotations

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QScrollArea, QSizePolicy, QTextEdit, QVBoxLayout, QWidget


FORENSIC_NOTES = """
ForensiWipe - Forensic Notes / Artifact Awareness

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


class ForensicNotesTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        box = QTextEdit()
        box.setReadOnly(True)
        box.setPlainText(FORENSIC_NOTES)
        box.setMinimumHeight(320)
        box.setMaximumWidth(860)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        container = QWidget()
        content = QVBoxLayout(container)
        content.setContentsMargins(15, 15, 15, 15)
        content.setSpacing(12)

        notes_box = QGroupBox("Forensic Notes")
        notes_layout = QVBoxLayout(notes_box)
        notes_layout.setContentsMargins(15, 15, 15, 15)
        notes_layout.setSpacing(12)
        notes_layout.addWidget(box)

        content.addWidget(notes_box)
        content.addStretch(1)

        scroll.setWidget(container)
        layout.addWidget(scroll)
