"""
Report Export Center View for CICMS.
Supports exporting PDF summaries, Excel workbooks, and CSV raw data dumps.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from reports.excel_report import generate_excel_report
from reports.csv_report import export_table_to_csv
from reports.pdf_summary import generate_pdf_summary_report
from database.models import UserSession
from utils.logger import logger

class ReportsView(ttk.Frame):
    """Report Center View UI."""

    def __init__(self, parent: ttk.Frame, session: UserSession):
        super().__init__(parent)
        self.session = session
        self.pack(fill=tk.BOTH, expand=True)
        self._build_ui()

    def _build_ui(self):
        top_bar = ttk.Frame(self, padding=(5, 5))
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="AUTOMATED REPORT GENERATION CENTER", font=("Segoe UI", 14, "bold"), foreground="#00e676").pack(side=tk.LEFT)

        container = ttk.Frame(self, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Excel Export Box
        box_excel = ttk.Frame(container, padding=20, style="Card.TFrame")
        box_excel.pack(fill=tk.X, pady=10)
        ttk.Label(box_excel, text="📊 Excel Master Report Exporter (openpyxl)", font=("Segoe UI", 12, "bold"), foreground="#00b0ff", style="Card.TLabel").pack(anchor=tk.W, pady=(0, 6))
        ttk.Label(box_excel, text="Generates a styled multi-tab Excel workbook containing executive KPI summaries, FIR registers, and Case logs.", style="Muted.TLabel").pack(anchor=tk.W, pady=(0, 12))
        ttk.Button(box_excel, text="Generate Excel Master Report (.xlsx)", command=self.export_excel, style="Accent.TButton").pack(anchor=tk.W)

        # PDF Export Box
        box_pdf = ttk.Frame(container, padding=20, style="Card.TFrame")
        box_pdf.pack(fill=tk.X, pady=10)
        ttk.Label(box_pdf, text="📄 Executive PDF Summary Report", font=("Segoe UI", 12, "bold"), foreground="#00e676", style="Card.TLabel").pack(anchor=tk.W, pady=(0, 6))
        ttk.Label(box_pdf, text="Generates printable PDF executive summary document with clearance rate metrics and critical investigation status.", style="Muted.TLabel").pack(anchor=tk.W, pady=(0, 12))
        ttk.Button(box_pdf, text="Generate PDF Executive Summary (.pdf)", command=self.export_pdf, style="Accent.TButton").pack(anchor=tk.W)

        # CSV Export Box
        box_csv = ttk.Frame(container, padding=20, style="Card.TFrame")
        box_csv.pack(fill=tk.X, pady=10)
        ttk.Label(box_csv, text="📁 Raw CSV Data Exporter", font=("Segoe UI", 12, "bold"), foreground="#ff9100", style="Card.TLabel").pack(anchor=tk.W, pady=(0, 6))
        ttk.Label(box_csv, text="Exports raw database tables for external auditing or data pipeline integration.", style="Muted.TLabel").pack(anchor=tk.W, pady=(0, 12))
        
        frame_csv_btns = ttk.Frame(box_csv, style="Card.TFrame")
        frame_csv_btns.pack(anchor=tk.W)
        ttk.Button(frame_csv_btns, text="Export FIRs CSV", command=lambda: self.export_csv("firs")).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_csv_btns, text="Export Cases CSV", command=lambda: self.export_csv("cases")).pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_csv_btns, text="Export Evidence CSV", command=lambda: self.export_csv("evidence")).pack(side=tk.LEFT, padx=10)

    def export_excel(self):
        fpath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")], initialfile="CICMS_Master_Report.xlsx")
        if fpath:
            out = generate_excel_report(fpath)
            messagebox.showinfo("Report Exported", f"Excel Master Report saved successfully to:\n{out}")

    def export_pdf(self):
        fpath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")], initialfile="CICMS_Executive_Summary.pdf")
        if fpath:
            out = generate_pdf_summary_report(fpath)
            messagebox.showinfo("Report Exported", f"PDF Executive Summary saved successfully to:\n{out}")

    def export_csv(self, table_name: str):
        fpath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], initialfile=f"CICMS_{table_name}.csv")
        if fpath:
            out = export_table_to_csv(table_name, fpath)
            messagebox.showinfo("Report Exported", f"CSV dump saved successfully to:\n{out}")
