from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.core.metadata_mode import METADATA_MODES, metadata_mode_hint
from app.core.partition_wiper import PartitionWiper


class PartitionTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.drive_list = QListWidget()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Full partition wipe", "Free-space wipe only", "Quick forensic wipe mode"])
        self.method_combo = QComboBox()
        self.method_combo.addItems(
            ["NULL_0x00", "ONES_0xFF", "RANDOM", "ALT_AA_55", "XOR_FAST", "BIT_INVERSION", "BIT_ROTATION"]
        )
        self.passes_spin = QSpinBox()
        self.passes_spin.setRange(1, 10)
        self.passes_spin.setValue(1)
        self.chunk_spin = QSpinBox()
        self.chunk_spin.setRange(1024, 4 * 1024 * 1024)
        self.chunk_spin.setValue(1024 * 1024)
        self.dry_run_box = QCheckBox("Dry Run")
        self.dry_run_box.setChecked(True)
        self.demo_safe_box = QCheckBox("Demo Safe Mode")
        self.demo_safe_box.setChecked(True)
        self.confirm_text = QLineEdit()
        self.confirm_text.setPlaceholderText("Type WIPE to confirm partition action")
        self.metadata_mode_combo = QComboBox()
        self.metadata_mode_combo.addItems(METADATA_MODES)
        self.metadata_mode_combo.setCurrentText("Enhanced")
        self.metadata_mode_combo.setToolTip("Controls how metadata is minimized during deletion.")
        self.metadata_mode_help = QLabel("Controls how metadata is minimized during deletion.")
        self.metadata_mode_help.setObjectName("Muted")
        self.metadata_mode_help.setWordWrap(True)
        self.metadata_mode_status = QLabel("")
        self.metadata_mode_status.setObjectName("Muted")
        self.metadata_mode_status.setWordWrap(True)
        self.warning = QLabel("WARNING: Partition actions are destructive. Authorized use only.")
        self.start_btn = QPushButton("Start Partition/Free-space Operation")
        self.refresh_btn = QPushButton("Refresh Drives")
        self._build_ui()
        self.refresh_drives()

    def _build_ui(self) -> None:
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

        scroll.setWidget(container)
        layout.addWidget(scroll)

        self.warning.setWordWrap(True)
        self.mode_combo.setMaximumWidth(760)
        self.metadata_mode_combo.setMaximumWidth(760)
        self.method_combo.setMaximumWidth(760)
        self.passes_spin.setMaximumWidth(240)
        self.chunk_spin.setMaximumWidth(320)
        self.confirm_text.setMaximumWidth(760)
        self.drive_list.setMinimumHeight(220)

        drives_box = QGroupBox("Drive Selection")
        drives_layout = QVBoxLayout(drives_box)
        drives_layout.setContentsMargins(15, 15, 15, 15)
        drives_layout.setSpacing(12)
        drives_layout.addWidget(self.warning)
        drives_layout.addWidget(self.drive_list)

        settings = QGroupBox("Partition Wipe Settings")
        form = QGridLayout(settings)
        form.setContentsMargins(15, 15, 15, 15)
        form.setSpacing(12)
        form.setColumnStretch(0, 1)
        form.setColumnStretch(1, 3)
        form.addWidget(QLabel("Metadata Handling Mode"), 0, 0)
        form.addWidget(self.metadata_mode_combo, 0, 1)
        form.addWidget(self.metadata_mode_help, 1, 1)
        form.addWidget(self.metadata_mode_status, 2, 1)
        form.addWidget(QLabel("Mode"), 3, 0)
        form.addWidget(self.mode_combo, 3, 1)
        form.addWidget(QLabel("Method"), 4, 0)
        form.addWidget(self.method_combo, 4, 1)
        form.addWidget(QLabel("Passes"), 5, 0)
        form.addWidget(self.passes_spin, 5, 1)
        form.addWidget(QLabel("Chunk size"), 6, 0)
        form.addWidget(self.chunk_spin, 6, 1)
        form.addWidget(self.dry_run_box, 7, 1)
        form.addWidget(self.demo_safe_box, 8, 1)
        form.addWidget(QLabel("Typed Confirmation"), 9, 0)
        form.addWidget(self.confirm_text, 9, 1)

        self.refresh_btn.setMaximumWidth(320)
        self.start_btn.setMaximumWidth(540)

        content.addWidget(drives_box)
        content.addWidget(settings)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(12)
        actions.addStretch(1)
        actions.addWidget(self.refresh_btn)
        actions.addWidget(self.start_btn)
        actions.addStretch(1)
        content.addLayout(actions)
        self.refresh_btn.clicked.connect(self.refresh_drives)
        self.metadata_mode_combo.currentTextChanged.connect(self._refresh_metadata_mode_hint)
        self._refresh_metadata_mode_hint()

    def _refresh_metadata_mode_hint(self) -> None:
        self.metadata_mode_status.setText(metadata_mode_hint(self.metadata_mode_combo.currentText()))

    def refresh_drives(self) -> None:
        self.drive_list.clear()
        for d in PartitionWiper().list_drives():
            tag = " [SYSTEM DRIVE]" if d.likely_system else ""
            self.drive_list.addItem(f"{d.mount_point}|{d.filesystem}|free={d.free_bytes}{tag}")
