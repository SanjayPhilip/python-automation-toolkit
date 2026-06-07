"""
ReportGenerator — generates text and CSV reports from data summaries.
Supports timestamped output files to avoid overwriting previous runs.
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from toolkit.logger import get_logger


class ReportGenerator:
    """
    Generate readable reports from processed data summaries.

    Usage:
        reporter = ReportGenerator(summary, output_dir="./output")
        reporter.generate_text_report()
        reporter.generate_csv_report()
    """

    def __init__(self, summary: dict, output_dir: str = "./output"):
        self.summary = summary
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log = get_logger("ReportGenerator")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _filename(self, prefix: str, ext: str) -> Path:
        return self.output_dir / f"{prefix}_{self.timestamp}.{ext}"

    def generate_text_report(self) -> str:
        """Write a human-readable .txt report. Returns the file path."""
        path = self._filename("report", "txt")
        lines = [
            "=" * 55,
            "  PYTHON AUTOMATION TOOLKIT — DATA REPORT",
            f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 55,
            "",
            f"  File     : {self.summary.get('file', 'N/A')}",
            f"  Rows     : {self.summary.get('rows', 0)}",
            f"  Columns  : {self.summary.get('columns', 0)}",
            f"  Headers  : {', '.join(self.summary.get('headers', []))}",
            "",
            "  COLUMN STATISTICS",
            "  " + "-" * 53,
        ]

        for col, stat in self.summary.get("stats", {}).items():
            lines.append(f"\n  [{col}]")
            for k, v in stat.items():
                lines.append(f"    {k:<10}: {v}")

        lines += ["", "=" * 55, "  End of Report", "=" * 55]

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            self.log.info(f"Text report saved: {path}")
        except Exception as e:
            self.log.error(f"Failed to write text report: {e}")
            raise

        return str(path)

    def generate_csv_report(self) -> str:
        """Write a flat CSV summary of column stats. Returns the file path."""
        path = self._filename("summary", "csv")
        rows = []

        for col, stat in self.summary.get("stats", {}).items():
            row = {"column": col}
            row.update({k: v for k, v in stat.items() if not isinstance(v, list)})
            rows.append(row)

        if not rows:
            self.log.warning("No stats to write to CSV.")
            return ""

        try:
            headers = list(rows[0].keys())
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(rows)
            self.log.info(f"CSV report saved: {path}")
        except Exception as e:
            self.log.error(f"Failed to write CSV report: {e}")
            raise

        return str(path)

    def generate_file_org_report(self, org_summary: dict) -> str:
        """Write a text report from a FileOrganizer summary."""
        path = self._filename("file_org_report", "txt")
        total = sum(len(v) for v in org_summary.values())
        lines = [
            "=" * 55,
            "  FILE ORGANIZER REPORT",
            f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 55,
            f"\n  Total files organized: {total}\n",
        ]
        for category, files in org_summary.items():
            lines.append(f"  {category}/ ({len(files)} file(s))")
            for f in files:
                lines.append(f"    - {f}")
        lines += ["", "=" * 55]

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        self.log.info(f"File org report saved: {path}")
        return str(path)
