APP_QSS = """
QWidget { background-color: #060b16; color: #dbeafe; font-size: 11pt; }
QMainWindow, QTabWidget, QTabWidget::pane, QScrollArea, QScrollArea > QWidget > QWidget { background-color: #060b16; }
QGroupBox { border: 1px solid #1f2f4b; margin-top: 8px; padding: 10px; border-radius: 10px; background: #0b1528; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color: #93c5fd; }
QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #1d4ed8, stop:1 #2563eb); border: 1px solid #3b82f6; border-radius: 8px; padding: 8px; font-weight: 600; }
QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #2563eb, stop:1 #3b82f6); }
QLineEdit, QComboBox, QSpinBox, QTextEdit, QPlainTextEdit, QListWidget { background:#0a1120; border:1px solid #233554; border-radius:6px; padding:6px; }
QTabWidget::pane { border: 1px solid #334155; border-radius: 8px; padding: 6px; }
QTabBar::tab {
  background: #0a1324;
  color: #93c5fd;
  border: 1px solid #22385a;
  border-bottom: none;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  padding: 8px 14px;
  margin-right: 2px;
}
QTabBar::tab:hover {
  background: #10233f;
  color: #bfdbfe;
}
QTabBar::tab:selected {
  background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #12315f, stop:1 #0f2242);
  color: #e0f2fe;
  border: 1px solid #3b82f6;
  border-bottom: 1px solid #0b1528;
}
QProgressBar { background:#08101d; border:1px solid #233554; border-radius:6px; text-align:center; min-height: 16px; }
QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #22c55e, stop:1 #16a34a); border-radius:6px; }

QFrame#SummaryCard {
  background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0d1a30, stop:1 #101d38);
  border: 1px solid #28406b;
  border-radius: 12px;
}
QLabel#CardTitle { color: #93c5fd; font-size: 10pt; }
QLabel#CardValue { font-size: 13pt; font-weight: 700; }

QFrame#DriveWidget { background: #091526; border: 1px solid #20395f; border-radius: 10px; }
QLabel#DriveTitle { font-weight: 600; color: #bfdbfe; }
QLabel#Muted { color: #94a3b8; font-size: 10pt; }

QPushButton#QuickActionButton {
  text-align: left;
  padding: 10px;
  min-height: 56px;
  border-radius: 10px;
  background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0f2f6d, stop:1 #0e7490);
  border: 1px solid #38bdf8;
}
QPushButton#QuickActionButton:hover {
  background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #1d4ed8, stop:1 #0891b2);
}

QLabel#ModeBannerSafe {
  background: #052e1c; border:1px solid #16a34a; color:#86efac;
  border-radius: 8px; padding: 8px; font-weight: 700;
}
QLabel#ModeBannerRisk {
  background: #3f1111; border:1px solid #ef4444; color:#fecaca;
  border-radius: 8px; padding: 8px; font-weight: 700;
}

QLabel#RiskBadgeGood { background:#052e1c; color:#86efac; border:1px solid #16a34a; border-radius: 8px; padding: 3px 8px; }
QLabel#RiskBadgeWarn { background:#3f2a04; color:#fde68a; border:1px solid #f59e0b; border-radius: 8px; padding: 3px 8px; }
QLabel#RiskBadgeBad { background:#3f1111; color:#fecaca; border:1px solid #ef4444; border-radius: 8px; padding: 3px 8px; }
"""
