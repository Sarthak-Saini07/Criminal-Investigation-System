"""
CSV Data Exporter for CICMS.
Generates raw CSV exports for cases, FIRs, evidence, and officer performance datasets.
"""

import csv
import pandas as pd
from pathlib import Path
from database.connection import get_db

def export_table_to_csv(table_name: str, output_path: str) -> str:
    """Exports any database table to CSV file."""
    db = get_db()
    rows = db.fetch_all(f"SELECT * FROM {table_name}")
    if not rows:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            f.write("No Data Found")
        return output_path

    keys = rows[0].keys()
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)

    return output_path
