from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QPushButton, QVBoxLayout


class SummaryCard(QFrame):
    def __init__(self, title: str, value: str, color: str = "#93c5fd") -> None:
        super().__init__()
        self.setObjectName("SummaryCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("CardTitle")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("CardValue")
        self.value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: str, color: str | None = None) -> None:
        self.value_label.setText(value)
        if color:
            self.value_label.setStyleSheet(f"color: {color};")


class DriveUsageWidget(QFrame):
    def __init__(self, label: str, filesystem: str, used: int, total: int, is_system: bool = False) -> None:
        super().__init__()
        self.setObjectName("DriveWidget")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        header = QHBoxLayout()
        left = QLabel(f"{label} ({filesystem})")
        left.setObjectName("DriveTitle")
        right = QLabel("SYSTEM" if is_system else "DATA")
        right.setObjectName("RiskBadgeWarn" if is_system else "RiskBadgeGood")
        header.addWidget(left)
        header.addStretch()
        header.addWidget(right)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        pct = int((used / total) * 100) if total else 0
        self.bar.setValue(max(0, min(100, pct)))
        self.bar.setFormat(f"Used {pct}%")

        self.meta = QLabel("")
        self.meta.setObjectName("Muted")
        self.meta.setWordWrap(True)
        layout.addLayout(header)
        layout.addWidget(self.bar)
        layout.addWidget(self.meta)

    def set_meta(self, used_text: str, free_text: str) -> None:
        self.meta.setText(f"Used: {used_text} | Free: {free_text}")


class QuickActionButton(QPushButton):
    def __init__(self, icon_text: str, title: str, subtitle: str) -> None:
        super().__init__(f"{icon_text}  {title}\n{subtitle}")
        self.setObjectName("QuickActionButton")
        self.setCursor(Qt.PointingHandCursor)


class StatusBadge(QLabel):
    def __init__(self, text: str, level: str) -> None:
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.set_badge(level)

    def set_badge(self, level: str) -> None:
        mapping = {"good": "RiskBadgeGood", "warn": "RiskBadgeWarn", "bad": "RiskBadgeBad"}
        self.setObjectName(mapping.get(level, "RiskBadgeWarn"))
        self.style().unpolish(self)
        self.style().polish(self)
