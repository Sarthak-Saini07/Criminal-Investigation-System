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
    """Creates a comprehensive 6-subplot Matplotlib analytics dashboard figure."""
    fig = plt.figure(figsize=(13, 7.5), facecolor=BG_COLOR)
    fig.subplots_adjust(hspace=0.45, wspace=0.32, top=0.92, bottom=0.08, left=0.06, right=0.96)

    if df.empty:
        ax = fig.add_subplot(111, facecolor=CARD_BG)
        ax.text(0.5, 0.5, "No Data Available for Analytics", color="white", fontsize=16, ha="center")
        return fig

    # -------------------------------------------------------------------------
    # Subplot 1: Crime Category Share (Donut Chart)
    # -------------------------------------------------------------------------
    ax1 = fig.add_subplot(2, 3, 1, facecolor=CARD_BG)
    cat_counts = df["category_name"].value_counts().head(5)
    wedges, texts, autotexts = ax1.pie(
        cat_counts, labels=[c[:12] for c in cat_counts.index], autopct="%1.0f%%",
        colors=PALETTE[:len(cat_counts)], startangle=140, pctdistance=0.75,
        textprops=dict(color=TEXT_COLOR, fontsize=7.5)
    )
    # Make it a Donut Chart
    centre_circle = plt.Circle((0,0), 0.50, fc=CARD_BG)
    ax1.add_artist(centre_circle)
    plt.setp(autotexts, size=7.5, weight="bold", color="white")
    ax1.set_title("Crime Category Share", color=TEXT_COLOR, fontsize=10, fontweight="bold", pad=8)

    # -------------------------------------------------------------------------
    # Subplot 2: Monthly Crime Trend & Moving Average
    # -------------------------------------------------------------------------
    ax2 = fig.add_subplot(2, 3, 2, facecolor=CARD_BG)
    monthly_df = df.set_index("incident_date").resample("ME")["fir_id"].count().reset_index()
    if not monthly_df.empty and len(monthly_df) > 1:
        x_vals = range(len(monthly_df))
        y_vals = monthly_df["fir_id"].values
        ax2.plot(x_vals, y_vals, marker="o", color="#00e676", label="FIR Volume", linewidth=2, markersize=4)
        ax2.fill_between(x_vals, y_vals, color="#00e676", alpha=0.15)
        
        if len(y_vals) >= 3:
            ma = compute_moving_average(y_vals, 3)
            ax2.plot(range(2, len(y_vals)), ma, color="#ff9100", linestyle="--", label="3-Mo Avg")
            
        ax2.set_title("Monthly FIR Trend & Moving Avg", color=TEXT_COLOR, fontsize=10, fontweight="bold", pad=8)
        ax2.set_xlabel("Month", color="#90a4ae", fontsize=8)
        ax2.set_ylabel("Count", color="#90a4ae", fontsize=8)
        ax2.legend(fontsize=7, loc="upper left")
        ax2.grid(True, linestyle=":", alpha=0.25, color="#546e7a")

    # -------------------------------------------------------------------------
    # Subplot 3: Case Status by Station (Stacked Bar)
    # -------------------------------------------------------------------------
    ax3 = fig.add_subplot(2, 3, 3, facecolor=CARD_BG)
    st_df = df.groupby(["station_name", "case_status"]).size().unstack(fill_value=0)
    top_st = st_df.head(5)
    solved = top_st["Closed"] if "Closed" in top_st.columns else pd.Series(0, index=top_st.index)
    open_c = top_st["Open"] if "Open" in top_st.columns else pd.Series(0, index=top_st.index)

    ax3.bar(top_st.index, solved, label="Closed", color="#00e676", width=0.55)
    ax3.bar(top_st.index, open_c, bottom=solved, label="Open", color="#ff1744", width=0.55)
    
    ax3.set_title("Status by Station", color=TEXT_COLOR, fontsize=10, fontweight="bold", pad=8)
    ax3.set_xticklabels([s.split()[0] for s in top_st.index], rotation=20, fontsize=7, color="#90a4ae")
    ax3.legend(fontsize=7)
    ax3.grid(True, linestyle=":", alpha=0.25, color="#546e7a")

    # -------------------------------------------------------------------------
    # Subplot 4: Average Investigation Time (Box Plot)
    # -------------------------------------------------------------------------
    ax4 = fig.add_subplot(2, 3, 4, facecolor=CARD_BG)
    dur_data = []
    cat_names = []
    for cat, group in df.groupby("category_name"):
        valid_dur = group["duration_days"].dropna()
        if len(valid_dur) > 0:
            dur_data.append(valid_dur.values)
            cat_names.append(cat[:10])

    if dur_data:
        bp = ax4.boxplot(dur_data[:4], patch_artist=True, labels=cat_names[:4])
        for patch in bp['boxes']:
            patch.set_facecolor('#00b0ff')
            patch.set_alpha(0.6)
        ax4.set_title("Investigation Duration Boxplot", color=TEXT_COLOR, fontsize=10, fontweight="bold", pad=8)
        ax4.set_ylabel("Days", color="#90a4ae", fontsize=8)
        ax4.tick_params(axis='x', rotation=15, labelsize=7)
        ax4.grid(True, linestyle=":", alpha=0.25, color="#546e7a")

    # -------------------------------------------------------------------------
    # Subplot 5: Crime Severity vs Resolution Time (Scatter)
    # -------------------------------------------------------------------------
    ax5 = fig.add_subplot(2, 3, 5, facecolor=CARD_BG)
    sample_df = df.dropna(subset=["duration_days", "severity_level"]).sample(min(150, len(df)))
    scatter = ax5.scatter(
        sample_df["severity_level"] + np.random.normal(0, 0.04, len(sample_df)),
        sample_df["duration_days"],
        c=sample_df["severity_level"], cmap="winter", alpha=0.7, edgecolors="none", s=25
    )
    ax5.set_title("Severity vs Resolution Days", color=TEXT_COLOR, fontsize=10, fontweight="bold", pad=8)
    ax5.set_xlabel("Severity (1-5)", color="#90a4ae", fontsize=8)
    ax5.set_ylabel("Days", color="#90a4ae", fontsize=8)
    ax5.grid(True, linestyle=":", alpha=0.25, color="#546e7a")

    # -------------------------------------------------------------------------
    # Subplot 6: NumPy Linear Regression Crime Forecast
    # -------------------------------------------------------------------------
    ax6 = fig.add_subplot(2, 3, 6, facecolor=CARD_BG)
    if not monthly_df.empty:
        counts = monthly_df["fir_id"].values.tolist()
        hist_pred, future_pred, r2 = numpy_linear_regression_predict(counts, future_steps=4)
        
        n_hist = len(counts)
        ax6.plot(range(1, n_hist + 1), counts, label="Actual", color="#00e676", marker="o", markersize=3)
        ax6.plot(range(1, n_hist + 1), hist_pred, label="OLS Fit", color="#00b0ff", linestyle="--")
        ax6.plot(range(n_hist + 1, n_hist + 5), future_pred, label="Forecast", color="#ff1744", marker="s", linestyle=":")
        
        ax6.set_title(f"NumPy Linear Forecast (R²={r2:.2f})", color=TEXT_COLOR, fontsize=10, fontweight="bold", pad=8)
        ax6.set_xlabel("Month", color="#90a4ae", fontsize=8)
        ax6.legend(fontsize=7)
        ax6.grid(True, linestyle=":", alpha=0.25, color="#546e7a")

    return fig
