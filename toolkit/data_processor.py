"""
DataProcessor — reads CSV files and performs common data-processing operations.
Handles missing values, type inference, filtering, and summary statistics.
"""

import csv
import os
import statistics
from pathlib import Path
from typing import Any
from toolkit.logger import get_logger


class DataProcessor:
    """
    Process CSV data files with filtering, cleaning, and summary stats.

    Usage:
        dp = DataProcessor("./data/sales.csv")
        summary = dp.summarize()
        filtered = dp.filter_rows(column="status", value="active")
        dp.save(filtered, "./output/active.csv")
    """

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.log = get_logger("DataProcessor")
        self.rows: list[dict] = []
        self.headers: list[str] = []

        if self.filepath.exists():
            self._load()
        else:
            self.log.warning(f"File not found: {filepath}. Starting with empty dataset.")

    def _load(self):
        try:
            with open(self.filepath, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.headers = list(reader.fieldnames or [])
                self.rows = [dict(row) for row in reader]
            self.log.info(f"Loaded {len(self.rows)} rows from '{self.filepath.name}'.")
        except Exception as e:
            self.log.error(f"Failed to load '{self.filepath}': {e}")
            raise

    def summarize(self) -> dict:
        """Return basic stats: row count, column count, numeric column stats."""
        if not self.rows:
            return {"rows": 0, "columns": 0, "stats": {}}

        stats = {}
        for col in self.headers:
            values = [row[col] for row in self.rows if row.get(col) not in (None, "")]
            numeric = []
            for v in values:
                try:
                    numeric.append(float(v))
                except ValueError:
                    pass

            if numeric:
                stats[col] = {
                    "count": len(numeric),
                    "min": round(min(numeric), 2),
                    "max": round(max(numeric), 2),
                    "mean": round(statistics.mean(numeric), 2),
                    "median": round(statistics.median(numeric), 2),
                }
            else:
                unique = set(values)
                stats[col] = {
                    "count": len(values),
                    "unique": len(unique),
                    "sample": list(unique)[:3],
                }

        summary = {
            "file": self.filepath.name,
            "rows": len(self.rows),
            "columns": len(self.headers),
            "headers": self.headers,
            "stats": stats,
        }
        self.log.info(f"Summary: {len(self.rows)} rows, {len(self.headers)} columns.")
        return summary

    def filter_rows(self, column: str, value: Any, exact: bool = True) -> list[dict]:
        """Filter rows where column matches value. Use exact=False for substring match."""
        if column not in self.headers:
            self.log.warning(f"Column '{column}' not found. Available: {self.headers}")
            return []

        if exact:
            result = [r for r in self.rows if r.get(column) == str(value)]
        else:
            result = [r for r in self.rows if str(value).lower() in str(r.get(column, "")).lower()]

        self.log.info(f"Filter '{column}={value}': {len(result)} row(s) matched.")
        return result

    def remove_duplicates(self, key_column: str = None) -> list[dict]:
        """Remove duplicate rows. If key_column given, dedup by that column only."""
        before = len(self.rows)
        if key_column:
            seen = set()
            result = []
            for row in self.rows:
                val = row.get(key_column)
                if val not in seen:
                    seen.add(val)
                    result.append(row)
        else:
            seen_tuples = set()
            result = []
            for row in self.rows:
                t = tuple(row.items())
                if t not in seen_tuples:
                    seen_tuples.add(t)
                    result.append(row)

        removed = before - len(result)
        self.log.info(f"Removed {removed} duplicate(s). {len(result)} rows remain.")
        self.rows = result
        return result

    def fill_missing(self, column: str, fill_value: Any = "N/A") -> int:
        """Fill empty/missing values in a column. Returns count of filled cells."""
        count = 0
        for row in self.rows:
            if row.get(column) in (None, ""):
                row[column] = str(fill_value)
                count += 1
        self.log.info(f"Filled {count} missing value(s) in '{column}' with '{fill_value}'.")
        return count

    def save(self, rows: list[dict], output_path: str) -> bool:
        """Save a list of row dicts to a new CSV file."""
        if not rows:
            self.log.warning("No rows to save.")
            return False
        try:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            headers = list(rows[0].keys())
            with open(out, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)
            self.log.info(f"Saved {len(rows)} rows to '{out}'.")
            return True
        except Exception as e:
            self.log.error(f"Failed to save: {e}")
            return False
