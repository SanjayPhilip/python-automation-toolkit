"""
Tests for the Python Automation Toolkit.
Run with: python -m pytest tests/ -v
"""

import os
import csv
import pytest
import tempfile
from pathlib import Path

from toolkit.data_processor import DataProcessor
from toolkit.file_organizer import FileOrganizer
from toolkit.report_generator import ReportGenerator


# ── DataProcessor Tests ───────────────────────────────────────────────────────

@pytest.fixture
def sample_csv(tmp_path):
    f = tmp_path / "test.csv"
    f.write_text("name,score,status\nAlice,90,active\nBob,75,inactive\nAlice,90,active\n")
    return str(f)

def test_data_processor_load(sample_csv):
    dp = DataProcessor(sample_csv)
    assert len(dp.rows) == 3
    assert "name" in dp.headers

def test_data_processor_summarize(sample_csv):
    dp = DataProcessor(sample_csv)
    summary = dp.summarize()
    assert summary["rows"] == 3
    assert summary["columns"] == 3
    assert "score" in summary["stats"]

def test_data_processor_filter(sample_csv):
    dp = DataProcessor(sample_csv)
    result = dp.filter_rows("status", "active")
    assert len(result) == 2

def test_data_processor_dedup(sample_csv):
    dp = DataProcessor(sample_csv)
    result = dp.remove_duplicates()
    assert len(result) == 2

def test_data_processor_fill_missing(sample_csv):
    dp = DataProcessor(sample_csv)
    dp.rows[0]["score"] = ""
    count = dp.fill_missing("score", "0")
    assert count == 1
    assert dp.rows[0]["score"] == "0"

def test_data_processor_save(sample_csv, tmp_path):
    dp = DataProcessor(sample_csv)
    out = str(tmp_path / "out.csv")
    ok = dp.save(dp.rows, out)
    assert ok
    assert Path(out).exists()

def test_data_processor_missing_file():
    dp = DataProcessor("nonexistent.csv")
    assert dp.rows == []


# ── FileOrganizer Tests ───────────────────────────────────────────────────────

@pytest.fixture
def temp_dir_with_files(tmp_path):
    (tmp_path / "photo.jpg").write_text("img")
    (tmp_path / "doc.pdf").write_text("pdf")
    (tmp_path / "script.py").write_text("py")
    (tmp_path / "archive.zip").write_bytes(b"zip")
    return tmp_path

def test_file_organizer_dry_run(temp_dir_with_files):
    org = FileOrganizer(str(temp_dir_with_files))
    summary = org.organize_by_extension(dry_run=True)
    assert len(summary) > 0
    files_still_in_root = list(temp_dir_with_files.glob("*.*"))
    assert len(files_still_in_root) == 4  # untouched

def test_file_organizer_live(temp_dir_with_files):
    org = FileOrganizer(str(temp_dir_with_files))
    summary = org.organize_by_extension(dry_run=False)
    assert len(summary) > 0
    root_files = [f for f in temp_dir_with_files.iterdir() if f.is_file()]
    assert len(root_files) == 0  # all moved to subfolders

def test_file_organizer_empty_dir(tmp_path):
    org = FileOrganizer(str(tmp_path))
    summary = org.organize_by_extension()
    assert summary == {}


# ── ReportGenerator Tests ─────────────────────────────────────────────────────

@pytest.fixture
def sample_summary():
    return {
        "file": "test.csv",
        "rows": 3,
        "columns": 2,
        "headers": ["name", "score"],
        "stats": {
            "name":  {"count": 3, "unique": 2, "sample": ["Alice", "Bob"]},
            "score": {"count": 3, "min": 75.0, "max": 90.0, "mean": 85.0, "median": 90.0},
        },
    }

def test_report_text(sample_summary, tmp_path):
    rg = ReportGenerator(sample_summary, output_dir=str(tmp_path))
    path = rg.generate_text_report()
    assert Path(path).exists()
    content = Path(path).read_text()
    assert "REPORT" in content

def test_report_csv(sample_summary, tmp_path):
    rg = ReportGenerator(sample_summary, output_dir=str(tmp_path))
    path = rg.generate_csv_report()
    assert Path(path).exists()
    with open(path) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["column"] in ("name", "score")
