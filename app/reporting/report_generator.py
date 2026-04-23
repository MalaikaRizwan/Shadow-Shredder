from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

from jinja2 import Template

from app.core.utils import ensure_dir, utc_now_iso
from app.reporting.export_utils import write_csv_row, write_json
from app.reporting.html_templates import OPERATION_TEMPLATE


@dataclass
class OperationRecord:
    operation_id: str
    case_id: str
    operator: str
    started_at: str
    ended_at: str
    target: str
    target_type: str
    filesystem: str
    method: str
    passes: int
    bytes_processed: int
    status: str
    verification: str
    warnings: list[str] = field(default_factory=list)
    forensic_notes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata_mode: str = "Enhanced"
    metadata_actions: dict = field(default_factory=dict)
    metadata_summary: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class ReportGenerator:
    def __init__(self, reports_dir: Path) -> None:
        self.reports_dir = ensure_dir(reports_dir)

    def save_reports(self, record: OperationRecord, formats: list[str] | None = None) -> dict[str, str]:
        if formats is None:
            formats = ["json", "html", "txt", "csv"]
        base = self._report_base(record)
        data = record.to_dict()

        outputs = {}

        if "json" in formats:
            json_path = base.with_suffix(".json")
            write_json(json_path, data)
            outputs["json"] = str(json_path)

        if "csv" in formats:
            csv_path = self.reports_dir / "operations.csv"
            write_csv_row(csv_path, {k: str(v) for k, v in data.items() if not isinstance(v, list)})
            outputs["csv"] = str(csv_path)

        if "html" in formats:
            html_path = base.with_suffix(".html")
            html = Template(OPERATION_TEMPLATE).render(**data)
            html_path.write_text(html, encoding="utf-8")
            outputs["html"] = str(html_path)

        if "txt" in formats:
            txt_path = base.with_suffix(".txt")
            txt_path.write_text(
                f"ForensiWipe Summary\nOperation: {record.operation_id}\nStatus: {record.status}\n"
                f"Target: {record.target}\nMethod: {record.method}\nVerification: {record.verification}\n"
                f"Metadata Handling Mode: {record.metadata_mode}\n"
                f"Metadata Actions: rename_rounds={record.metadata_actions.get('rename_rounds', 0)}, "
                f"truncate={record.metadata_actions.get('truncate', False)}, "
                f"sha256_pre_wipe={record.metadata_actions.get('sha256_pre_wipe', False)}\n"
                f"{record.metadata_summary}\n"
                f"Ended: {record.ended_at or utc_now_iso()}",
                encoding="utf-8",
            )
            outputs["txt"] = str(txt_path)

        return outputs

    def _report_base(self, record: OperationRecord) -> Path:
        timestamp = record.started_at or record.ended_at or record.operation_id
        safe_name = self._format_timestamp(timestamp)
        return self.reports_dir / f"report_{safe_name}"

    def _format_timestamp(self, stamp: str) -> str:
        try:
            stamp = stamp.replace("Z", "+00:00")
            dt = datetime.fromisoformat(stamp)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            target_tz = timezone(timedelta(hours=5))
            dt = dt.astimezone(target_tz)
            return dt.strftime("%Y%m%d_%H%M%S")
        except ValueError:
            safe = stamp.replace(" ", "_").replace(":", "-")
            return safe