from __future__ import annotations

import traceback

from PySide6.QtCore import QObject, Signal, Slot

from app.core.wipe_engine import WipeEngine, WipeRequest


class OperationWorker(QObject):
    progress = Signal(int, int, str)
    done = Signal(dict)
    failed = Signal(str)

    def __init__(self, request: WipeRequest) -> None:
        super().__init__()
        self._request = request
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def _is_cancelled(self) -> bool:
        return self._cancelled

    @Slot()
    def run(self) -> None:
        try:
            engine = WipeEngine()
            result = engine.execute(
                self._request,
                progress_cb=lambda cur, total, msg: self.progress.emit(cur, max(total, 1), msg),
                cancel_flag=self._is_cancelled,
            )
            self.done.emit(result.to_dict())
        except Exception as exc:
            self.failed.emit(f"{exc}\n{traceback.format_exc()}")
