"""
Data Models for CICMS domain objects.
Provides structured Python object representations of database tables.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, date

@dataclass
class PoliceStation:
    station_id: Optional[int]
    station_code: str
    station_name: str
    jurisdiction_zone: str
    address: str
    city: str
    contact_number: str
    email: Optional[str] = None

@dataclass
class Officer:
    officer_id: Optional[int]
    badge_number: str
    first_name: str
    last_name: str
    rank_title: str
    station_id: int
    department_id: int
    phone: str
    email: str
    join_date: date
    is_active: bool = True

@dataclass
class UserSession:
    user_id: int
    username: str
    role: str
    officer_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    rank_title: Optional[str] = None
    station_id: Optional[int] = None

@dataclass
class FIRModel:
    fir_id: Optional[int]
    fir_number: str
    station_id: int
    category_id: int
    complainant_name: str
    incident_date: str
    incident_location: str
    crime_description: str
    status: str = "Registered"

@dataclass
class CaseModel:
    case_id: Optional[int]
    case_number: str
    fir_id: int
    case_title: str
    priority: str
    status: str
    opening_date: str
    lead_officer_id: Optional[int] = None
    closing_date: Optional[str] = None
    summary: Optional[str] = None

@dataclass
class EvidenceModel:
    evidence_id: Optional[int]
    evidence_code: str
    case_id: int
    evidence_type: str
    description: str
    collected_at: str
    storage_location: str
    collected_by_officer_id: Optional[int] = None
    status: str = "In Vault"
