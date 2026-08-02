"""
Helper utilities for CICMS.
Includes password hashing, reference generator functions, and date formatting.
"""

import hashlib
import os
import random
import string
from datetime import datetime, date
from typing import Union

SALT = "CICMS_SECURE_POLICE_SALT_2026"

def hash_password(password: str) -> str:
    """Hashes a plain password using SHA-256 with a salt."""
    salted = f"{password}{SALT}".encode("utf-8")
    return hashlib.sha256(salted).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored hash."""
    return hash_password(plain_password) == hashed_password

def generate_fir_number(seq_num: int) -> str:
    """Generates a standardized FIR Number format (FIR-YYYY-XXXXX)."""
    year = datetime.now().year
    return f"FIR-{year}-{seq_num:05d}"

def generate_case_number(seq_num: int) -> str:
    """Generates a standardized Case Number format (CASE-YYYY-XXXXX)."""
    year = datetime.now().year
    return f"CASE-{year}-{seq_num:05d}"

def generate_evidence_code(seq_num: int) -> str:
    """Generates a standardized Evidence Item Code format (EVD-YYYY-XXXXX)."""
    year = datetime.now().year
    return f"EVD-{year}-{seq_num:05d}"

def format_date(dt: Union[datetime, date, str]) -> str:
    """Formats datetime or date object to YYYY-MM-DD string."""
    if isinstance(dt, (datetime, date)):
        return dt.strftime("%Y-%m-%d")
    return str(dt)

def format_datetime(dt: Union[datetime, str]) -> str:
    """Formats datetime object to YYYY-MM-DD HH:MM:SS string."""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)

def sanitize_string(text: str) -> str:
    """Sanitizes user input string."""
    if not text:
        return ""
    return text.strip()
