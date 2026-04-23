from app.reporting.report_generator import OperationRecord, ReportGenerator


def test_report_generation(tmp_path):
    gen = ReportGenerator(tmp_path)
    record = OperationRecord(
        operation_id="op1",
        case_id="case1",
        operator="tester",
        started_at="2026-01-01T00:00:00Z",
        ended_at="2026-01-01T00:00:01Z",
        target="C:/temp/demo.txt",
        target_type="file",
        filesystem="NTFS",
        method="RANDOM",
        passes=2,
        bytes_processed=123,
        status="success",
        verification="deleted",
    )
    outputs = gen.save_reports(record, ["json", "html", "txt", "csv"])
    for p in outputs.values():
        from pathlib import Path

        assert Path(p).exists()
