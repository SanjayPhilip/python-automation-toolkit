"""
FileOrganizer — automatically sorts files in a directory by extension.
Supports dry-run mode so you can preview changes before applying them.
"""

import os
import shutil
from pathlib import Path
from toolkit.logger import get_logger

EXTENSION_MAP = {
    "Images":     {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"},
    "Documents":  {".pdf", ".docx", ".doc", ".txt", ".md", ".pptx", ".xlsx"},
    "Videos":     {".mp4", ".mov", ".avi", ".mkv", ".wmv"},
    "Audio":      {".mp3", ".wav", ".flac", ".aac", ".ogg"},
    "Archives":   {".zip", ".tar", ".gz", ".rar", ".7z"},
    "Code":       {".py", ".js", ".jsx", ".ts", ".html", ".css", ".json", ".csv"},
    "Data":       {".csv", ".json", ".xml", ".yaml", ".yml", ".sql"},
}


class FileOrganizer:
    """
    Organizes files in a target directory into categorized subfolders.

    Usage:
        organizer = FileOrganizer("./data")
        organizer.organize_by_extension()           # live run
        organizer.organize_by_extension(dry_run=True)  # preview only
    """

    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir)
        self.log = get_logger("FileOrganizer")

        if not self.target_dir.exists():
            self.target_dir.mkdir(parents=True)
            self.log.info(f"Created target directory: {self.target_dir}")

    def _get_category(self, suffix: str) -> str:
        for category, extensions in EXTENSION_MAP.items():
            if suffix.lower() in extensions:
                return category
        return "Misc"

    def organize_by_extension(self, dry_run: bool = False) -> dict:
        """
        Move files into subfolders by type.
        Returns a summary dict of {category: [filenames]}.
        """
        summary = {}
        files = [f for f in self.target_dir.iterdir() if f.is_file()]

        if not files:
            self.log.info("No files found to organize.")
            return summary

        for file in files:
            category = self._get_category(file.suffix)
            dest_folder = self.target_dir / category

            summary.setdefault(category, []).append(file.name)

            if not dry_run:
                dest_folder.mkdir(exist_ok=True)
                dest = dest_folder / file.name
                if dest.exists():
                    self.log.warning(f"Skipping (already exists): {file.name}")
                    continue
                shutil.move(str(file), str(dest))
                self.log.debug(f"Moved: {file.name} → {category}/")
            else:
                self.log.info(f"[DRY RUN] Would move: {file.name} → {category}/")

        self.log.info(f"Organized {len(files)} file(s) into {len(summary)} categorie(s).")
        return summary

    def flatten(self, dry_run: bool = False) -> int:
        """
        Reverse operation — move all files from subfolders back to target_dir.
        Returns count of files moved.
        """
        count = 0
        for item in self.target_dir.rglob("*"):
            if item.is_file() and item.parent != self.target_dir:
                dest = self.target_dir / item.name
                if not dry_run:
                    shutil.move(str(item), str(dest))
                    self.log.debug(f"Flattened: {item.name}")
                else:
                    self.log.info(f"[DRY RUN] Would flatten: {item.name}")
                count += 1
        self.log.info(f"Flattened {count} file(s).")
        return count
