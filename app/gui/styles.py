APP_QSS = """
QWidget {
  background-color: #0b1020;
  color: #edf2ff;
  font-family: "Segoe UI", "Inter", "Arial", sans-serif;
  font-size: 10.5pt;
}

QMainWindow,
QTabWidget,
QTabWidget::pane,
QScrollArea,
QScrollArea > QWidget > QWidget {
  background-color: #0b1020;
}

QMainWindow {
  background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #0b1020, stop:0.55 #11182c, stop:1 #090d18);
}

QGroupBox {
  border: 1px solid rgba(148, 163, 184, 0.20);
  margin-top: 12px;
  padding: 12px;
  border-radius: 14px;
  background: rgba(15, 22, 39, 0.96);
}
QGroupBox::title {
  subcontrol-origin: margin;
  left: 12px;
  padding: 0 6px;
  color: #c7d2fe;
  font-weight: 700;
}

QPushButton {
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #2d6cdf, stop:1 #1f4fb4);
  border: 1px solid #3d79e6;
  border-bottom: 2px solid #16387d;
  border-radius: 10px;
  padding: 8px 14px;
  font-weight: 600;
  color: #ffffff;
  min-height: 24px;
}
QPushButton:hover {
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #3a7bf0, stop:1 #275fca);
}
QPushButton:pressed {
  background: #1f4fb4;
  border-top: 1px solid #16387d;
  border-left: 1px solid #16387d;
  border-right: 1px solid #16387d;
  border-bottom: 1px solid #102a5d;
  padding-top: 9px;
  padding-left: 15px;
}
QPushButton:disabled {
  background: #2a3142;
  border-color: #3d455a;
  color: #93a4bf;
}

QLineEdit,
QComboBox,
QSpinBox,
QTextEdit,
QPlainTextEdit,
QListWidget {
  background: rgba(8, 14, 27, 0.98);
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 10px;
  padding: 7px 10px;
  color: #f8fbff;
  selection-background-color: #60a5fa;
  selection-color: #08111f;
}
QLineEdit:focus,
QComboBox:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QListWidget:focus,
QSpinBox:focus {
  border: 1px solid #60a5fa;
  background: rgba(10, 17, 32, 1);
}
QComboBox::drop-down {
  background: rgba(35, 48, 76, 0.95);
  border-left: 1px solid rgba(148, 163, 184, 0.28);
  width: 22px;
  border-top-right-radius: 10px;
  border-bottom-right-radius: 10px;
}

QTabWidget::pane {
  border: 1px solid rgba(148, 163, 184, 0.20);
  border-radius: 14px;
  background: rgba(13, 18, 31, 0.96);
}
QTabBar::tab {
  background: rgba(18, 26, 45, 0.96);
  color: #cbd5e1;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-bottom: none;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
  padding: 8px 15px;
  margin-right: 4px;
  font-weight: 600;
}
QTabBar::tab:hover {
  background: rgba(28, 40, 66, 0.98);
  color: #f8fbff;
}
QTabBar::tab:selected {
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #315dbf, stop:1 #1e3f87);
  color: #ffffff;
  border: 1px solid #6ea8ff;
  border-bottom: 1px solid rgba(13, 18, 31, 0.96);
  font-weight: 700;
}

QProgressBar {
  background: rgba(7, 12, 22, 0.98);
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 10px;
  text-align: center;
  color: #e5eefc;
  font-weight: 600;
  font-size: 9pt;
  min-height: 18px;
}
QProgressBar::chunk {
  background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
    stop:0 #34d399, stop:1 #059669);
  border-radius: 8px;
  margin: 2px;
}

QScrollBar:vertical,
QScrollBar:horizontal {
  background: transparent;
  border: none;
}
QScrollBar:vertical {
  width: 12px;
  margin: 4px;
}
QScrollBar:horizontal {
  height: 12px;
  margin: 4px;
}
QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
  background: rgba(148, 163, 184, 0.45);
  border-radius: 6px;
  min-height: 24px;
  min-width: 24px;
}
QScrollBar::handle:vertical:hover,
QScrollBar::handle:horizontal:hover {
  background: rgba(96, 165, 250, 0.70);
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
  background: transparent;
}

QFrame#SummaryCard {
  background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 rgba(16, 24, 42, 0.98), stop:1 rgba(12, 18, 32, 0.98));
  border: 1px solid rgba(96, 165, 250, 0.20);
  border-radius: 16px;
}
QLabel#CardTitle {
  color: #93c5fd;
  font-size: 9pt;
  font-weight: 700;
  letter-spacing: 0.8px;
  text-transform: uppercase;
}
QLabel#CardValue {
  font-size: 14pt;
  font-weight: 700;
  color: #ffffff;
}

QFrame#DriveWidget {
  background: rgba(12, 18, 33, 0.98);
  border: 1px solid rgba(96, 165, 250, 0.18);
  border-radius: 14px;
}
QLabel#DriveTitle {
  font-weight: 700;
  color: #e5eefc;
}
QLabel#Muted {
  color: #94a3b8;
  font-size: 9.5pt;
}

QPushButton#QuickActionButton {
  text-align: left;
  padding: 10px 12px;
  min-height: 56px;
  border-radius: 12px;
  background: rgba(17, 24, 39, 0.98);
  border: 1px solid rgba(148, 163, 184, 0.22);
  color: #f8fbff;
  font-weight: 600;
}
QPushButton#QuickActionButton:hover {
  background: rgba(25, 35, 56, 0.98);
  border: 1px solid rgba(96, 165, 250, 0.45);
}

QLabel#ModeBannerSafe {
  background: rgba(8, 47, 73, 0.92);
  border: 1px solid rgba(34, 197, 94, 0.55);
  color: #dcfce7;
  border-radius: 10px;
  padding: 8px;
  font-weight: 700;
}
QLabel#ModeBannerRisk {
  background: rgba(69, 10, 10, 0.92);
  border: 1px solid rgba(248, 113, 113, 0.60);
  color: #fee2e2;
  border-radius: 10px;
  padding: 8px;
  font-weight: 700;
}

QLabel#RiskBadgeGood {
  background: rgba(8, 47, 73, 0.92);
  color: #dcfce7;
  border: 1px solid rgba(34, 197, 94, 0.55);
  border-radius: 999px;
  padding: 3px 8px;
  font-weight: 700;
}
QLabel#RiskBadgeWarn {
  background: rgba(69, 52, 10, 0.92);
  color: #fef3c7;
  border: 1px solid rgba(250, 204, 21, 0.60);
  border-radius: 999px;
  padding: 3px 8px;
  font-weight: 700;
}
QLabel#RiskBadgeBad {
  background: rgba(69, 10, 10, 0.92);
  color: #fee2e2;
  border: 1px solid rgba(248, 113, 113, 0.60);
  border-radius: 999px;
  padding: 3px 8px;
  font-weight: 700;
}
"""
