#main_window.py
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from PySide6.QtCore import QThread, Qt, QTimer
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
from app.gui.dialogs import ForensicNotesDialog
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
        self.setWindowTitle("Shadow Shredder - Forensic Sanitization Workstation")
        self.resize(1200, 800)
        self.setStyleSheet(APP_QSS)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(False)
        self.tabs.setUsesScrollButtons(True)
        self.tabs.setElideMode(Qt.ElideRight)
        self.dashboard = DashboardTab()
        self.shredder = ShredderTab()
        self.partition = PartitionTab()
        self.reports_tab = ReportsTab(self.reports_dir)

        self.tabs.addTab(self.dashboard, "Dashboard")
        self.tabs.addTab(self.shredder, "File / Folder Shredder")
        self.tabs.addTab(self.partition, "Partition / Free Space Wipe")
        self.tabs.addTab(self.reports_tab, "Reports & Logs")
        for i in range(self.tabs.count()):
            tab_widget = self.tabs.widget(i)
            tab_widget.setAttribute(Qt.WA_StyledBackground, True)

        self.progress = QProgressBar()
        self.status_console = QPlainTextEdit()
        self.status_console.setReadOnly(True)
        self.banner = QLabel("For authorized and lawful use only. Demo Safe Mode recommended for classroom.")
        self.live_feed_toggle = QPushButton("Show Live Feed")
        self.live_feed_toggle.setCheckable(True)
        self.live_feed_toggle.setChecked(False)
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

        self.thread: QThread | None = None
        self.worker: OperationWorker | None = None
        self._active_request: WipeRequest | None = None
        self._active_operation_name = ""
        self._active_start = ""
        self._forensic_notes_dialog = None
        self._toggle_live_feed(False)
        self._append("Startup disclaimer acknowledged in GUI.")
        QTimer.singleShot(0, self._show_forensic_notes_popup)

    def _on_tab_changed(self, index: int) -> None:
        if self.tabs.tabText(index) == "Dashboard":
            self.dashboard.refresh_drives()

    def _show_forensic_notes_popup(self) -> None:
        self._forensic_notes_dialog = ForensicNotesDialog(self)
        self._forensic_notes_dialog.setAttribute(Qt.WA_DeleteOnClose, True)
        self._forensic_notes_dialog.finished.connect(self._clear_forensic_notes_dialog)
        self._forensic_notes_dialog.open()

    def _clear_forensic_notes_dialog(self) -> None:
        self._forensic_notes_dialog = None

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

    def _set_operation_controls_enabled(self, enabled: bool) -> None:
        self.shredder.start_btn.setEnabled(enabled)
        self.partition.start_btn.setEnabled(enabled)

    def _run_request(self, request: WipeRequest, operation_name: str) -> None:
        if self.thread and self.thread.isRunning():
            QMessageBox.warning(self, "Operation in progress", "Wait for the current operation to finish.")
            return

        start = utc_now_iso()
        self._active_request = request
        self._active_operation_name = operation_name
        self._active_start = start

        self.thread = QThread(self)
        self.worker = OperationWorker(request)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._on_progress)
        self.worker.done.connect(self._on_done)
        self.worker.failed.connect(self._on_failed)
        self.worker.done.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self._on_thread_finished)

        self._set_operation_controls_enabled(False)
        self.thread.start()
        self._append(f"Started operation {operation_name} on {request.target_path}")

    def _on_progress(self, current: int, total: int, msg: str) -> None:
        pct = int((current / total) * 100) if total else 0
        self.progress.setValue(max(0, min(100, pct)))
        self._append(f"{pct}% - {msg}")

    def _on_done(self, payload: dict[str, Any]) -> None:
        request = self._active_request
        operation_name = self._active_operation_name
        start = self._active_start

        if request is None:
            self._append("Internal state error: missing request context for completed operation.")
            self._set_operation_controls_enabled(True)
            return

        self._append(f"Completed: {payload.get('verification')} | errors={len(payload.get('errors', []))}")
        is_dry_run = bool(request.dry_run)
        status = "simulated" if is_dry_run else ("success" if payload.get("success") else "failed")
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
            status=status,
            verification=str(payload.get("verification", "unknown")),
            warnings=payload.get("warnings", []),
            forensic_notes=payload.get("forensic_notes", []),
            errors=payload.get("errors", []),
            metadata_mode=str(payload.get("metadata", {}).get("metadata_mode", "Enhanced")),
            metadata_actions=payload.get("metadata", {}).get("metadata_actions", {}),
            metadata_summary=str(payload.get("metadata", {}).get("metadata_summary", "")),
        )
        if request.generate_reports:
            outputs = self.reporter.save_reports(record, request.report_formats)
            self._append(f"Reports generated: {outputs}")
        else:
            outputs = {}
            self._append("Report generation disabled")
        self.dashboard.add_recent(f"{record.status} | {record.target_type} | {record.target}")
        self.reports_tab.refresh()
        if is_dry_run:
            QMessageBox.information(
                self,
                "Simulation complete",
                f"{operation_name} ran in Dry Run mode.\nNo files were deleted.\nStatus: {record.status}",
            )
        else:
            QMessageBox.information(self, "Operation complete", f"{operation_name} complete.\nStatus: {record.status}")

        self._set_operation_controls_enabled(True)

    def _on_failed(self, error_text: str) -> None:
        self._append(error_text)
        self._set_operation_controls_enabled(True)
        QMessageBox.critical(self, "Operation failed", error_text)

    def _on_thread_finished(self) -> None:
        self.thread = None
        self.worker = None
        self._active_request = None
        self._active_operation_name = ""
        self._active_start = ""

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
            generate_reports=self.shredder.generate_reports.isChecked(),
            report_formats=self.shredder.selected_report_formats(),
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
            generate_reports=self.partition.generate_reports.isChecked(),
            report_formats=self.partition.selected_report_formats(),
        )
        self._append("Typed confirmation validated for partition/free-space action.")
        self._append(metadata_mode_summary(req.metadata_mode))
        self._run_request(req, "Partition/Free-space Wipe")
