"""
Matplotlib Dashboard Chart Generator for CICMS Desktop Application.
Renders professional, dark-themed police analytics subplots.
"""

import matplotlib
try:
    matplotlib.use("TkAgg")  # Preferred for Tkinter desktop GUI
except Exception:
    matplotlib.use("Agg")    # Headless fallback for batch exports
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Tuple, List
from analytics.statistics import compute_moving_average, numpy_linear_regression_predict

# Modern Dark Theme Palette
plt.style.use("dark_background")
PALETTE = ["#00b0ff", "#00e676", "#ff9100", "#ff1744", "#e040fb", "#7c4dff", "#64ffda", "#ffd600"]
BG_COLOR = "#0f1219"
CARD_BG = "#1f2636"
TEXT_COLOR = "#ffffff"

def create_analytics_figure(df: pd.DataFrame) -> plt.Figure:
    """Creates a comprehensive 4-subplot Matplotlib analytics dashboard figure."""
    fig = plt.figure(figsize=(10, 6.2), facecolor=BG_COLOR)
    fig.subplots_adjust(hspace=0.42, wspace=0.28, top=0.92, bottom=0.08, left=0.08, right=0.95)

    if df.empty:
        ax = fig.add_subplot(111, facecolor=CARD_BG)
        ax.text(0.5, 0.5, "No Data Available for Analytics", color="white", fontsize=16, ha="center")
        return fig

    # 1. Crime Category Share (Donut Chart)
    ax1 = fig.add_subplot(2, 2, 1, facecolor=CARD_BG)
    cat_counts = df["category_name"].value_counts().head(5)
    wedges, texts, autotexts = ax1.pie(
        cat_counts, labels=[c[:12] for c in cat_counts.index], autopct="%1.0f%%",
        colors=PALETTE[:len(cat_counts)], startangle=140, pctdistance=0.75,
        textprops=dict(color=TEXT_COLOR, fontsize=8)
    )
    centre_circle = plt.Circle((0,0), 0.50, fc=CARD_BG)
    ax1.add_artist(centre_circle)
    plt.setp(autotexts, size=8, weight="bold", color="white")
    ax1.set_title("Crime Category Share", color=TEXT_COLOR, fontsize=11, fontweight="bold", pad=8)

    # 2. Monthly Crime Trend & Moving Average
    ax2 = fig.add_subplot(2, 2, 2, facecolor=CARD_BG)
    monthly_df = df.set_index("incident_date").resample("ME")["fir_id"].count().reset_index()
    if not monthly_df.empty and len(monthly_df) > 1:
        x_vals = range(len(monthly_df))
        y_vals = monthly_df["fir_id"].values
        ax2.plot(x_vals, y_vals, marker="o", color="#00e676", label="FIR Volume", linewidth=2, markersize=4)
        ax2.fill_between(x_vals, y_vals, color="#00e676", alpha=0.15)
        
        if len(y_vals) >= 3:
            ma = compute_moving_average(y_vals, 3)
            ax2.plot(range(2, len(y_vals)), ma, color="#ff9100", linestyle="--", label="3-Mo Avg")
            
        ax2.set_title("Monthly FIR Trend & Moving Avg", color=TEXT_COLOR, fontsize=11, fontweight="bold", pad=8)
        ax2.set_xlabel("Month", color="#90a4ae", fontsize=8.5)
        ax2.set_ylabel("Count", color="#90a4ae", fontsize=8.5)
        ax2.legend(fontsize=7.5, loc="upper left")
        ax2.grid(True, linestyle=":", alpha=0.25, color="#546e7a")

    # 3. Case Status by Station (Stacked Bar)
    ax3 = fig.add_subplot(2, 2, 3, facecolor=CARD_BG)
    st_df = df.groupby(["station_name", "case_status"]).size().unstack(fill_value=0)
    top_st = st_df.head(5)
    solved = top_st["Closed"] if "Closed" in top_st.columns else pd.Series(0, index=top_st.index)
    open_c = top_st["Open"] if "Open" in top_st.columns else pd.Series(0, index=top_st.index)

    ax3.bar(top_st.index, solved, label="Closed", color="#00e676", width=0.55)
    ax3.bar(top_st.index, open_c, bottom=solved, label="Open", color="#ff1744", width=0.55)
    
    ax3.set_title("Status by Station", color=TEXT_COLOR, fontsize=11, fontweight="bold", pad=8)
    ax3.set_xticks(range(len(top_st)))
    ax3.set_xticklabels([s.split()[0] for s in top_st.index], rotation=15, fontsize=7.5, color="#90a4ae")
    ax3.legend(fontsize=7.5)
    ax3.grid(True, linestyle=":", alpha=0.25, color="#546e7a")

    # 4. NumPy Linear Regression Crime Forecast
    ax4 = fig.add_subplot(2, 2, 4, facecolor=CARD_BG)
    if not monthly_df.empty:
        counts = monthly_df["fir_id"].values.tolist()
        hist_pred, future_pred, r2 = numpy_linear_regression_predict(counts, future_steps=4)
        
        n_hist = len(counts)
        ax4.plot(range(1, n_hist + 1), counts, label="Actual", color="#00e676", marker="o", markersize=3)
        ax4.plot(range(1, n_hist + 1), hist_pred, label="OLS Fit", color="#00b0ff", linestyle="--")
        ax4.plot(range(n_hist + 1, n_hist + 5), future_pred, label="Forecast", color="#ff1744", marker="s", linestyle=":")
        
        ax4.set_title(f"NumPy Linear Forecast (R²={r2:.2f})", color=TEXT_COLOR, fontsize=11, fontweight="bold", pad=8)
        ax4.set_xlabel("Month", color="#90a4ae", fontsize=8.5)
        ax4.legend(fontsize=7.5)
        ax4.grid(True, linestyle=":", alpha=0.25, color="#546e7a")

    return fig
