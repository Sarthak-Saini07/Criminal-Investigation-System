"""
Witness Registry & Protection Status Module for CICMS.
"""

import tkinter as tk
from tkinter import ttk
from database.connection import get_db
from database.models import UserSession

class WitnessView(ttk.Frame):
    """Witness Management View UI."""

    def __init__(self, parent: ttk.Frame, session: UserSession):
        super().__init__(parent)
        self.session = session
        self.db = get_db()
        self.pack(fill=tk.BOTH, expand=True)
        self._build_ui()

    def _build_ui(self):
        top_bar = ttk.Frame(self, padding=10)
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="WITNESS REGISTRY & PROTECTION MODULE", font=("Segoe UI", 14, "bold"), foreground="#38ef7d").pack(side=tk.LEFT)

        table_frame = ttk.Frame(self, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("Witness ID", "Case ID", "Full Name", "Protection Status", "Statement Summary")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor=tk.CENTER)

        self.tree.column("Statement Summary", width=300, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = self.db.fetch_all("SELECT * FROM witnesses LIMIT 200")
        for r in rows:
            self.tree.insert("", tk.END, values=(
                r["witness_id"], r["case_id"], r["full_name"], r["protection_status"], r["statement_summary"]
            ))
