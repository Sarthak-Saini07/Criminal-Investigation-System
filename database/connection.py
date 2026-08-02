"""
Database Connection Manager for CICMS.
Supports MySQL connection with automatic SQLite fallback for environment compatibility.
"""

import os
import sqlite3
import configparser
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from utils.logger import logger

# Config path
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "config.ini"

class DatabaseManager:
    """Singleton Database Connection Manager."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.config = configparser.ConfigParser()
        if CONFIG_PATH.exists():
            self.config.read(CONFIG_PATH)
        else:
            logger.warning("config.ini not found, using default fallback settings.")

        self.db_type = "sqlite"  # Default fallback
        self.connection = None
        self.connect()

    def connect(self):
        """Attempts connection to MySQL; falls back to SQLite if MySQL fails or configuration specifies."""
        use_fallback = self.config.getboolean("database", "use_sqlite_fallback", fallback=True)
        host = self.config.get("database", "host", fallback="localhost")
        port = self.config.getint("database", "port", fallback=3306)
        user = self.config.get("database", "user", fallback="root")
        password = self.config.get("database", "password", fallback="root")
        db_name = self.config.get("database", "database", fallback="cicms_db")

        if not use_fallback:
            try:
                import mysql.connector
                self.connection = mysql.connector.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=db_name,
                    autocommit=True
                )
                self.db_type = "mysql"
                logger.info(f"Connected to MySQL Database: {db_name}@{host}:{port}")
                return
            except Exception as e:
                logger.warning(f"MySQL Connection failed: {e}. Falling back to SQLite.")

        # SQLite Fallback setup
        sqlite_rel_path = self.config.get("database", "sqlite_db_path", fallback="database/cicms.db")
        sqlite_abs_path = Path(__file__).resolve().parent.parent / sqlite_rel_path
        sqlite_abs_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.sqlite_path = str(sqlite_abs_path)
        self.connection = sqlite3.connect(self.sqlite_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.db_type = "sqlite"
        logger.info(f"Connected to SQLite Database: {self.sqlite_path}")
        self._ensure_sqlite_schema()

    def _ensure_sqlite_schema(self):
        """Creates SQLite tables if using SQLite fallback."""
        cursor = self.connection.cursor()
        
        # SQLite dialect schema
        schema_sql = """
        CREATE TABLE IF NOT EXISTS police_stations (
            station_id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL UNIQUE,
            station_name TEXT NOT NULL,
            jurisdiction_zone TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS departments (
            department_id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_name TEXT NOT NULL UNIQUE,
            description TEXT,
            head_officer_name TEXT
        );

        CREATE TABLE IF NOT EXISTS officers (
            officer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            badge_number TEXT NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            rank_title TEXT NOT NULL,
            station_id INTEGER NOT NULL,
            department_id INTEGER NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            join_date DATE NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (station_id) REFERENCES police_stations(station_id),
            FOREIGN KEY (department_id) REFERENCES departments(department_id)
        );

        CREATE TABLE IF NOT EXISTS user_logins (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            officer_id INTEGER,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (officer_id) REFERENCES officers(officer_id)
        );

        CREATE TABLE IF NOT EXISTS crime_categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE,
            severity_level INTEGER NOT NULL,
            ipc_section TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_number TEXT NOT NULL UNIQUE,
            complainant_name TEXT NOT NULL,
            complainant_phone TEXT NOT NULL,
            complainant_address TEXT NOT NULL,
            incident_date TIMESTAMP NOT NULL,
            incident_location TEXT NOT NULL,
            details TEXT NOT NULL,
            station_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS firs (
            fir_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fir_number TEXT NOT NULL UNIQUE,
            complaint_id INTEGER,
            station_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            complainant_name TEXT NOT NULL,
            incident_date TIMESTAMP NOT NULL,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            incident_location TEXT NOT NULL,
            crime_description TEXT NOT NULL,
            status TEXT DEFAULT 'Registered'
        );

        CREATE TABLE IF NOT EXISTS cases (
            case_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT NOT NULL UNIQUE,
            fir_id INTEGER NOT NULL UNIQUE,
            case_title TEXT NOT NULL,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Open',
            opening_date DATE NOT NULL,
            closing_date DATE,
            lead_officer_id INTEGER,
            summary TEXT
        );

        CREATE TABLE IF NOT EXISTS case_assignments (
            assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            officer_id INTEGER NOT NULL,
            assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            role_in_case TEXT DEFAULT 'Investigating Officer',
            status TEXT DEFAULT 'Active'
        );

        CREATE TABLE IF NOT EXISTS case_status_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            previous_status TEXT,
            new_status TEXT NOT NULL,
            change_reason TEXT,
            changed_by_user TEXT,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS suspects (
            suspect_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            alias_name TEXT,
            dob DATE,
            gender TEXT,
            national_id TEXT,
            address TEXT,
            height_cm INTEGER,
            build TEXT,
            arrest_status TEXT DEFAULT 'Under Investigation',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS criminal_histories (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            suspect_id INTEGER NOT NULL,
            prior_convictions_count INTEGER DEFAULT 0,
            past_offenses TEXT,
            gang_affiliation TEXT,
            risk_level TEXT DEFAULT 'Low'
        );

        CREATE TABLE IF NOT EXISTS victims (
            victim_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            gender TEXT,
            age INTEGER,
            phone TEXT,
            address TEXT,
            injury_level TEXT,
            medical_report_summary TEXT,
            compensation_status TEXT DEFAULT 'Pending'
        );

        CREATE TABLE IF NOT EXISTS witnesses (
            witness_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            statement_summary TEXT NOT NULL,
            protection_status TEXT DEFAULT 'None',
            is_key_witness BOOLEAN DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS evidence (
            evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
            evidence_code TEXT NOT NULL UNIQUE,
            case_id INTEGER NOT NULL,
            evidence_type TEXT NOT NULL,
            description TEXT NOT NULL,
            collected_at TIMESTAMP NOT NULL,
            collected_by_officer_id INTEGER,
            storage_location TEXT NOT NULL,
            status TEXT DEFAULT 'In Vault'
        );

        CREATE TABLE IF NOT EXISTS evidence_chains (
            chain_id INTEGER PRIMARY KEY AUTOINCREMENT,
            evidence_id INTEGER NOT NULL,
            transferred_from TEXT NOT NULL,
            transferred_to TEXT NOT NULL,
            transfer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            purpose TEXT NOT NULL,
            officer_in_charge_id INTEGER
        );

        CREATE TABLE IF NOT EXISTS forensic_reports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            evidence_id INTEGER NOT NULL,
            lab_name TEXT NOT NULL,
            examiner_name TEXT NOT NULL,
            submission_date DATE NOT NULL,
            completion_date DATE,
            findings TEXT NOT NULL,
            conclusion TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS interrogations (
            interrogation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            suspect_id INTEGER NOT NULL,
            interrogator_officer_id INTEGER NOT NULL,
            session_date TIMESTAMP NOT NULL,
            duration_minutes INTEGER,
            key_confessions TEXT,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS arrests (
            arrest_id INTEGER PRIMARY KEY AUTOINCREMENT,
            suspect_id INTEGER NOT NULL,
            case_id INTEGER NOT NULL,
            arresting_officer_id INTEGER NOT NULL,
            arrest_date TIMESTAMP NOT NULL,
            arrest_location TEXT NOT NULL,
            warrant_number TEXT,
            custody_location TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS judges (
            judge_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            court_name TEXT NOT NULL,
            specialization TEXT
        );

        CREATE TABLE IF NOT EXISTS lawyers (
            lawyer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name VARCHAR(100) NOT NULL,
            bar_association_number VARCHAR(50) NOT NULL UNIQUE,
            lawyer_type TEXT,
            phone TEXT
        );

        CREATE TABLE IF NOT EXISTS chargesheets (
            chargesheet_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chargesheet_number TEXT NOT NULL UNIQUE,
            case_id INTEGER NOT NULL UNIQUE,
            filing_date DATE NOT NULL,
            court_name TEXT NOT NULL,
            charges_summary TEXT NOT NULL,
            sections_applied TEXT NOT NULL,
            investigating_officer_id INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS court_cases (
            court_case_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL UNIQUE,
            court_case_number TEXT NOT NULL UNIQUE,
            judge_id INTEGER,
            prosecutor_id INTEGER,
            defense_lawyer_id INTEGER,
            filing_date DATE NOT NULL,
            verdict TEXT DEFAULT 'Pending',
            sentence_summary TEXT
        );

        CREATE TABLE IF NOT EXISTS hearings (
            hearing_id INTEGER PRIMARY KEY AUTOINCREMENT,
            court_case_id INTEGER NOT NULL,
            hearing_date TIMESTAMP NOT NULL,
            summary TEXT,
            next_hearing_date DATE,
            outcome TEXT
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            action_performed TEXT NOT NULL,
            target_table TEXT,
            details TEXT,
            ip_address TEXT DEFAULT '127.0.0.1',
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.executescript(schema_sql)
        self.connection.commit()

    def execute_query(self, query: str, params: Tuple = ()) -> Any:
        """Executes INSERT/UPDATE/DELETE query."""
        try:
            if self.db_type == "mysql":
                cursor = self.connection.cursor()
                cursor.execute(query, params)
                return cursor.lastrowid
            else:
                cursor = self.connection.cursor()
                # Replace MySQL %s with SQLite ? placeholder if needed
                sql_prepared = query.replace("%s", "?")
                cursor.execute(sql_prepared, params)
                self.connection.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error executing query [{query[:50]}...]: {e}")
            raise e

    def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Executes SELECT query and returns list of dictionaries."""
        try:
            if self.db_type == "mysql":
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute(query, params)
                return cursor.fetchall()
            else:
                cursor = self.connection.cursor()
                sql_prepared = query.replace("%s", "?")
                cursor.execute(sql_prepared, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching data [{query[:50]}...]: {e}")
            return []

    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Executes SELECT query and returns single dictionary or None."""
        results = self.fetch_all(query, params)
        return results[0] if results else None

def get_db() -> DatabaseManager:
    """Returns DatabaseManager instance."""
    return DatabaseManager()
