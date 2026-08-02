"""
Feature Engineering and Data Preprocessing for CICMS.
Calculates resolution durations, time periods, and grouping features.
"""

import pandas as pd
import numpy as np

def preprocess_case_features(df: pd.DataFrame) -> pd.DataFrame:
    """Applies feature engineering to the cleaned DataFrame."""
    if df.empty:
        return df

    # 1. Calculate Investigation Duration in Days
    df["resolution_days"] = (df["closing_date"] - df["opening_date"]).dt.days
    # For open cases, calculate days elapsed up to current date
    df["days_elapsed"] = (pd.Timestamp.now() - df["opening_date"]).dt.days
    df["duration_days"] = np.where(df["resolution_days"].notnull(), df["resolution_days"], df["days_elapsed"])
    df["duration_days"] = df["duration_days"].clip(lower=0)

    # 2. Solved vs Unsolved Binary Indicator
    df["is_solved"] = np.where(df["case_status"] == "Closed", 1, 0)

    # 3. Monthly & Daily Time Grouping
    df["year_month"] = df["incident_date"].dt.to_period("M").astype(str)
    df["month_name"] = df["incident_date"].dt.strftime("%b %Y")
    df["day_of_week"] = df["incident_date"].dt.day_name()

    return df
