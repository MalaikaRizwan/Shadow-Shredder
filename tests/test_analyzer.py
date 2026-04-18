from pathlib import Path

from app.core.analyzer import Analyzer


def test_analyze_file(tmp_path: Path):
    p = tmp_path / "demo.txt"
    p.write_text("abc", encoding="utf-8")
    data = Analyzer().analyze_path(p)
    assert data.exists is True
    assert data.target_type == "file"
    assert data.size_bytes == 3


def test_analyze_folder(tmp_path: Path):
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "a.bin").write_bytes(b"1234")
    info = Analyzer().analyze_path(folder)
    assert info.target_type == "folder"
    assert info.files_count >= 1
