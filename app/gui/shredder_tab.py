from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.analyzer import Analyzer
from app.core.metadata_mode import METADATA_MODES, metadata_mode_hint
from app.core.wipe_methods import (
    AlternatingPatternMethod,
    BitInversionMethod,
    BitRotationMethod,
    CustomByteMethod,
    NullBytesMethod,
    OnesBytesMethod,
    RandomBytesMethod,
    XorMethod,
)


class ShredderTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.target_input = QLineEdit()
        self.method_combo = QComboBox()
        for m in [
            NullBytesMethod.name,
            OnesBytesMethod.name,
            RandomBytesMethod.name,
            AlternatingPatternMethod.name,
            CustomByteMethod.name,
            XorMethod.name,
            BitInversionMethod.name,
            BitRotationMethod.name,
        ]:
            self.method_combo.addItem(m)
        self.passes_spin = QSpinBox()
        self.passes_spin.setRange(1, 35)
        self.passes_spin.setValue(2)
        self.chunk_spin = QSpinBox()
        self.chunk_spin.setRange(1024, 4 * 1024 * 1024)
        self.chunk_spin.setValue(1024 * 1024)
        self.custom_byte_spin = QSpinBox()
        self.custom_byte_spin.setRange(0, 255)
        self.verify_box = QCheckBox("Verify deletion")
        self.verify_box.setChecked(True)
        self.dry_run_box = QCheckBox("Dry Run (Simulation)")
        self.dry_run_box.setChecked(True)
        self.demo_safe_box = QCheckBox("Demo Safe Mode")
        self.demo_safe_box.setChecked(True)
        self.rename_rounds = QSpinBox()
        self.rename_rounds.setRange(0, 8)
        self.rename_rounds.setValue(2)
        self.quick_mode = QCheckBox("Quick forensic wipe mode (speed-optimized)")
        self.hash_before = QCheckBox("Compute SHA-256 before wipe")
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
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.start_btn = QPushButton("Start Shred")

        self._build_ui()

    def _build_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(15, 15, 15, 15)
        main.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        container = QWidget()
        content = QVBoxLayout(container)
        content.setContentsMargins(15, 15, 15, 15)
        content.setSpacing(12)

        scroll.setWidget(container)
        main.addWidget(scroll)

        self.target_input.setMaximumWidth(760)
        self.method_combo.setMaximumWidth(760)
        self.metadata_mode_combo.setMaximumWidth(760)
        self.passes_spin.setMaximumWidth(220)
        self.chunk_spin.setMaximumWidth(320)
        self.custom_byte_spin.setMaximumWidth(220)
        self.rename_rounds.setMaximumWidth(220)
        self.preview.setMinimumHeight(220)

        target_box = QGroupBox("Target Selection")
        t_layout = QHBoxLayout(target_box)
        t_layout.setContentsMargins(15, 15, 15, 15)
        t_layout.setSpacing(12)
        t_layout.addWidget(self.target_input)
        file_btn = QPushButton("File")
        folder_btn = QPushButton("Folder")
        file_btn.setMaximumWidth(160)
        folder_btn.setMaximumWidth(160)
        file_btn.clicked.connect(self._pick_file)
        folder_btn.clicked.connect(self._pick_folder)
        t_layout.addWidget(file_btn)
        t_layout.addWidget(folder_btn)

        settings = QGroupBox("Wipe Settings")
        s_layout = QGridLayout(settings)
        s_layout.setContentsMargins(15, 15, 15, 15)
        s_layout.setSpacing(12)
        s_layout.setColumnStretch(0, 1)
        s_layout.setColumnStretch(1, 3)
        s_layout.addWidget(QLabel("Metadata Handling Mode"), 0, 0)
        s_layout.addWidget(self.metadata_mode_combo, 0, 1)
        s_layout.addWidget(self.metadata_mode_help, 1, 1)
        s_layout.addWidget(self.metadata_mode_status, 2, 1)
        s_layout.addWidget(QLabel("Method"), 3, 0)
        s_layout.addWidget(self.method_combo, 3, 1)
        s_layout.addWidget(QLabel("Passes"), 4, 0)
        s_layout.addWidget(self.passes_spin, 4, 1)
        s_layout.addWidget(QLabel("Chunk size (bytes)"), 5, 0)
        s_layout.addWidget(self.chunk_spin, 5, 1)
        s_layout.addWidget(QLabel("Custom byte value"), 6, 0)
        s_layout.addWidget(self.custom_byte_spin, 6, 1)
        s_layout.addWidget(QLabel("Rename rounds"), 7, 0)
        s_layout.addWidget(self.rename_rounds, 7, 1)
        s_layout.addWidget(self.verify_box, 8, 1)
        s_layout.addWidget(self.dry_run_box, 9, 1)
        s_layout.addWidget(self.demo_safe_box, 10, 1)
        s_layout.addWidget(self.quick_mode, 11, 1)
        s_layout.addWidget(self.hash_before, 12, 1)

        preview_box = QGroupBox("Preview")
        p_layout = QVBoxLayout(preview_box)
        p_layout.setContentsMargins(15, 15, 15, 15)
        p_layout.setSpacing(12)
        analyze_btn = QPushButton("Analyze Target")
        analyze_btn.setMaximumWidth(300)
        analyze_btn.clicked.connect(self._analyze)
        p_layout.addWidget(analyze_btn)
        p_layout.addWidget(self.preview)

        self.start_btn.setMaximumWidth(420)

        content.addWidget(target_box)
        content.addWidget(settings)
        content.addWidget(preview_box)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(12)
        action_row.addStretch(1)
        action_row.addWidget(self.start_btn)
        action_row.addStretch(1)
        content.addLayout(action_row)
        self.metadata_mode_combo.currentTextChanged.connect(self._refresh_metadata_mode_hint)
        self._refresh_metadata_mode_hint()

    def _refresh_metadata_mode_hint(self) -> None:
        self.metadata_mode_status.setText(metadata_mode_hint(self.metadata_mode_combo.currentText()))

    def _pick_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path:
            self.target_input.setText(path)

    def _pick_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path:
            self.target_input.setText(path)

    def _analyze(self) -> None:
        path_txt = self.target_input.text().strip()
        if not path_txt:
            self.preview.setPlainText("No target selected.")
            return
        analysis = Analyzer().analyze_path(Path(path_txt)).to_dict()
        lines = [f"{k}: {v}" for k, v in analysis.items()]
        self.preview.setPlainText("\n".join(lines))

    def target_type(self) -> str:
        p = Path(self.target_input.text().strip())
        if p.is_file():
            return "file"
        if p.is_dir():
            return "folder"
        return "file"
