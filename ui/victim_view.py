"""
Victim Registry & Medical Records View for CICMS.
"""

import tkinter as tk
from tkinter import ttk
from database.connection import get_db
from database.models import UserSession

class VictimView(ttk.Frame):
    """Victim Registry View UI."""

    def __init__(self, parent: ttk.Frame, session: UserSession):
        super().__init__(parent)
        self.session = session
        self.db = get_db()
        self.pack(fill=tk.BOTH, expand=True)
        self._build_ui()

    def _build_ui(self):
        top_bar = ttk.Frame(self, padding=10)
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="VICTIM REGISTRY & MEDICAL RECORDS", font=("Segoe UI", 14, "bold"), foreground="#38ef7d").pack(side=tk.LEFT)

        table_frame = ttk.Frame(self, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("Victim ID", "Case ID", "Full Name", "Gender", "Age", "Injury Level", "Compensation Status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = self.db.fetch_all("SELECT * FROM victims LIMIT 200")
        for r in rows:
            self.tree.insert("", tk.END, values=(
                r["victim_id"], r["case_id"], r["full_name"], r["gender"], r["age"], r["injury_level"], r["compensation_status"]
            ))
