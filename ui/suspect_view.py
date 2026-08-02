"""
Suspect & Criminal History Registry View for CICMS.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database.connection import get_db
from database.queries import GET_SUSPECTS_BY_CASE, INSERT_SUSPECT, INSERT_CRIMINAL_HISTORY
from database.models import UserSession

class SuspectView(ttk.Frame):
    """Suspect Management View UI."""

    def __init__(self, parent: ttk.Frame, session: UserSession):
        super().__init__(parent)
        self.session = session
        self.db = get_db()
        self.pack(fill=tk.BOTH, expand=True)
        self._build_ui()

    def _build_ui(self):
        top_bar = ttk.Frame(self, padding=10)
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="SUSPECT & CRIMINAL HISTORY REGISTRY", font=("Segoe UI", 14, "bold"), foreground="#38ef7d").pack(side=tk.LEFT)

        ttk.Label(top_bar, text="Filter by Case ID:").pack(side=tk.LEFT, padx=(20, 5))
        self.ent_case = ttk.Entry(top_bar, width=10)
        self.ent_case.pack(side=tk.LEFT)
        self.ent_case.insert(0, "1")

        ttk.Button(top_bar, text="Load Suspects", command=self.load_data).pack(side=tk.LEFT, padx=5)

        if self.session.role in ["Admin", "Police Officer", "Investigation Officer"]:
            ttk.Button(top_bar, text="+ Add Suspect Profile", command=self.add_suspect_dialog, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)

        table_frame = ttk.Frame(self, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("Suspect ID", "Full Name", "Alias", "Gender", "Arrest Status", "Prior Convictions", "Risk Level")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        case_id = self.ent_case.get().strip() or "1"
        rows = self.db.fetch_all(GET_SUSPECTS_BY_CASE, (case_id,))
        for r in rows:
            self.tree.insert("", tk.END, values=(
                r["suspect_id"], r["full_name"], r["alias_name"] or "None", r["gender"], r["arrest_status"], r.get("prior_convictions_count", 0), r.get("risk_level", "Low")
            ))

    def add_suspect_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add Suspect Record")
        dialog.geometry("400x380")

        ttk.Label(dialog, text="Case ID:").pack(pady=5)
        ent_cid = ttk.Entry(dialog)
        ent_cid.pack()
        ent_cid.insert(0, self.ent_case.get())

        ttk.Label(dialog, text="Suspect Full Name:").pack(pady=5)
        ent_name = ttk.Entry(dialog, width=30)
        ent_name.pack()

        ttk.Label(dialog, text="Alias / Street Name:").pack(pady=5)
        ent_alias = ttk.Entry(dialog, width=30)
        ent_alias.pack()

        ttk.Label(dialog, text="Arrest Status:").pack(pady=5)
        cmb_st = ttk.Combobox(dialog, values=["Wanted", "Under Investigation", "Arrested", "Released", "Bailed"])
        cmb_st.pack()
        cmb_st.set("Under Investigation")

        def save():
            cid = ent_cid.get()
            fn = ent_name.get().strip()
            al = ent_alias.get().strip()
            st = cmb_st.get()

            if not fn:
                messagebox.showerror("Error", "Suspect name is required.")
                return

            sid = self.db.execute_query(INSERT_SUSPECT, (cid, fn, al, "1990-01-01", "Male", "NAT-ID-99", "Unknown", 175, "Athletic", st))
            self.db.execute_query(INSERT_CRIMINAL_HISTORY, (sid, 0, "None", "None", "Low"))
            messagebox.showinfo("Success", "Suspect profile created.")
            dialog.destroy()
            self.load_data()

        ttk.Button(dialog, text="Save Suspect", command=save, style="Accent.TButton").pack(pady=15)
