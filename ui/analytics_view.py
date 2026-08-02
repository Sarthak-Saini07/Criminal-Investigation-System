"""
Analytics & Crime Prediction Dashboard View for CICMS.
Embeds Matplotlib figure inside Tkinter canvas with interactive metric cards and decision insights.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

from analytics.cleaning import load_and_clean_fir_data
from analytics.preprocessing import preprocess_case_features
from analytics.kpi import compute_all_kpis
from analytics.statistics import numpy_linear_regression_predict
from dashboard.charts import create_analytics_figure
from dashboard.dashboard import generate_business_insights
from database.models import UserSession

class AnalyticsView(ttk.Frame):
    """Analytics & Insights Dashboard View UI."""

    def __init__(self, parent: ttk.Frame, session: UserSession):
        super().__init__(parent)
        self.session = session
        self.pack(fill=tk.BOTH, expand=True)
        self._load_and_process_data()
        self._build_ui()

    def _load_and_process_data(self):
        raw_df = load_and_clean_fir_data()
        self.df = preprocess_case_features(raw_df)
        self.kpis = compute_all_kpis(self.df)
        self.insights = generate_business_insights(self.kpis, self.df)

    def _build_ui(self):
        # Header Bar
        top_bar = ttk.Frame(self, padding=(5, 5))
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="DEPARTMENT ANALYTICS & INSIGHTS", font=("Segoe UI", 14, "bold"), foreground="#00e676").pack(side=tk.LEFT)
        ttk.Button(top_bar, text="🔄 Refresh Analytics", command=self.refresh_analytics).pack(side=tk.RIGHT)

        # Tabbed Container
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tab 1: Visual Analytics Dashboard
        tab_dash = ttk.Frame(notebook, padding=10)
        notebook.add(tab_dash, text="📊 Visual Analytics Dashboard")

        # KPI Stat Cards Row
        cards_frame = ttk.Frame(tab_dash)
        cards_frame.pack(fill=tk.X, pady=(0, 10))

        kpi_list = [
            ("TOTAL FIRS REGISTERED", str(self.kpis.get("total_firs", 0)), "#00b0ff", "📜"),
            ("CASE CLEARANCE RATE", f"{self.kpis.get('clearance_rate_pct', 0)}%", "#00e676", "✅"),
            ("AVG RESOLUTION TIME", f"{self.kpis.get('avg_resolution_days', 0)} Days", "#ff9100", "⏱️"),
            ("COURT CONVICTION RATE", f"{self.kpis.get('conviction_rate_pct', 0)}%", "#e040fb", "⚖️")
        ]

        for title, val, color, icon in kpi_list:
            card = ttk.Frame(cards_frame, padding=12, style="Card.TFrame")
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)
            
            top_row = ttk.Frame(card, style="Card.TFrame")
            top_row.pack(fill=tk.X)
            ttk.Label(top_row, text=icon, font=("Segoe UI", 14), style="Card.TLabel").pack(side=tk.LEFT)
            ttk.Label(top_row, text=title, font=("Segoe UI", 8, "bold"), foreground="#90a4ae", style="Card.TLabel").pack(side=tk.RIGHT)
            
            ttk.Label(card, text=val, font=("Segoe UI", 18, "bold"), foreground=color, style="Card.TLabel").pack(anchor=tk.W, pady=(6, 0))

        # Embedded Matplotlib Figure Canvas
        canvas_frame = ttk.Frame(tab_dash, style="Card.TFrame")
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        fig = create_analytics_figure(self.df)
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Tab 2: Decision Insights & Strategic Recommendations
        tab_insights = ttk.Frame(notebook, padding=10)
        notebook.add(tab_insights, text="💡 Decision Insights & Recommendations")

        txt_ins = tk.Text(tab_insights, padding=15, font=("Segoe UI", 10), bg="#171c28", fg="#e0e6ed", insertbackground="white", relief="flat")
        txt_ins.pack(fill=tk.BOTH, expand=True)

        for ins in self.insights:
            txt_ins.insert(tk.END, f"📌 METRIC AREA: {ins['metric']}\n", "header")
            txt_ins.insert(tk.END, f"• Observation: ", "bullet_title")
            txt_ins.insert(tk.END, f"{ins['observation']}\n")
            txt_ins.insert(tk.END, f"• Analysis: ", "bullet_title")
            txt_ins.insert(tk.END, f"{ins['analysis']}\n")
            txt_ins.insert(tk.END, f"• Business Insight: ", "bullet_title")
            txt_ins.insert(tk.END, f"{ins['business_insight']}\n")
            txt_ins.insert(tk.END, f"• Possible Cause: ", "bullet_title")
            txt_ins.insert(tk.END, f"{ins['possible_cause']}\n")
            txt_ins.insert(tk.END, f"• Recommendation: ", "bullet_title")
            txt_ins.insert(tk.END, f"{ins['recommendation']}\n")
            txt_ins.insert(tk.END, f"• Expected Impact: ", "bullet_title")
            txt_ins.insert(tk.END, f"{ins['expected_impact']}\n\n{'-'*90}\n\n")

        txt_ins.tag_configure("header", font=("Segoe UI", 11, "bold"), foreground="#00e676")
        txt_ins.tag_configure("bullet_title", font=("Segoe UI", 10, "bold"), foreground="#00b0ff")
        txt_ins.configure(state="disabled")

    def refresh_analytics(self):
        self._load_and_process_data()
        messagebox.showinfo("Refreshed", "Analytics and Insights updated with latest database records.")
