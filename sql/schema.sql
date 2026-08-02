-- =============================================================================
-- CRIMINAL INVESTIGATION AND CASE MANAGEMENT SYSTEM (CICMS)
-- DATABASE SCHEMA DEFINITION (MySQL 8.0+)
-- =============================================================================

CREATE DATABASE IF NOT EXISTS cicms_db;
USE cicms_db;

-- -----------------------------------------------------------------------------
-- 1. POLICE STATIONS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS police_stations (
    station_id INT AUTO_INCREMENT PRIMARY KEY,
    station_code VARCHAR(20) NOT NULL UNIQUE,
    station_name VARCHAR(100) NOT NULL,
    jurisdiction_zone VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(50) NOT NULL,
    contact_number VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 2. DEPARTMENTS / DIVISIONS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    head_officer_name VARCHAR(100)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 3. POLICE OFFICERS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS officers (
    officer_id INT AUTO_INCREMENT PRIMARY KEY,
    badge_number VARCHAR(30) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    rank_title VARCHAR(50) NOT NULL,
    station_id INT NOT NULL,
    department_id INT NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    join_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (station_id) REFERENCES police_stations(station_id) ON DELETE RESTRICT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 4. USER LOGINS (RBAC)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_logins (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL CHECK (role IN ('Admin', 'Police Officer', 'Investigation Officer', 'Supervisor', 'Read-only Analyst')),
    officer_id INT,
    last_login DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (officer_id) REFERENCES officers(officer_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 5. CRIME CATEGORIES
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crime_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    severity_level INT NOT NULL CHECK (severity_level BETWEEN 1 AND 5),
    ipc_section VARCHAR(50) NOT NULL,
    description TEXT
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 6. COMPLAINTS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_number VARCHAR(30) NOT NULL UNIQUE,
    complainant_name VARCHAR(100) NOT NULL,
    complainant_phone VARCHAR(20) NOT NULL,
    complainant_address TEXT NOT NULL,
    incident_date DATETIME NOT NULL,
    incident_location VARCHAR(200) NOT NULL,
    details TEXT NOT NULL,
    station_id INT NOT NULL,
    status VARCHAR(30) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Converted to FIR', 'Rejected')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES police_stations(station_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 7. FIRS (FIRST INFORMATION REPORTS)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS firs (
    fir_id INT AUTO_INCREMENT PRIMARY KEY,
    fir_number VARCHAR(30) NOT NULL UNIQUE,
    complaint_id INT,
    station_id INT NOT NULL,
    category_id INT NOT NULL,
    complainant_name VARCHAR(100) NOT NULL,
    incident_date DATETIME NOT NULL,
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    incident_location VARCHAR(200) NOT NULL,
    crime_description TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'Registered' CHECK (status IN ('Registered', 'Under Investigation', 'Chargesheeted', 'Closed')),
    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE SET NULL,
    FOREIGN KEY (station_id) REFERENCES police_stations(station_id) ON DELETE RESTRICT,
    FOREIGN KEY (category_id) REFERENCES crime_categories(category_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 8. CASES
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cases (
    case_id INT AUTO_INCREMENT PRIMARY KEY,
    case_number VARCHAR(30) NOT NULL UNIQUE,
    fir_id INT NOT NULL UNIQUE,
    case_title VARCHAR(200) NOT NULL,
    priority VARCHAR(20) DEFAULT 'Medium' CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
    status VARCHAR(30) DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Transferred', 'Closed')),
    opening_date DATE NOT NULL,
    closing_date DATE,
    lead_officer_id INT,
    summary TEXT,
    FOREIGN KEY (fir_id) REFERENCES firs(fir_id) ON DELETE RESTRICT,
    FOREIGN KEY (lead_officer_id) REFERENCES officers(officer_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 9. CASE ASSIGNMENTS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS case_assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    officer_id INT NOT NULL,
    assigned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    role_in_case VARCHAR(50) DEFAULT 'Investigating Officer',
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Reassigned', 'Completed')),
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
    FOREIGN KEY (officer_id) REFERENCES officers(officer_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 10. CASE STATUS HISTORY
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS case_status_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    previous_status VARCHAR(30),
    new_status VARCHAR(30) NOT NULL,
    change_reason TEXT,
    changed_by_user VARCHAR(50),
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 11. SUSPECTS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS suspects (
    suspect_id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    alias_name VARCHAR(50),
    dob DATE,
    gender VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other')),
    national_id VARCHAR(30),
    address TEXT,
    height_cm INT,
    build VARCHAR(30),
    arrest_status VARCHAR(30) DEFAULT 'Under Investigation' CHECK (arrest_status IN ('Wanted', 'Under Investigation', 'Arrested', 'Released', 'Bailed')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 12. CRIMINAL HISTORIES
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS criminal_histories (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    suspect_id INT NOT NULL,
    prior_convictions_count INT DEFAULT 0,
    past_offenses TEXT,
    gang_affiliation VARCHAR(100),
    risk_level VARCHAR(20) DEFAULT 'Low' CHECK (risk_level IN ('Low', 'Moderate', 'High', 'Extreme')),
    FOREIGN KEY (suspect_id) REFERENCES suspects(suspect_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 13. VICTIMS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS victims (
    victim_id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other')),
    age INT,
    phone VARCHAR(20),
    address TEXT,
    injury_level VARCHAR(30) CHECK (injury_level IN ('None', 'Minor', 'Severe', 'Fatal')),
    medical_report_summary TEXT,
    compensation_status VARCHAR(30) DEFAULT 'Pending' CHECK (compensation_status IN ('Pending', 'Approved', 'Disbursed', 'N/A')),
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 14. WITNESSES
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS witnesses (
    witness_id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    statement_summary TEXT NOT NULL,
    protection_status VARCHAR(30) DEFAULT 'None' CHECK (protection_status IN ('None', 'Monitored', 'Protective Custody')),
    is_key_witness BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 15. EVIDENCE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id INT AUTO_INCREMENT PRIMARY KEY,
    evidence_code VARCHAR(30) NOT NULL UNIQUE,
    case_id INT NOT NULL,
    evidence_type VARCHAR(50) NOT NULL CHECK (evidence_type IN ('Physical', 'Digital', 'DNA', 'Fingerprint', 'Weapon', 'Vehicle', 'Document')),
    description TEXT NOT NULL,
    collected_at DATETIME NOT NULL,
    collected_by_officer_id INT,
    storage_location VARCHAR(100) NOT NULL,
    status VARCHAR(30) DEFAULT 'In Vault' CHECK (status IN ('In Vault', 'In Testing', 'Court Exhibit', 'Disposed', 'Returned')),
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
    FOREIGN KEY (collected_by_officer_id) REFERENCES officers(officer_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 16. EVIDENCE CHAIN OF CUSTODY
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS evidence_chains (
    chain_id INT AUTO_INCREMENT PRIMARY KEY,
    evidence_id INT NOT NULL,
    transferred_from VARCHAR(100) NOT NULL,
    transferred_to VARCHAR(100) NOT NULL,
    transfer_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    purpose TEXT NOT NULL,
    officer_in_charge_id INT,
    FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id) ON DELETE CASCADE,
    FOREIGN KEY (officer_in_charge_id) REFERENCES officers(officer_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 17. FORENSIC REPORTS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS forensic_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    evidence_id INT NOT NULL,
    lab_name VARCHAR(100) NOT NULL,
    examiner_name VARCHAR(100) NOT NULL,
    submission_date DATE NOT NULL,
    completion_date DATE,
    findings TEXT NOT NULL,
    conclusion VARCHAR(50) NOT NULL,
    FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 18. INTERROGATIONS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS interrogations (
    interrogation_id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    suspect_id INT NOT NULL,
    interrogator_officer_id INT NOT NULL,
    session_date DATETIME NOT NULL,
    duration_minutes INT,
    key_confessions TEXT,
    notes TEXT,
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
    FOREIGN KEY (suspect_id) REFERENCES suspects(suspect_id) ON DELETE CASCADE,
    FOREIGN KEY (interrogator_officer_id) REFERENCES officers(officer_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 19. ARRESTS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS arrests (
    arrest_id INT AUTO_INCREMENT PRIMARY KEY,
    suspect_id INT NOT NULL,
    case_id INT NOT NULL,
    arresting_officer_id INT NOT NULL,
    arrest_date DATETIME NOT NULL,
    arrest_location VARCHAR(200) NOT NULL,
    warrant_number VARCHAR(50),
    custody_location VARCHAR(100) NOT NULL,
    FOREIGN KEY (suspect_id) REFERENCES suspects(suspect_id) ON DELETE CASCADE,
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
    FOREIGN KEY (arresting_officer_id) REFERENCES officers(officer_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 20. COURT PERSONNEL & PROCEEDINGS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS judges (
    judge_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    court_name VARCHAR(100) NOT NULL,
    specialization VARCHAR(50)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS lawyers (
    lawyer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    bar_association_number VARCHAR(50) NOT NULL UNIQUE,
    lawyer_type VARCHAR(20) CHECK (lawyer_type IN ('Prosecutor', 'Defense')),
    phone VARCHAR(20)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS chargesheets (
    chargesheet_id INT AUTO_INCREMENT PRIMARY KEY,
    chargesheet_number VARCHAR(30) NOT NULL UNIQUE,
    case_id INT NOT NULL UNIQUE,
    filing_date DATE NOT NULL,
    court_name VARCHAR(100) NOT NULL,
    charges_summary TEXT NOT NULL,
    sections_applied VARCHAR(200) NOT NULL,
    investigating_officer_id INT NOT NULL,
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
    FOREIGN KEY (investigating_officer_id) REFERENCES officers(officer_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS court_cases (
    court_case_id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL UNIQUE,
    court_case_number VARCHAR(50) NOT NULL UNIQUE,
    judge_id INT,
    prosecutor_id INT,
    defense_lawyer_id INT,
    filing_date DATE NOT NULL,
    verdict VARCHAR(30) DEFAULT 'Pending' CHECK (verdict IN ('Pending', 'Convicted', 'Acquitted', 'Dismissed')),
    sentence_summary TEXT,
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
    FOREIGN KEY (judge_id) REFERENCES judges(judge_id) ON DELETE SET NULL,
    FOREIGN KEY (prosecutor_id) REFERENCES lawyers(lawyer_id) ON DELETE SET NULL,
    FOREIGN KEY (defense_lawyer_id) REFERENCES lawyers(lawyer_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS hearings (
    hearing_id INT AUTO_INCREMENT PRIMARY KEY,
    court_case_id INT NOT NULL,
    hearing_date DATETIME NOT NULL,
    summary TEXT,
    next_hearing_date DATE,
    outcome VARCHAR(50),
    FOREIGN KEY (court_case_id) REFERENCES court_cases(court_case_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 21. AUDIT LOGS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    action_performed VARCHAR(100) NOT NULL,
    target_table VARCHAR(50),
    details TEXT,
    ip_address VARCHAR(45) DEFAULT '127.0.0.1',
    logged_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Indexes for Optimization
CREATE INDEX idx_firs_station ON firs(station_id);
CREATE INDEX idx_firs_category ON firs(category_id);
CREATE INDEX idx_cases_status ON cases(status);
CREATE INDEX idx_cases_lead_officer ON cases(lead_officer_id);
CREATE INDEX idx_evidence_case ON evidence(case_id);
CREATE INDEX idx_suspects_case ON suspects(case_id);
