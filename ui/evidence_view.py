"""
Evidence Vault & Chain of Custody Management for CICMS.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database.connection import get_db
from database.queries import GET_EVIDENCE_BY_CASE, GET_EVIDENCE_CHAIN, INSERT_EVIDENCE, INSERT_EVIDENCE_CHAIN
from database.models import UserSession
from utils.helpers import generate_evidence_code
from utils.logger import logger

class EvidenceView(ttk.Frame):
    """Evidence Vault View UI."""

    def __init__(self, parent: ttk.Frame, session: UserSession):
        super().__init__(parent)
        self.session = session
        self.db = get_db()
        self.pack(fill=tk.BOTH, expand=True)
        self._build_ui()

    def _build_ui(self):
        top_bar = ttk.Frame(self, padding=10)
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="EVIDENCE VAULT & CHAIN OF CUSTODY", font=("Segoe UI", 14, "bold"), foreground="#38ef7d").pack(side=tk.LEFT)

        ttk.Label(top_bar, text="Case ID:").pack(side=tk.LEFT, padx=(20, 5))
        self.ent_case = ttk.Entry(top_bar, width=10)
        self.ent_case.pack(side=tk.LEFT)
        self.ent_case.insert(0, "1")

        ttk.Button(top_bar, text="Load Evidence", command=self.load_data).pack(side=tk.LEFT, padx=5)

        ttk.Button(top_bar, text="View Chain of Custody", command=self.view_chain_dialog).pack(side=tk.RIGHT, padx=5)
        
        if self.session.role in ["Admin", "Police Officer", "Investigation Officer"]:
            ttk.Button(top_bar, text="+ Deposit New Evidence", command=self.add_evidence_dialog, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)

        table_frame = ttk.Frame(self, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("Evidence ID", "Code", "Type", "Description", "Storage Vault", "Status", "Officer")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor=tk.CENTER)

        self.tree.column("Description", width=250, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        case_id = self.ent_case.get().strip() or "1"
        rows = self.db.fetch_all(GET_EVIDENCE_BY_CASE, (case_id,))
        for r in rows:
            self.tree.insert("", tk.END, values=(
                r["evidence_id"], r["evidence_code"], r["evidence_type"], r["description"], r["storage_location"], r["status"], r["officer_name"] or "N/A"
            ))

    def get_selected_evidence_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an evidence record.")
            return None
        return self.tree.item(selected[0])["values"][0]

    def view_chain_dialog(self):
        ev_id = self.get_selected_evidence_id()
        if not ev_id:
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Chain of Custody Audit Log - Evidence ID {ev_id}")
        dialog.geometry("650x350")

        rows = self.db.fetch_all(GET_EVIDENCE_CHAIN, (ev_id,))
        txt = tk.Text(dialog, padding=10, font=("Consolas", 10))
        txt.pack(fill=tk.BOTH, expand=True)

        for r in rows:
            txt.insert(tk.END, f"[{r['transfer_date']}] Transferred from: '{r['transferred_from']}' -> '{r['transferred_to']}'\nPurpose: {r['purpose']} | Officer In Charge: {r['officer_name'] or 'N/A'}\n{'-'*65}\n")
        txt.configure(state="disabled")

    def add_evidence_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Deposit New Evidence Item")
        dialog.geometry("400x400")

        ttk.Label(dialog, text="Case ID:").pack(pady=5)
        ent_cid = ttk.Entry(dialog)
        ent_cid.pack()
        ent_cid.insert(0, self.ent_case.get())

        ttk.Label(dialog, text="Evidence Type:").pack(pady=5)
        cmb_type = ttk.Combobox(dialog, values=['Physical', 'Digital', 'DNA', 'Fingerprint', 'Weapon', 'Vehicle', 'Document'])
        cmb_type.pack()
        cmb_type.set("Physical")

        ttk.Label(dialog, text="Description:").pack(pady=5)
        ent_desc = ttk.Entry(dialog, width=35)
        ent_desc.pack()

        ttk.Label(dialog, text="Storage Location / Vault Room:").pack(pady=5)
        ent_loc = ttk.Entry(dialog, width=35)
        ent_loc.pack()
        ent_loc.insert(0, "Vault Room B-12")

        def save():
            cid = ent_cid.get()
            etype = cmb_type.get()
            desc = ent_desc.get().strip()
            loc = ent_loc.get().strip()

            if not desc:
                messagebox.showerror("Error", "Description is required.")
                return

            seq = len(self.tree.get_children()) + 1
            code = generate_evidence_code(seq)
            now_str = "2026-08-02 12:00:00"

            ev_id = self.db.execute_query(INSERT_EVIDENCE, (code, cid, etype, desc, now_str, self.session.officer_id or 1, loc, "In Vault"))
            self.db.execute_query(INSERT_EVIDENCE_CHAIN, (ev_id, "Field Crime Scene", loc, now_str, "Initial Custody Vault Deposit", self.session.officer_id or 1))

            logger.info(f"Registered Evidence '{code}' in Vault.")
            messagebox.showinfo("Success", f"Evidence Registered!\nItem Code: {code}")
            dialog.destroy()
            self.load_data()

        ttk.Button(dialog, text="Deposit to Vault", command=save, style="Accent.TButton").pack(pady=15)
