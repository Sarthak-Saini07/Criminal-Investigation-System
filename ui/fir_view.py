"""
FIR Management View Component for CICMS.
Supports registering new FIRs, searching FIRs, updating status, and printing summary details.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database.connection import get_db
from database.queries import GET_ALL_FIRS, SEARCH_FIRS, INSERT_FIR, INSERT_CASE
from database.models import UserSession
from utils.helpers import generate_fir_number, generate_case_number, format_datetime
from utils.logger import logger

class FIRView(ttk.Frame):
    """FIR Management View UI."""

    def __init__(self, parent: ttk.Frame, session: UserSession):
        super().__init__(parent)
        self.session = session
        self.db = get_db()
        self.pack(fill=tk.BOTH, expand=True)
        self._build_ui()

    def _build_ui(self):
        # Header Controls Bar
        top_bar = ttk.Frame(self, padding=(5, 5))
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="FIRST INFORMATION REPORTS (FIR)", font=("Segoe UI", 14, "bold"), foreground="#00e676").pack(side=tk.LEFT)

        # Action Buttons (RBAC enabled)
        if self.session.role in ["Admin", "Police Officer", "Supervisor"]:
            btn_reg = ttk.Button(top_bar, text="➕ Register New FIR", command=self.open_register_dialog, style="Accent.TButton")
            btn_reg.pack(side=tk.LEFT, padx=20)

        # Search Box
        btn_search = ttk.Button(top_bar, text="🔍 Search", command=self.search_firs)
        btn_search.pack(side=tk.RIGHT, padx=5)
        self.ent_search = ttk.Entry(top_bar, width=28)
        self.ent_search.pack(side=tk.RIGHT, padx=5)

        # FIR Treeview Table Frame
        table_frame = ttk.Frame(self, padding=(0, 10))
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("FIR No.", "Complainant", "Category", "Station", "Incident Date", "Status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor=tk.CENTER)

        self.tree.column("Complainant", width=180, anchor=tk.W)
        self.tree.column("FIR No.", width=140, anchor=tk.W)

        scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_data()

    def load_data(self):
        """Populates Treeview with FIR records."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = self.db.fetch_all(GET_ALL_FIRS)
        for r in rows:
            self.tree.insert("", tk.END, values=(
                r["fir_number"],
                r["complainant_name"],
                r["category_name"],
                r["station_name"],
                str(r["incident_date"]),
                r["status"]
            ))

    def search_firs(self):
        query = f"%{self.ent_search.get().strip()}%"
        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = self.db.fetch_all(SEARCH_FIRS, (query, query, query))
        for r in rows:
            self.tree.insert("", tk.END, values=(
                r["fir_number"], r["complainant_name"], r["category_name"], r["station_name"], str(r["incident_date"]), r["status"]
            ))

    def open_register_dialog(self):
        """Dialog window to register a new FIR and open associated case."""
        dialog = tk.Toplevel(self)
        dialog.title("Register New First Information Report (FIR)")
        dialog.geometry("520x580")
        dialog.configure(bg="#0f1219")
        dialog.grab_set()

        ttk.Label(dialog, text="REGISTER NEW FIR", font=("Segoe UI", 14, "bold"), foreground="#00e676").pack(pady=15)

        form = ttk.Frame(dialog, padding=20, style="Card.TFrame")
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        ttk.Label(form, text="Complainant Full Name:", style="Card.TLabel").grid(row=0, column=0, sticky=tk.W, pady=8)
        ent_comp = ttk.Entry(form, width=35)
        ent_comp.grid(row=0, column=1, pady=8)

        ttk.Label(form, text="Police Station ID (1-10):", style="Card.TLabel").grid(row=1, column=0, sticky=tk.W, pady=8)
        ent_station = ttk.Entry(form, width=35)
        ent_station.insert(0, "1")
        ent_station.grid(row=1, column=1, pady=8)

        ttk.Label(form, text="Crime Category ID (1-12):", style="Card.TLabel").grid(row=2, column=0, sticky=tk.W, pady=8)
        ent_cat = ttk.Entry(form, width=35)
        ent_cat.insert(0, "1")
        ent_cat.grid(row=2, column=1, pady=8)

        ttk.Label(form, text="Incident Location:", style="Card.TLabel").grid(row=3, column=0, sticky=tk.W, pady=8)
        ent_loc = ttk.Entry(form, width=35)
        ent_loc.grid(row=3, column=1, pady=8)

        ttk.Label(form, text="Crime Details:", style="Card.TLabel").grid(row=4, column=0, sticky=tk.W, pady=8)
        txt_desc = tk.Text(form, width=35, height=5, bg="#171c28", fg="white", insertbackground="white")
        txt_desc.grid(row=4, column=1, pady=8)

        def save_fir():
            comp = ent_comp.get().strip()
            loc = ent_loc.get().strip()
            desc = txt_desc.get("1.0", tk.END).strip()
            sid = int(ent_station.get())
            cid = int(ent_cat.get())

            if not comp or not loc or not desc:
                messagebox.showerror("Error", "All required fields must be filled.")
                return

            seq = len(self.tree.get_children()) + 1
            fir_num = generate_fir_number(seq)
            case_num = generate_case_number(seq)
            now_str = "2026-08-02 12:00:00"

            fir_id = self.db.execute_query(INSERT_FIR, (fir_num, None, sid, cid, comp, now_str, loc, desc, "Registered"))
            self.db.execute_query(INSERT_CASE, (case_num, fir_id, f"Investigation of {fir_num}", "Medium", "Open", "2026-08-02", None, desc))

            logger.info(f"Registered FIR '{fir_num}' and initialized Case '{case_num}'.")
            messagebox.showinfo("Success", f"FIR Registered Successfully!\nFIR No: {fir_num}\nCase Opened: {case_num}")
            dialog.destroy()
            self.load_data()

        btn_save = ttk.Button(dialog, text="Submit & Auto-Open Case", command=save_fir, style="Accent.TButton")
        btn_save.pack(pady=15)
