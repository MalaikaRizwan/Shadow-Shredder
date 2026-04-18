from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ReportsTab(QWidget):
    def __init__(self, reports_dir: Path) -> None:
        super().__init__()
        self.reports_dir = reports_dir
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter reports...")
        self.report_list = QListWidget()
        self.refresh_btn = QPushButton("Refresh")
        self.open_btn = QPushButton("Open Selected")
        self.export_btn = QPushButton("Open Reports Folder")
        self._build_ui()
        self.refresh()

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

        self.filter_input.setMaximumWidth(760)
        self.refresh_btn.setMaximumWidth(240)
        self.open_btn.setMaximumWidth(280)
        self.export_btn.setMaximumWidth(320)
        self.report_list.setMinimumHeight(300)

        controls_box = QGroupBox("Report Controls")
        controls_layout = QGridLayout(controls_box)
        controls_layout.setContentsMargins(15, 15, 15, 15)
        controls_layout.setSpacing(12)
        controls_layout.setColumnStretch(0, 1)
        controls_layout.setColumnStretch(1, 3)
        controls_layout.addWidget(QLabel("Filter"), 0, 0)
        controls_layout.addWidget(self.filter_input, 0, 1)

        list_box = QGroupBox("Generated Reports")
        list_layout = QVBoxLayout(list_box)
        list_layout.setContentsMargins(15, 15, 15, 15)
        list_layout.setSpacing(12)
        list_layout.addWidget(self.report_list)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)
        row.addStretch(1)
        row.addWidget(self.refresh_btn)
        row.addWidget(self.open_btn)
        row.addWidget(self.export_btn)
        row.addStretch(1)

        content.addWidget(controls_box)
        content.addWidget(list_box)
        content.addLayout(row)
        self.refresh_btn.clicked.connect(self.refresh)
        self.open_btn.clicked.connect(self.open_selected)
        self.export_btn.clicked.connect(self.open_folder)
        self.filter_input.textChanged.connect(self.refresh)

    def refresh(self) -> None:
        self.report_list.clear()
        needle = self.filter_input.text().strip().lower()
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        for p in sorted(self.reports_dir.glob("*.*"), reverse=True):
            if needle and needle not in p.name.lower():
                continue
            self.report_list.addItem(str(p))

    def open_selected(self) -> None:
        item = self.report_list.currentItem()
        if not item:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(item.text()))

    def open_folder(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.reports_dir)))
