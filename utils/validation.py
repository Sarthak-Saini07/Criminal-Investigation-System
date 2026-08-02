"""
Validation utilities for CICMS form inputs and data structures.
"""

import re
from datetime import datetime
from typing import Tuple, Optional

def validate_email(email: str) -> bool:
    """Validates email format."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip())) if email else False

def validate_phone(phone: str) -> bool:
    """Validates phone number format (digits, length 10-15)."""
    pattern = r"^\+?[0-9]{10,15}$"
    return bool(re.match(pattern, phone.strip())) if phone else False

def validate_national_id(national_id: str) -> bool:
    """Validates national ID format (alphanumeric, length 6-20)."""
    if not national_id or len(national_id.strip()) < 6:
        return False
    return True

def validate_date_str(date_str: str) -> Tuple[bool, Optional[str]]:
    """Validates if a string is a valid YYYY-MM-DD date."""
    if not date_str:
        return False, "Date cannot be empty."
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True, None
    except ValueError:
        return False, "Invalid date format. Expected YYYY-MM-DD."

def validate_required_fields(data: dict, required_keys: list) -> Tuple[bool, list]:
    """Checks if all required fields are non-empty in a dictionary."""
    missing = []
    for key in required_keys:
        val = data.get(key)
        if val is None or (isinstance(val, str) and not val.strip()):
            missing.append(key)
    return len(missing) == 0, missing
