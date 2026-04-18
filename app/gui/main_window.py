from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.filesystem_detector import detect_filesystem
from app.core.metadata_mode import build_metadata_mode_config, metadata_mode_summary
from app.core.utils import ensure_dir, get_username_fallback, new_operation_id, utc_now_iso
from app.core.wipe_engine import WipeRequest
from app.gui.dashboard_tab import DashboardTab
from app.gui.forensic_notes_tab import ForensicNotesTab
from app.gui.partition_tab import PartitionTab
from app.gui.reports_tab import ReportsTab
from app.gui.shredder_tab import ShredderTab
from app.gui.styles import APP_QSS
from app.gui.workers import OperationWorker
from app.reporting.report_generator import OperationRecord, ReportGenerator


class MainWindow(QMainWindow):
    def __init__(self, project_root: Path) -> None:
        super().__init__()
        self.project_root = project_root
        self.logs_dir = ensure_dir(project_root / "app" / "logs")
        self.reports_dir = ensure_dir(project_root / "app" / "reports")
        self._setup_logging()
        self.reporter = ReportGenerator(self.reports_dir)
        self.setWindowTitle("ForensiWipe - Forensic Sanitization Workstation")
        self.resize(1200, 800)
        self.setStyleSheet(APP_QSS)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(False)
        self.tabs.setUsesScrollButtons(True)
        self.tabs.setElideMode(Qt.ElideRight)
        self.tabs.setStyleSheet("QTabWidget, QTabWidget::pane, QWidget { background-color: #060b16; }")
        self.dashboard = DashboardTab()
        self.shredder = ShredderTab()
        self.partition = PartitionTab()
        self.reports_tab = ReportsTab(self.reports_dir)
        self.notes_tab = ForensicNotesTab()

        self.tabs.addTab(self.dashboard, "Dashboard")
        self.tabs.addTab(self.shredder, "File / Folder Shredder")
        self.tabs.addTab(self.partition, "Partition / Free Space Wipe")
        self.tabs.addTab(self.reports_tab, "Reports & Logs")
        self.tabs.addTab(self.notes_tab, "Forensic Notes")
        for i in range(self.tabs.count()):
            tab_widget = self.tabs.widget(i)
            tab_widget.setAttribute(Qt.WA_StyledBackground, True)

        self.progress = QProgressBar()
        self.status_console = QPlainTextEdit()
        self.status_console.setReadOnly(True)
        self.banner = QLabel("For authorized and lawful use only. Demo Safe Mode recommended for classroom.")
        self.live_feed_toggle = QPushButton("Hide Live Feed")
        self.live_feed_toggle.setCheckable(True)
        self.live_feed_toggle.setChecked(True)
        self.live_feed_toggle.clicked.connect(self._toggle_live_feed)

        banner_row = QWidget()
        banner_layout = QHBoxLayout(banner_row)
        banner_layout.setContentsMargins(0, 0, 0, 0)
        banner_layout.addWidget(self.banner, 1)
        banner_layout.addWidget(self.live_feed_toggle, 0)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(banner_row)
        layout.addWidget(self.tabs)
        layout.addWidget(self.progress)
        layout.addWidget(self.status_console)
        self.setCentralWidget(central)

        self.shredder.start_btn.clicked.connect(self.start_shredder_operation)
        self.partition.start_btn.clicked.connect(self.start_partition_operation)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self._append("Startup disclaimer acknowledged in GUI.")

    def _on_tab_changed(self, index: int) -> None:
        if self.tabs.tabText(index) == "Dashboard":
            self.dashboard.refresh_drives()

    def _setup_logging(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            handlers=[
                logging.FileHandler(self.logs_dir / "app.log", encoding="utf-8"),
                logging.FileHandler(self.logs_dir / "errors.log", encoding="utf-8"),
            ],
        )

    def _toggle_live_feed(self, visible: bool) -> None:
        self.status_console.setVisible(visible)
        self.live_feed_toggle.setText("Hide Live Feed" if visible else "Show Live Feed")

    def _append(self, text: str) -> None:
        self.status_console.appendPlainText(text)
        logging.getLogger("forensiwipe.gui").info(text)

    def _run_request(self, request: WipeRequest, operation_name: str) -> None:
        start = utc_now_iso()
        self.thread = QThread(self)
        self.worker = OperationWorker(request)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._on_progress)
        self.worker.done.connect(lambda payload: self._on_done(payload, request, start, operation_name))
        self.worker.failed.connect(self._on_failed)
        self.worker.done.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.start()
        self._append(f"Started operation {operation_name} on {request.target_path}")

    def _on_progress(self, current: int, total: int, msg: str) -> None:
        pct = int((current / total) * 100) if total else 0
        self.progress.setValue(max(0, min(100, pct)))
        self._append(f"{pct}% - {msg}")

    def _on_done(self, payload: dict, request: WipeRequest, start: str, operation_name: str) -> None:
        self._append(f"Completed: {payload.get('verification')} | errors={len(payload.get('errors', []))}")
        record = OperationRecord(
            operation_id=new_operation_id(),
            case_id="CASE-DEMO-001",
            operator=get_username_fallback(),
            started_at=start,
            ended_at=utc_now_iso(),
            target=request.target_path,
            target_type=request.target_type,
            filesystem=detect_filesystem(Path(request.target_path)),
            method=request.method_name,
            passes=request.passes,
            bytes_processed=int(payload.get("bytes_processed", 0)),
            status="success" if payload.get("success") else "failed",
            verification=str(payload.get("verification", "unknown")),
            warnings=payload.get("warnings", []),
            forensic_notes=payload.get("forensic_notes", []),
            errors=payload.get("errors", []),
            metadata_mode=str(payload.get("metadata", {}).get("metadata_mode", "Enhanced")),
            metadata_actions=payload.get("metadata", {}).get("metadata_actions", {}),
            metadata_summary=str(payload.get("metadata", {}).get("metadata_summary", "")),
        )
        outputs = self.reporter.save_reports(record)
        self.dashboard.add_recent(f"{record.status} | {record.target_type} | {record.target}")
        self.reports_tab.refresh()
        self._append(f"Reports generated: {outputs}")
        QMessageBox.information(self, "Operation complete", f"{operation_name} complete.\nStatus: {record.status}")

    def _on_failed(self, error_text: str) -> None:
        self._append(error_text)
        QMessageBox.critical(self, "Operation failed", error_text)

    def start_shredder_operation(self) -> None:
        target = self.shredder.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Missing target", "Select a file or folder.")
            return
        req = WipeRequest(
            target_path=target,
            target_type=self.shredder.target_type(),
            method_name=self.shredder.method_combo.currentText(),
            passes=self.shredder.passes_spin.value(),
            chunk_size=self.shredder.chunk_spin.value(),
            verify=self.shredder.verify_box.isChecked(),
            dry_run=self.shredder.dry_run_box.isChecked(),
            demo_safe_mode=self.shredder.demo_safe_box.isChecked(),
            custom_byte_value=self.shredder.custom_byte_spin.value(),
            secure_rename_rounds=self.shredder.rename_rounds.value(),
            quick_mode=self.shredder.quick_mode.isChecked(),
            hash_before=self.shredder.hash_before.isChecked(),
            metadata_mode=self.shredder.metadata_mode_combo.currentText(),
            metadata_actions=build_metadata_mode_config(
                self.shredder.metadata_mode_combo.currentText(),
                {
                    "rename_rounds": self.shredder.rename_rounds.value(),
                    "hash_before": self.shredder.hash_before.isChecked(),
                },
            ),
        )
        self._append(metadata_mode_summary(req.metadata_mode))
        self._run_request(req, "File/Folder Shred")

    def start_partition_operation(self) -> None:
        item = self.partition.drive_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No drive selected", "Select a drive from list.")
            return
        if self.partition.confirm_text.text().strip() != "WIPE":
            QMessageBox.warning(self, "Confirmation required", "Type WIPE to proceed.")
            return
        mount = item.text().split("|")[0]
        mode = self.partition.mode_combo.currentText()
        target_type = "free-space" if "Free-space" in mode else "partition"
        if target_type == "partition":
            QMessageBox.warning(
                self,
                "Safety constraint",
                "Raw full partition wiping is intentionally constrained in this academic build. "
                "Use Dry Run or Free-space wipe mode for safe demonstration.",
            )
            return
        req = WipeRequest(
            target_path=mount,
            target_type=target_type,
            method_name=self.partition.method_combo.currentText(),
            passes=self.partition.passes_spin.value(),
            chunk_size=self.partition.chunk_spin.value(),
            verify=False,
            dry_run=self.partition.dry_run_box.isChecked(),
            demo_safe_mode=self.partition.demo_safe_box.isChecked(),
            quick_mode="Quick forensic wipe mode" in mode,
            metadata_mode=self.partition.metadata_mode_combo.currentText(),
            metadata_actions=build_metadata_mode_config(
                self.partition.metadata_mode_combo.currentText(),
                {"rename_rounds": 0},
            ),
        )
        self._append("Typed confirmation validated for partition/free-space action.")
        self._append(metadata_mode_summary(req.metadata_mode))
        self._run_request(req, "Partition/Free-space Wipe")
