"""
Court Module & Chargesheet Registry View for CICMS.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database.connection import get_db
from database.models import UserSession

class CourtView(ttk.Frame):
    """Court Module View UI."""

    def __init__(self, parent: ttk.Frame, session: UserSession):
        super().__init__(parent)
        self.session = session
        self.db = get_db()
        self.pack(fill=tk.BOTH, expand=True)
        self._build_ui()

    def _build_ui(self):
        top_bar = ttk.Frame(self, padding=10)
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="COURT HEARINGS & CHARGESHEET REGISTRY", font=("Segoe UI", 14, "bold"), foreground="#38ef7d").pack(side=tk.LEFT)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padding=10)

        # Tab 1: Chargesheets
        tab_cs = ttk.Frame(notebook)
        notebook.add(tab_cs, text="Chargesheet Registry")

        cols_cs = ("Chargesheet No", "Case ID", "Filing Date", "Court Name", "IPC Sections", "Summary")
        tree_cs = ttk.Treeview(tab_cs, columns=cols_cs, show="headings")
        for c in cols_cs:
            tree_cs.heading(c, text=c)
            tree_cs.column(c, width=130, anchor=tk.CENTER)
        tree_cs.column("Summary", width=250, anchor=tk.W)
        tree_cs.pack(fill=tk.BOTH, expand=True)

        rows_cs = self.db.fetch_all("SELECT * FROM chargesheets LIMIT 100")
        for r in rows_cs:
            tree_cs.insert("", tk.END, values=(r["chargesheet_number"], r["case_id"], str(r["filing_date"]), r["court_name"], r["sections_applied"], r["charges_summary"]))

        # Tab 2: Court Cases & Verdicts
        tab_cc = ttk.Frame(notebook)
        notebook.add(tab_cc, text="Court Cases & Verdicts")

        cols_cc = ("Court Case No", "Case ID", "Filing Date", "Verdict", "Sentence Summary")
        tree_cc = ttk.Treeview(tab_cc, columns=cols_cc, show="headings")
        for c in cols_cc:
            tree_cc.heading(c, text=c)
            tree_cc.column(c, width=140, anchor=tk.CENTER)
        tree_cc.pack(fill=tk.BOTH, expand=True)

        rows_cc = self.db.fetch_all("SELECT * FROM court_cases LIMIT 100")
        for r in rows_cc:
            tree_cc.insert("", tk.END, values=(r["court_case_number"], r["case_id"], str(r["filing_date"]), r["verdict"], r["sentence_summary"] or "N/A"))
