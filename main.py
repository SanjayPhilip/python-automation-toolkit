"""
Python Automation Toolkit — Sanjay Philip
Run individual modules or use this as the main entry point.
"""

from toolkit.file_organizer import FileOrganizer
from toolkit.data_processor import DataProcessor
from toolkit.report_generator import ReportGenerator
from toolkit.logger import get_logger

log = get_logger("main")

def main():
    log.info("=== Python Automation Toolkit ===")

    # Example: Organize files in a folder
    organizer = FileOrganizer("./data")
    organizer.organize_by_extension()

    # Example: Process a CSV
    processor = DataProcessor("./data/sample.csv")
    summary = processor.summarize()
    log.info(f"Data summary: {summary}")

    # Example: Generate a report
    reporter = ReportGenerator(summary, output_dir="./output")
    reporter.generate_text_report()
    reporter.generate_csv_report()

    log.info("All tasks completed. Check ./output folder.")

if __name__ == "__main__":
    main()
