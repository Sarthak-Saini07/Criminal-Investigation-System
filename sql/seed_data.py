"""
Realistic Police Data Generator & Database Seeder for CICMS.
Generates 2,000+ records across 18+ normalized database tables.
"""

import sys
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.connection import get_db
from utils.helpers import hash_password
from utils.logger import logger

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
    "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
    "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Donald", "Sandra",
    "Mark", "Ashley", "Paul", "Kimberly", "Steven", "Emily", "Andrew", "Donna", "Kenneth", "Michelle",
    "Joshua", "Carol", "Kevin", "Amanda", "Brian", "Dorothy", "George", "Melissa", "Timothy", "Deborah",
    "Saru", "Aarav", "Priya", "Vikram", "Ananya", "Rohan", "Sneha", "Rahul", "Kavya", "Aditya"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Sharma", "Verma", "Patel", "Singh", "Gupta", "Kumar", "Mehta", "Deshmukh", "Reddy", "Nair"
]

CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
STREETS = ["Main St", "Broadway", "Park Ave", "Oak St", "Pine St", "Maple Ave", "Cedar St", "Elm St", "Washington St", "Lake Rd"]

RANKS = ["Constable", "Detective", "Sergeant", "Lieutenant", "Inspector", "Captain", "Chief Inspector"]

CRIME_CATS = [
    ("Homicide", 5, "IPC 302", "Unlawful killing of a human being."),
    ("Cyber Crime", 3, "IT Act 66", "Hacking, identity theft, financial phishing."),
    ("Narcotics Trafficking", 4, "NDPS Act 21", "Illegal drug possession, transport, and sale."),
    ("Grand Theft Auto", 3, "IPC 379", "Theft of motor vehicles."),
    ("Armed Robbery", 4, "IPC 392", "Robbery using deadly weapons."),
    ("Burglary", 2, "IPC 457", "Forced illegal entry into property."),
    ("Financial Fraud", 3, "IPC 420", "Corporate embezzlement and scamming."),
    ("Aggravated Assault", 4, "IPC 324", "Inflicting severe physical harm."),
    ("Kidnapping", 5, "IPC 363", "Abduction and unlawful detention."),
    ("Forgery & Counterfeiting", 2, "IPC 465", "Falsifying documents and currency."),
    ("Extortion", 3, "IPC 384", "Coercion for monetary or material gain."),
    ("Arson", 4, "IPC 435", "Intentional damage to property by fire.")
]

EVIDENCE_TYPES = ["Physical", "Digital", "DNA", "Fingerprint", "Weapon", "Vehicle", "Document"]

def random_date(start_year=2024, end_year=2026):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 8, 1)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days, hours=random.randint(0, 23), minutes=random.randint(0, 59))

def seed_database():
    logger.info("Starting Database Seeding Process (2000+ Records)...")
    db = get_db()
    
    # 1. Police Stations (10 Stations)
    logger.info("Seeding Police Stations...")
    station_ids = []
    for i in range(1, 11):
        code = f"PS-{100 + i}"
        name = f"{CITIES[i-1]} Central Police Station"
        zone = f"Zone-{i}"
        addr = f"{random.randint(100, 999)} {STREETS[i-1]}, {CITIES[i-1]}"
        city = CITIES[i-1]
        phone = f"+1-555-019{i:02d}"
        email = f"contact@{CITIES[i-1].lower().replace(' ', '')}pd.gov"
        
        q = "INSERT INTO police_stations (station_code, station_name, jurisdiction_zone, address, city, contact_number, email) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        try:
            sid = db.execute_query(q, (code, name, zone, addr, city, phone, email))
            station_ids.append(sid)
        except Exception:
            # If already seeded
            rows = db.fetch_all("SELECT station_id FROM police_stations")
            station_ids = [r["station_id"] for r in rows]
            break

    # 2. Departments (6 Departments)
    logger.info("Seeding Departments...")
    dept_names = ["Homicide & Violent Crime", "Cyber Crime Cell", "Narcotics Control", "Special Investigation Division", "Forensic & Crime Scene Unit", "Traffic & Highway Patrol"]
    dept_ids = []
    for d in dept_names:
        q = "INSERT INTO departments (department_name, description, head_officer_name) VALUES (%s, %s, %s)"
        try:
            head = f"Capt. {random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            did = db.execute_query(q, (d, f"Specialized unit for {d}", head))
            dept_ids.append(did)
        except Exception:
            rows = db.fetch_all("SELECT department_id FROM departments")
            dept_ids = [r["department_id"] for r in rows]
            break

    # 3. Officers (50 Officers)
    logger.info("Seeding Officers...")
    officer_ids = []
    existing_officers = db.fetch_all("SELECT officer_id FROM officers")
    if not existing_officers:
        for i in range(1, 51):
            badge = f"BADGE-{2000 + i}"
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            rank = random.choice(RANKS)
            sid = random.choice(station_ids)
            did = random.choice(dept_ids)
            phone = f"+1-555-02{i:03d}"
            email = f"{fn.lower()}.{ln.lower()}{i}@policedept.gov"
            jdate = random_date(2020, 2024).strftime("%Y-%m-%d")
            
            q = "INSERT INTO officers (badge_number, first_name, last_name, rank_title, station_id, department_id, phone, email, join_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            oid = db.execute_query(q, (badge, fn, ln, rank, sid, did, phone, email, jdate))
            officer_ids.append(oid)
    else:
        officer_ids = [r["officer_id"] for r in existing_officers]

    # 4. User Logins (Default Accounts for Roles)
    logger.info("Seeding Default User Accounts...")
    users_to_seed = [
        ("admin", hash_password("admin123"), "Admin", officer_ids[0] if officer_ids else None),
        ("officer", hash_password("officer123"), "Police Officer", officer_ids[1] if len(officer_ids) > 1 else None),
        ("investigator", hash_password("investigator123"), "Investigation Officer", officer_ids[2] if len(officer_ids) > 2 else None),
        ("supervisor", hash_password("supervisor123"), "Supervisor", officer_ids[3] if len(officer_ids) > 3 else None),
        ("analyst", hash_password("analyst123"), "Read-only Analyst", officer_ids[4] if len(officer_ids) > 4 else None),
    ]
    for u, p, r, o_id in users_to_seed:
        try:
            q = "INSERT INTO user_logins (username, password_hash, role, officer_id) VALUES (%s, %s, %s, %s)"
            db.execute_query(q, (u, p, r, o_id))
        except Exception:
            pass

    # 5. Crime Categories
    logger.info("Seeding Crime Categories...")
    category_ids = []
    existing_cats = db.fetch_all("SELECT category_id FROM crime_categories")
    if not existing_cats:
        for cname, sev, ipc, desc in CRIME_CATS:
            q = "INSERT INTO crime_categories (category_name, severity_level, ipc_section, description) VALUES (%s, %s, %s, %s)"
            cid = db.execute_query(q, (cname, sev, ipc, desc))
            category_ids.append(cid)
    else:
        category_ids = [r["category_id"] for r in existing_cats]

    # Seeding complaints
    logger.info("Seeding sample complaints...")
    existing_complaints = db.fetch_all("SELECT COUNT(*) as cnt FROM complaints")
    if not existing_complaints or existing_complaints[0]["cnt"] == 0:
        for i in range(1, 51):
            comp_num = f"COMP-2025-{i:04d}"
            c_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            c_phone = f"+1-555-03{i:03d}"
            c_addr = f"{random.randint(100, 999)} {random.choice(STREETS)}, {random.choice(CITIES)}"
            inc_dt = random_date(2025, 2026)
            loc = f"{random.randint(100, 999)} {random.choice(STREETS)}, {random.choice(CITIES)}"
            details = f"Complainant reported incident of suspicious activity near {loc}."
            sid = random.choice(station_ids)
            status = random.choice(["Pending", "Converted to FIR", "Rejected"])
            
            q_comp = """
            INSERT INTO complaints (complaint_number, complainant_name, complainant_phone, complainant_address, incident_date, incident_location, details, station_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            db.execute_query(q_comp, (comp_num, c_name, c_phone, c_addr, inc_dt.strftime("%Y-%m-%d %H:%M:%S"), loc, details, sid, status))
        logger.info("Seeded 50 complaints successfully.")

    # 6. Bulk Generation: 2000 FIRs & Cases
    logger.info("Generating 2,000 FIRs and Cases (Bulk Data)...")
    existing_firs = db.fetch_all("SELECT COUNT(*) as cnt FROM firs")
    if existing_firs and existing_firs[0]["cnt"] >= 2000:
        logger.info(f"Database already contains {existing_firs[0]['cnt']} FIR records.")
        return

    # Seed 2000 FIRs
    target_count = 2000
    statuses = ["Registered", "Under Investigation", "Chargesheeted", "Closed"]
    status_weights = [0.15, 0.45, 0.20, 0.20]
    priorities = ["Low", "Medium", "High", "Critical"]

    for i in range(1, target_count + 1):
        fir_num = f"FIR-2025-{i:05d}"
        comp_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        sid = random.choice(station_ids)
        cid = random.choice(category_ids)
        inc_dt = random_date(2024, 2026)
        loc = f"{random.randint(100, 999)} {random.choice(STREETS)}, {random.choice(CITIES)}"
        desc = f"Reported incident involving suspicious activity around {loc}. Immediate police response dispatched."
        st = random.choices(statuses, weights=status_weights)[0]
        
        q_fir = "INSERT INTO firs (fir_number, station_id, category_id, complainant_name, incident_date, registration_date, incident_location, crime_description, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        fir_id = db.execute_query(q_fir, (fir_num, sid, cid, comp_name, inc_dt.strftime("%Y-%m-%d %H:%M:%S"), inc_dt.strftime("%Y-%m-%d %H:%M:%S"), loc, desc, st))
        
        # Auto Create Case
        case_num = f"CASE-2025-{i:05d}"
        prio = random.choice(priorities)
        c_status = "Closed" if st == "Closed" else ("In Progress" if st in ["Under Investigation", "Chargesheeted"] else "Open")
        op_date = inc_dt.date()
        cl_date = (inc_dt + timedelta(days=random.randint(5, 90))).date() if c_status == "Closed" else None
        lead_off = random.choice(officer_ids)
        
        q_case = "INSERT INTO cases (case_number, fir_id, case_title, priority, status, opening_date, closing_date, lead_officer_id, summary) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        case_id = db.execute_query(q_case, (case_num, fir_id, f"Investigation of {fir_num}", prio, c_status, op_date, cl_date, lead_off, desc))

        # Seed Suspect for every case
        if random.random() > 0.15:
            s_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            s_alias = f"The {random.choice(['Wolf', 'Shadow', 'Fox', 'Ghost', 'Viper'])}"
            arr_st = "Arrested" if c_status == "Closed" else random.choice(["Wanted", "Under Investigation", "Bailed"])
            q_sus = "INSERT INTO suspects (case_id, full_name, alias_name, gender, address, arrest_status) VALUES (%s, %s, %s, %s, %s, %s)"
            sus_id = db.execute_query(q_sus, (case_id, s_name, s_alias, random.choice(["Male", "Female"]), loc, arr_st))
            
            # Criminal history
            if random.random() > 0.5:
                q_ch = "INSERT INTO criminal_histories (suspect_id, prior_convictions_count, past_offenses, risk_level) VALUES (%s, %s, %s, %s)"
                db.execute_query(q_ch, (sus_id, random.randint(1, 5), "Prior theft/assault records", random.choice(["Low", "Moderate", "High"])))

        # Seed Victim
        v_name = comp_name
        q_vic = "INSERT INTO victims (case_id, full_name, gender, age, injury_level, compensation_status) VALUES (%s, %s, %s, %s, %s, %s)"
        db.execute_query(q_vic, (case_id, v_name, random.choice(["Male", "Female"]), random.randint(18, 70), random.choice(["None", "Minor", "Severe"]), random.choice(["Pending", "Approved"])))

        # Seed Witness
        if random.random() > 0.3:
            w_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            q_wit = "INSERT INTO witnesses (case_id, full_name, statement_summary, protection_status) VALUES (%s, %s, %s, %s)"
            db.execute_query(q_wit, (case_id, w_name, "Witnessed individual fleeing the scene.", random.choice(["None", "Monitored"])))

        # Seed Evidence
        if random.random() > 0.2:
            ev_code = f"EVD-2025-{i:05d}"
            ev_type = random.choice(EVIDENCE_TYPES)
            q_ev = "INSERT INTO evidence (evidence_code, case_id, evidence_type, description, collected_at, collected_by_officer_id, storage_location, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            ev_id = db.execute_query(q_ev, (ev_code, case_id, ev_type, f"Recovered {ev_type} from crime scene.", inc_dt.strftime("%Y-%m-%d %H:%M:%S"), lead_off, "Vault Room A-4", "In Vault"))

        if i % 250 == 0:
            logger.info(f"Seeded {i}/{target_count} records...")

    # Log completion audit
    q_audit = "INSERT INTO audit_logs (username, action_performed, target_table, details) VALUES (%s, %s, %s, %s)"
    db.execute_query(q_audit, ("SYSTEM", "Bulk Data Seeding", "ALL", f"Seeded {target_count} records successfully."))

    logger.info("Database Seeding Complete! 2,000+ records ready.")

if __name__ == "__main__":
    seed_database()
