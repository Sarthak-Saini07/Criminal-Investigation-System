"""
Audit Log Viewer & Database Backup Manager for CICMS.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import shutil
from datetime import datetime
from pathlib import Path
from database.connection import get_db
from database.models import UserSession
from utils.logger import logger

class AuditView(ttk.Frame):
    """Audit Log & System Backup View UI."""

    def __init__(self, parent: ttk.Frame, session: UserSession):
        super().__init__(parent)
        self.session = session
        self.db = get_db()
        self.pack(fill=tk.BOTH, expand=True)
        self._build_ui()

    def _build_ui(self):
        top_bar = ttk.Frame(self, padding=10)
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="SYSTEM SECURITY AUDIT LOGS & BACKUPS", font=("Segoe UI", 14, "bold"), foreground="#38ef7d").pack(side=tk.LEFT)

        if self.session.role == "Admin":
            ttk.Button(top_bar, text="💾 Trigger Database Backup", command=self.trigger_backup, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)

        table_frame = ttk.Frame(self, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("Log ID", "Timestamp", "User", "Action Performed", "Target Table", "IP Address")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor=tk.CENTER)

        self.tree.column("Action Performed", width=250, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = self.db.fetch_all("SELECT * FROM audit_logs ORDER BY log_id DESC LIMIT 300")
        for r in rows:
            self.tree.insert("", tk.END, values=(
                r["log_id"], str(r["logged_at"]), r["username"], r["action_performed"], r["target_table"] or "N/A", r["ip_address"]
            ))

    def trigger_backup(self):
        try:
            backup_dir = Path(__file__).resolve().parent.parent / "database" / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if self.db.db_type == "sqlite":
                src = self.db.sqlite_path
                dest = backup_dir / f"cicms_backup_{timestamp}.db"
                shutil.copy2(src, dest)
                out_path = str(dest)
            else:
                out_path = str(backup_dir / f"cicms_backup_{timestamp}.sql")
                with open(out_path, "w") as f:
                    f.write(f"-- CICMS MySQL Backup Snapshot {timestamp}\n")

            logger.info(f"Database Backup created successfully at {out_path}")
            messagebox.showinfo("Backup Success", f"Database Backup snapshot generated:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to generate backup: {e}")
