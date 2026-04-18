from __future__ import annotations

import logging
import os
from datetime import datetime

import psutil
from PySide6.QtCore import QObject, QTimer, Signal, Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QSizePolicy,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.core.partition_wiper import PartitionWiper
from app.core.privilege_checker import is_admin
from app.core.utils import human_size
from app.gui.widgets import DriveUsageWidget, QuickActionButton, StatusBadge, SummaryCard


class _LogEmitter(QObject):
    message = Signal(str)


class _QtLogHandler(logging.Handler):
    def __init__(self, emitter: _LogEmitter) -> None:
        super().__init__()
        self._emitter = emitter

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self._emitter.message.emit(msg)


class DashboardTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("DashboardRoot")
        self._session_wipe_count = 0
        self._last_operation_status = "No operations yet"
        self._forensic_tips = [
            "Deleted files may still leave traces in NTFS MFT and USN journal records.",
            "Free-space wiping reduces practical recoverability of previously deleted content.",
            "SSD wear leveling and TRIM can reduce deterministic overwrite effectiveness.",
            "Dry Run mode is recommended for demonstration and classroom safety.",
        ]
        self._tip_index = 0

        self.mode_banner = QLabel("")
        self.mode_banner.setAlignment(Qt.AlignCenter)
        self.mode_banner.setWordWrap(True)
        self.mode_banner.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.cards: dict[str, SummaryCard] = {
            "drives": SummaryCard("Total Drives Detected", "0", "#60a5fa"),
            "free": SummaryCard("Total Free Space", "0 B", "#34d399"),
            "privilege": SummaryCard("Privilege Level", "Standard", "#fbbf24"),
            "demo_mode": SummaryCard("Demo Safe Mode", "ON", "#22c55e"),
            "last_status": SummaryCard("Last Operation Status", "N/A", "#c4b5fd"),
            "wipe_count": SummaryCard("Session Wipe Count", "0", "#f97316"),
        }
        for card in self.cards.values():
            card.setMinimumHeight(94)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
            card.title_label.setWordWrap(True)
            card.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            card.value_label.setWordWrap(True)
            card.value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.drive_visual_container = QWidget()
        self.drive_visual_layout = QVBoxLayout(self.drive_visual_container)
        self.drive_visual_layout.setContentsMargins(8, 8, 8, 8)
        self.drive_visual_layout.setSpacing(10)
        self.drive_visual_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.drive_scroll = QScrollArea()
        self.drive_scroll.setWidgetResizable(True)
        self.drive_scroll.setWidget(self.drive_visual_container)
        self.drive_scroll.setFrameShape(QFrame.NoFrame)
        self.drive_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.activity_feed = QListWidget()
        self.activity_feed.setMinimumHeight(180)
        self.activity_feed.setAlternatingRowColors(True)
        self.activity_feed.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.quick_file_btn = QuickActionButton("F", "Quick File Wipe", "Jump to File/Folder tab")
        self.quick_folder_btn = QuickActionButton("D", "Folder Wipe", "Recursive folder sanitization")
        self.quick_space_btn = QuickActionButton("S", "Free Space Wipe", "Jump to Partition tab")
        self.quick_demo_btn = QuickActionButton("R", "Dry Run Demo", "Open shredder with simulation focus")

        self.tip_label = QLabel("")
        self.tip_label.setWordWrap(True)
        self.tip_label.setObjectName("Muted")
        self.tip_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tip_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.cpu_bar = QProgressBar()
        self.mem_bar = QProgressBar()
        self.disk_bar = QProgressBar()
        for bar in (self.cpu_bar, self.mem_bar, self.disk_bar):
            bar.setRange(0, 100)

        self.risk_badges = {
            "system_drive": StatusBadge("System Drive Detected", "warn"),
            "privileges": StatusBadge("Admin Privileges Missing", "warn"),
            "mode": StatusBadge("Safe Mode Enabled", "good"),
        }
        self.recoverability_label = StatusBadge("Recoverability Risk: LOW", "good")

        self._build_ui()
        self._wire_actions()
        self._install_activity_log_hook()
        self.refresh_drives()
        self._refresh_system_health()
        self._refresh_mode_indicators()

        self.tip_timer = QTimer(self)
        self.tip_timer.timeout.connect(self._rotate_tip)
        self.tip_timer.start(4500)

        self.health_timer = QTimer(self)
        self.health_timer.timeout.connect(self._refresh_system_health)
        self.health_timer.start(2000)

        self.mode_timer = QTimer(self)
        self.mode_timer.timeout.connect(self._refresh_mode_indicators)
        self.mode_timer.start(1200)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(12)
        root.addWidget(self.mode_banner)

        dashboard_content_widget = QWidget()
        dashboard_content_widget.setObjectName("DashboardContentWidget")
        dashboard_content_layout = QVBoxLayout(dashboard_content_widget)
        dashboard_content_layout.setContentsMargins(10, 10, 10, 10)
        dashboard_content_layout.setSpacing(12)

        # Top stats section
        top_cards = QGroupBox("Forensic Control Metrics")
        top_cards.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        cards_layout = QGridLayout(top_cards)
        cards_layout.setContentsMargins(10, 10, 10, 10)
        cards_layout.setSpacing(12)
        card_keys = list(self.cards.keys())
        for i, key in enumerate(card_keys):
            cards_layout.addWidget(self.cards[key], i // 3, i % 3)
        cards_layout.setColumnStretch(0, 1)
        cards_layout.setColumnStretch(1, 1)
        cards_layout.setColumnStretch(2, 1)

        # Middle + bottom sections in a single responsive grid
        dashboard_grid = QGridLayout()
        dashboard_grid.setContentsMargins(0, 0, 0, 0)
        dashboard_grid.setSpacing(12)

        drive_panel = QGroupBox("Drive Utilization Visualization")
        drive_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        d_layout = QVBoxLayout(drive_panel)
        d_layout.setContentsMargins(10, 10, 10, 10)
        d_layout.setSpacing(12)
        d_layout.addWidget(self.drive_scroll)

        activity_panel = QGroupBox("Live Activity Feed")
        activity_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        a_layout = QVBoxLayout(activity_panel)
        a_layout.setContentsMargins(10, 10, 10, 10)
        a_layout.setSpacing(12)
        a_layout.addWidget(self.activity_feed)

        quick_panel = QGroupBox("Quick Actions")
        quick_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        q_layout = QVBoxLayout(quick_panel)
        q_layout.setContentsMargins(10, 10, 10, 10)
        q_layout.setSpacing(12)
        q_layout.addWidget(self.quick_file_btn)
        q_layout.addWidget(self.quick_folder_btn)
        q_layout.addWidget(self.quick_space_btn)
        q_layout.addWidget(self.quick_demo_btn)
        q_layout.addStretch(1)

        insight_panel = QGroupBox("Forensic Insights")
        insight_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        i_layout = QVBoxLayout(insight_panel)
        i_layout.setContentsMargins(10, 10, 10, 10)
        i_layout.setSpacing(12)
        i_layout.addWidget(self.tip_label)

        status_panel = QGroupBox("System / Risk Status")
        status_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        s_layout = QVBoxLayout(status_panel)
        s_layout.setContentsMargins(10, 10, 10, 10)
        s_layout.setSpacing(12)

        health_panel = QGroupBox("System Health")
        health_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        h_layout = QVBoxLayout(health_panel)
        h_layout.setContentsMargins(10, 10, 10, 10)
        h_layout.setSpacing(12)
        h_layout.addWidget(QLabel("CPU Usage"))
        h_layout.addWidget(self.cpu_bar)
        h_layout.addWidget(QLabel("RAM Usage"))
        h_layout.addWidget(self.mem_bar)
        h_layout.addWidget(QLabel("Disk Usage"))
        h_layout.addWidget(self.disk_bar)

        risk_panel = QGroupBox("Risk / Status")
        risk_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        r_layout = QVBoxLayout(risk_panel)
        r_layout.setContentsMargins(10, 10, 10, 10)
        r_layout.setSpacing(12)
        r_layout.addWidget(self.risk_badges["system_drive"])
        r_layout.addWidget(self.risk_badges["privileges"])
        r_layout.addWidget(self.risk_badges["mode"])
        r_layout.addWidget(self.recoverability_label)

        s_layout.addWidget(health_panel)
        s_layout.addWidget(risk_panel)

        # Row 0 = top stats container, Row 1 = main panels, Row 2 = bottom panels
        dashboard_grid.addWidget(top_cards, 0, 0, 1, 3)
        dashboard_grid.addWidget(drive_panel, 1, 0, 1, 2)
        dashboard_grid.addWidget(activity_panel, 1, 2)
        dashboard_grid.addWidget(quick_panel, 2, 0)
        dashboard_grid.addWidget(insight_panel, 2, 1)
        dashboard_grid.addWidget(status_panel, 2, 2)

        dashboard_grid.setColumnStretch(0, 1)
        dashboard_grid.setColumnStretch(1, 1)
        dashboard_grid.setColumnStretch(2, 1)
        dashboard_grid.setRowStretch(0, 0)
        dashboard_grid.setRowStretch(1, 1)
        dashboard_grid.setRowStretch(2, 1)

        dashboard_content_layout.addLayout(dashboard_grid)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidget(dashboard_content_widget)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        root.addWidget(scroll_area)

    def _wire_actions(self) -> None:
        self.quick_file_btn.clicked.connect(lambda: self._goto_tab("File / Folder Shredder"))
        self.quick_folder_btn.clicked.connect(lambda: self._goto_tab("File / Folder Shredder"))
        self.quick_space_btn.clicked.connect(lambda: self._goto_tab("Partition / Free Space Wipe"))
        self.quick_demo_btn.clicked.connect(self._activate_demo_route)

    def _install_activity_log_hook(self) -> None:
        self._log_emitter = _LogEmitter()
        self._log_emitter.message.connect(self._append_activity)
        self._log_handler = _QtLogHandler(self._log_emitter)
        self._log_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.getLogger("forensiwipe.gui").addHandler(self._log_handler)

    def _append_activity(self, text: str) -> None:
        ts = datetime.now().strftime("%I:%M:%S %p")
        item = QListWidgetItem(f"[{ts}] {text}")
        self.activity_feed.insertItem(0, item)
        while self.activity_feed.count() > 200:
            self.activity_feed.takeItem(self.activity_feed.count() - 1)

    def _rotate_tip(self) -> None:
        self.tip_label.setText(self._forensic_tips[self._tip_index])
        self._tip_index = (self._tip_index + 1) % len(self._forensic_tips)

    def _refresh_system_health(self) -> None:
        cpu = int(psutil.cpu_percent(interval=None))
        mem = int(psutil.virtual_memory().percent)
        disk_root = "C:\\" if os.name == "nt" else "/"
        disk = int(psutil.disk_usage(disk_root).percent)
        self.cpu_bar.setValue(cpu)
        self.mem_bar.setValue(mem)
        self.disk_bar.setValue(disk)
        self.cpu_bar.setFormat(f"{cpu}%")
        self.mem_bar.setFormat(f"{mem}%")
        self.disk_bar.setFormat(f"{disk}%")

    def _refresh_mode_indicators(self) -> None:
        main = self.window()
        demo_on = True
        method = "NULL_0x00"
        passes = 1
        dry_run = True

        if hasattr(main, "shredder"):
            demo_on = bool(main.shredder.demo_safe_box.isChecked())
            method = main.shredder.method_combo.currentText()
            passes = main.shredder.passes_spin.value()
            dry_run = main.shredder.dry_run_box.isChecked()

        if demo_on:
            self.mode_banner.setObjectName("ModeBannerSafe")
            self.mode_banner.setText("DEMO SAFE MODE: ON  |  Destructive flows are constrained")
            self.cards["demo_mode"].set_value("ON", "#22c55e")
            self.risk_badges["mode"].setText("Safe Mode Enabled")
            self.risk_badges["mode"].set_badge("good")
        else:
            self.mode_banner.setObjectName("ModeBannerRisk")
            self.mode_banner.setText("REAL MODE: ACTIVE  |  Confirm targets carefully before operation")
            self.cards["demo_mode"].set_value("OFF", "#ef4444")
            self.risk_badges["mode"].setText("Real Mode Active")
            self.risk_badges["mode"].set_badge("bad")

        self.mode_banner.style().unpolish(self.mode_banner)
        self.mode_banner.style().polish(self.mode_banner)
        self._update_recoverability_risk(method, passes, dry_run)

    def _update_recoverability_risk(self, method: str, passes: int, dry_run: bool) -> None:
        if dry_run:
            self.recoverability_label.setText("Recoverability Risk: HIGH (dry-run, no overwrite)")
            self.recoverability_label.set_badge("bad")
            return
        if passes >= 3 and method in {"RANDOM", "ONES_0xFF", "NULL_0x00"}:
            self.recoverability_label.setText("Recoverability Risk: LOW")
            self.recoverability_label.set_badge("good")
        elif passes >= 2:
            self.recoverability_label.setText("Recoverability Risk: MEDIUM")
            self.recoverability_label.set_badge("warn")
        else:
            self.recoverability_label.setText("Recoverability Risk: HIGH")
            self.recoverability_label.set_badge("bad")

    def _goto_tab(self, tab_name: str) -> None:
        main = self.window()
        if hasattr(main, "tabs"):
            for idx in range(main.tabs.count()):
                if main.tabs.tabText(idx) == tab_name:
                    main.tabs.setCurrentIndex(idx)
                    return

    def _activate_demo_route(self) -> None:
        self._goto_tab("File / Folder Shredder")
        main = self.window()
        if hasattr(main, "shredder"):
            main.shredder.dry_run_box.setChecked(True)
            main.shredder.demo_safe_box.setChecked(True)
            self._append_activity("Dry Run Demo route activated from dashboard quick action.")

    def refresh_drives(self) -> None:
        while self.drive_visual_layout.count():
            item = self.drive_visual_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        drives = PartitionWiper().list_drives()
        total_free = 0
        system_detected = False
        for d in drives:
            total_free += d.free_bytes
            system_detected = system_detected or d.likely_system
            widget = DriveUsageWidget(
                label=d.mount_point,
                filesystem=d.filesystem,
                used=d.used_bytes,
                total=d.total_bytes,
                is_system=d.likely_system,
            )
            widget.set_meta(human_size(d.used_bytes), human_size(d.free_bytes))
            self.drive_visual_layout.addWidget(widget)
        self.drive_visual_layout.addStretch(1)

        self.cards["drives"].set_value(str(len(drives)))
        self.cards["free"].set_value(human_size(total_free))
        self.cards["privilege"].set_value("Administrator" if is_admin() else "Standard User", "#34d399" if is_admin() else "#f59e0b")
        self.cards["last_status"].set_value(self._last_operation_status, "#c4b5fd")
        self.cards["wipe_count"].set_value(str(self._session_wipe_count))

        self.risk_badges["system_drive"].setText("System Drive Detected" if system_detected else "No System Drive Flag")
        self.risk_badges["system_drive"].set_badge("warn" if system_detected else "good")
        self.risk_badges["privileges"].setText("Admin Privileges Present" if is_admin() else "Admin Privileges Missing")
        self.risk_badges["privileges"].set_badge("good" if is_admin() else "warn")

    def add_recent(self, text: str) -> None:
        self._session_wipe_count += 1
        self._last_operation_status = text
        self.cards["last_status"].set_value(text[:36] + ("..." if len(text) > 36 else ""))
        self.cards["wipe_count"].set_value(str(self._session_wipe_count))
        self._append_activity(text)
