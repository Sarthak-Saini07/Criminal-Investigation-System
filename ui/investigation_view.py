"""
Investigation Progress, Interrogation Notes & Forensic Reports for CICMS.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database.connection import get_db
from database.models import UserSession

class InvestigationView(ttk.Frame):
    """Investigation Module View UI."""

    def __init__(self, parent: ttk.Frame, session: UserSession):
        super().__init__(parent)
        self.session = session
        self.db = get_db()
        self.pack(fill=tk.BOTH, expand=True)
        self._build_ui()

    def _build_ui(self):
        top_bar = ttk.Frame(self, padding=10)
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="INVESTIGATION & FORENSIC REPORTS", font=("Segoe UI", 14, "bold"), foreground="#38ef7d").pack(side=tk.LEFT)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padding=10)

        # Tab 1: Forensic Reports
        tab_forensic = ttk.Frame(notebook)
        notebook.add(tab_forensic, text="Forensic Lab Reports")

        cols_f = ("Report ID", "Evidence ID", "Lab Name", "Examiner", "Submission Date", "Conclusion")
        tree_f = ttk.Treeview(tab_forensic, columns=cols_f, show="headings")
        for c in cols_f:
            tree_f.heading(c, text=c)
            tree_f.column(c, width=130, anchor=tk.CENTER)
        tree_f.pack(fill=tk.BOTH, expand=True)

        rows_f = self.db.fetch_all("SELECT * FROM forensic_reports LIMIT 100")
        for r in rows_f:
            tree_f.insert("", tk.END, values=(r["report_id"], r["evidence_id"], r["lab_name"], r["examiner_name"], str(r["submission_date"]), r["conclusion"]))

        # Tab 2: Interrogations
        tab_inter = ttk.Frame(notebook)
        notebook.add(tab_inter, text="Interrogation Sessions")

        cols_i = ("Session ID", "Case ID", "Suspect ID", "Date", "Duration (mins)", "Key Confessions")
        tree_i = ttk.Treeview(tab_inter, columns=cols_i, show="headings")
        for c in cols_i:
            tree_i.heading(c, text=c)
            tree_i.column(c, width=130, anchor=tk.CENTER)
        tree_i.pack(fill=tk.BOTH, expand=True)

        rows_i = self.db.fetch_all("SELECT * FROM interrogations LIMIT 100")
        for r in rows_i:
            tree_i.insert("", tk.END, values=(r["interrogation_id"], r["case_id"], r["suspect_id"], str(r["session_date"]), r["duration_minutes"], r["key_confessions"]))
