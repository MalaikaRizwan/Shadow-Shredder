from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QLineEdit, QVBoxLayout


class TypedConfirmationDialog(QDialog):
    def __init__(self, expected: str, warning: str, parent=None) -> None:
        super().__init__(parent)
        self.expected = expected
        self.setWindowTitle("Destructive Action Confirmation")
        self._entry = QLineEdit()
        self._entry.setPlaceholderText(f"Type '{expected}' to continue")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(warning))
        layout.addWidget(self._entry)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def is_valid(self) -> bool:
        return self._entry.text().strip() == self.expected
