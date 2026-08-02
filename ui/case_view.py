"""
Case Management View Component for CICMS.
Manages active criminal cases, officer assignments, status changes, and timeline audits.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database.connection import get_db
from database.queries import GET_ALL_CASES, GET_CASE_TIMELINE, UPDATE_CASE_STATUS, ASSIGN_LEAD_OFFICER
from database.models import UserSession
from utils.logger import logger

class CaseView(ttk.Frame):
    """Case Management View UI."""

    def __init__(self, parent: ttk.Frame, session: UserSession):
        super().__init__(parent)
        self.session = session
        self.db = get_db()
        self.pack(fill=tk.BOTH, expand=True)
        self._build_ui()

    def _build_ui(self):
        top_bar = ttk.Frame(self, padding=(5, 5))
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="CRIMINAL CASE MANAGEMENT", font=("Segoe UI", 14, "bold"), foreground="#00e676").pack(side=tk.LEFT)

        if self.session.role in ["Admin", "Supervisor", "Investigation Officer"]:
            ttk.Button(top_bar, text="⚙️ Update Status", command=self.update_status_dialog, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
            ttk.Button(top_bar, text="👮 Assign Officer", command=self.assign_officer_dialog).pack(side=tk.RIGHT, padx=5)

        ttk.Button(top_bar, text="📜 View Case Timeline", command=self.view_timeline).pack(side=tk.RIGHT, padx=5)

        # Table Frame
        table_frame = ttk.Frame(self, padding=(0, 10))
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("Case ID", "Case Number", "FIR Ref", "Title", "Category", "Priority", "Status", "Lead Officer", "Opened Date")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=tk.CENTER)

        self.tree.column("Case ID", width=60)
        self.tree.column("Title", width=220, anchor=tk.W)

        scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = self.db.fetch_all(GET_ALL_CASES)
        for r in rows:
            self.tree.insert("", tk.END, values=(
                r["case_id"],
                r["case_number"],
                r["fir_number"],
                r["case_title"],
                r["category_name"],
                r["priority"],
                r["status"],
                r["lead_officer_name"] or "Unassigned",
                str(r["opening_date"])
            ))

    def get_selected_case_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a case from the list.")
            return None
        return self.tree.item(selected[0])["values"][0]

    def view_timeline(self):
        cid = self.get_selected_case_id()
        if not cid:
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Case Audit Timeline - Case ID {cid}")
        dialog.geometry("620x420")
        dialog.configure(bg="#0f1219")

        rows = self.db.fetch_all(GET_CASE_TIMELINE, (cid,))
        if not rows:
            ttk.Label(dialog, text="No status history recorded yet for this case.", font=("Segoe UI", 11)).pack(pady=30)
            return

        txt = tk.Text(dialog, padding=15, font=("Consolas", 10), bg="#171c28", fg="#e0e6ed", insertbackground="white", relief="flat")
        txt.pack(fill=tk.BOTH, expand=True)
        for r in rows:
            txt.insert(tk.END, f"[{r['changed_at']}] Status: '{r['previous_status']}' -> '{r['new_status']}'\nBy User: {r['changed_by_user']} | Reason: {r['change_reason']}\n{'-'*65}\n")
        txt.configure(state="disabled")

    def update_status_dialog(self):
        cid = self.get_selected_case_id()
        if not cid:
            return

        dialog = tk.Toplevel(self)
        dialog.title("Update Case Status")
        dialog.geometry("380x220")
        dialog.configure(bg="#0f1219")

        ttk.Label(dialog, text="Select New Case Status:", font=("Segoe UI", 11, "bold")).pack(pady=(20, 5))
        cmb_status = ttk.Combobox(dialog, values=["Open", "In Progress", "Transferred", "Closed"])
        cmb_status.pack(pady=10)
        cmb_status.set("In Progress")

        def apply_update():
            new_st = cmb_status.get()
            cl_date = "2026-08-02" if new_st == "Closed" else None
            self.db.execute_query(UPDATE_CASE_STATUS, (new_st, cl_date, cid))
            messagebox.showinfo("Updated", f"Case status updated to '{new_st}'.")
            dialog.destroy()
            self.load_data()

        ttk.Button(dialog, text="Save Status Change", command=apply_update, style="Accent.TButton").pack(pady=15)

    def assign_officer_dialog(self):
        cid = self.get_selected_case_id()
        if not cid:
            return

        dialog = tk.Toplevel(self)
        dialog.title("Assign Lead Investigating Officer")
        dialog.geometry("380x220")
        dialog.configure(bg="#0f1219")

        ttk.Label(dialog, text="Lead Officer ID (1-50):", font=("Segoe UI", 11, "bold")).pack(pady=(20, 5))
        ent_oid = ttk.Entry(dialog, width=20)
        ent_oid.pack(pady=10)
        ent_oid.insert(0, "1")

        def apply_assign():
            oid = int(ent_oid.get())
            self.db.execute_query(ASSIGN_LEAD_OFFICER, (oid, cid))
            messagebox.showinfo("Assigned", f"Lead Officer ID {oid} assigned to Case ID {cid}.")
            dialog.destroy()
            self.load_data()

        ttk.Button(dialog, text="Confirm Assignment", command=apply_assign, style="Accent.TButton").pack(pady=15)
