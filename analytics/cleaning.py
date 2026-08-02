"""
Data Cleaning & Transformation Engine using Pandas.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from database.connection import get_db
from utils.logger import logger

def load_and_clean_fir_data() -> pd.DataFrame:
    """Loads FIR & Case data into a Pandas DataFrame and applies data cleaning."""
    db = get_db()
    query = """
    SELECT 
        f.fir_id,
        f.fir_number,
        f.station_id,
        ps.station_name,
        ps.city,
        f.category_id,
        cc.category_name,
        cc.severity_level,
        f.complainant_name,
        f.incident_date,
        f.registration_date,
        f.status AS fir_status,
        c.case_id,
        c.case_number,
        c.priority,
        c.status AS case_status,
        c.opening_date,
        c.closing_date,
        c.lead_officer_id,
        CONCAT(o.first_name, ' ', o.last_name) AS officer_name
    FROM firs f
    JOIN police_stations ps ON f.station_id = ps.station_id
    JOIN crime_categories cc ON f.category_id = cc.category_id
    LEFT JOIN cases c ON c.fir_id = f.fir_id
    LEFT JOIN officers o ON c.lead_officer_id = o.officer_id
    """
    data = db.fetch_all(query)
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    # Date conversion & cleaning
    df["incident_date"] = pd.to_datetime(df["incident_date"], errors="coerce")
    df["registration_date"] = pd.to_datetime(df["registration_date"], errors="coerce")
    df["opening_date"] = pd.to_datetime(df["opening_date"], errors="coerce")
    df["closing_date"] = pd.to_datetime(df["closing_date"], errors="coerce")

    # Text sanitization
    df["station_name"] = df["station_name"].astype(str).str.strip()
    df["category_name"] = df["category_name"].astype(str).str.strip()
    df["city"] = df["city"].astype(str).str.strip()

    # Fill missing values
    df["case_status"] = df["case_status"].fillna("Open")
    df["priority"] = df["priority"].fillna("Medium")
    df["officer_name"] = df["officer_name"].fillna("Unassigned")

    return df
