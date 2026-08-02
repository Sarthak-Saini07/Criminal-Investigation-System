"""
SQL Queries Repository for CICMS.
Contains structured SQL statements for data retrieval, analytics, and record operations.
Includes CTEs, Window Functions, Correlated Subqueries, and Complex Aggregates.
"""

# =============================================================================
# USER AUTHENTICATION & RBAC QUERIES
# =============================================================================
GET_USER_BY_USERNAME = """
SELECT u.*, o.first_name, o.last_name, o.rank_title, o.station_id 
FROM user_logins u
LEFT JOIN officers o ON u.officer_id = o.officer_id
WHERE u.username = %s AND u.is_active = 1
"""

UPDATE_LAST_LOGIN = """
UPDATE user_logins SET last_login = CURRENT_TIMESTAMP WHERE user_id = %s
"""

# =============================================================================
# FIR MANAGEMENT QUERIES
# =============================================================================
GET_ALL_FIRS = """
SELECT f.*, cc.category_name, cc.severity_level, ps.station_name 
FROM firs f
JOIN crime_categories cc ON f.category_id = cc.category_id
JOIN police_stations ps ON f.station_id = ps.station_id
ORDER BY f.fir_id DESC
"""

SEARCH_FIRS = """
SELECT f.*, cc.category_name, ps.station_name 
FROM firs f
JOIN crime_categories cc ON f.category_id = cc.category_id
JOIN police_stations ps ON f.station_id = ps.station_id
WHERE f.fir_number LIKE %s OR f.complainant_name LIKE %s OR f.incident_location LIKE %s
ORDER BY f.fir_id DESC
"""

INSERT_FIR = """
INSERT INTO firs (fir_number, complaint_id, station_id, category_id, complainant_name, incident_date, incident_location, crime_description, status)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

UPDATE_FIR_STATUS = """
UPDATE firs SET status = %s WHERE fir_id = %s
"""

# =============================================================================
# CASE MANAGEMENT QUERIES
# =============================================================================
GET_ALL_CASES = """
SELECT c.*, f.fir_number, cc.category_name, ps.station_name,
       CONCAT(o.first_name, ' ', o.last_name) AS lead_officer_name
FROM cases c
JOIN firs f ON c.fir_id = f.fir_id
JOIN crime_categories cc ON f.category_id = cc.category_id
JOIN police_stations ps ON f.station_id = ps.station_id
LEFT JOIN officers o ON c.lead_officer_id = o.officer_id
ORDER BY c.case_id DESC
"""

GET_CASE_BY_ID = """
SELECT c.*, f.fir_number, cc.category_name, cc.severity_level, ps.station_name, ps.city,
       CONCAT(o.first_name, ' ', o.last_name) AS lead_officer_name, o.badge_number AS lead_officer_badge
FROM cases c
JOIN firs f ON c.fir_id = f.fir_id
JOIN crime_categories cc ON f.category_id = cc.category_id
JOIN police_stations ps ON f.station_id = ps.station_id
LEFT JOIN officers o ON c.lead_officer_id = o.officer_id
WHERE c.case_id = %s
"""

INSERT_CASE = """
INSERT INTO cases (case_number, fir_id, case_title, priority, status, opening_date, lead_officer_id, summary)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

UPDATE_CASE_STATUS = """
UPDATE cases SET status = %s, closing_date = %s WHERE case_id = %s
"""

ASSIGN_LEAD_OFFICER = """
UPDATE cases SET lead_officer_id = %s WHERE case_id = %s
"""

GET_CASE_TIMELINE = """
SELECT history_id, case_id, previous_status, new_status, change_reason, changed_by_user, changed_at
FROM case_status_history
WHERE case_id = %s
ORDER BY changed_at ASC
"""

# =============================================================================
# SUSPECT & CRIMINAL HISTORY QUERIES
# =============================================================================
GET_SUSPECTS_BY_CASE = """
SELECT s.*, ch.prior_convictions_count, ch.past_offenses, ch.gang_affiliation, ch.risk_level
FROM suspects s
LEFT JOIN criminal_histories ch ON s.suspect_id = ch.suspect_id
WHERE s.case_id = %s
"""

INSERT_SUSPECT = """
INSERT INTO suspects (case_id, full_name, alias_name, dob, gender, national_id, address, height_cm, build, arrest_status)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

INSERT_CRIMINAL_HISTORY = """
INSERT INTO criminal_histories (suspect_id, prior_convictions_count, past_offenses, gang_affiliation, risk_level)
VALUES (%s, %s, %s, %s, %s)
"""

# =============================================================================
# EVIDENCE & CHAIN OF CUSTODY QUERIES
# =============================================================================
GET_EVIDENCE_BY_CASE = """
SELECT e.*, CONCAT(o.first_name, ' ', o.last_name) AS officer_name
FROM evidence e
LEFT JOIN officers o ON e.collected_by_officer_id = o.officer_id
WHERE e.case_id = %s
ORDER BY e.evidence_id DESC
"""

INSERT_EVIDENCE = """
INSERT INTO evidence (evidence_code, case_id, evidence_type, description, collected_at, collected_by_officer_id, storage_location, status)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

GET_EVIDENCE_CHAIN = """
SELECT ec.*, CONCAT(o.first_name, ' ', o.last_name) AS officer_name
FROM evidence_chains ec
LEFT JOIN officers o ON ec.officer_in_charge_id = o.officer_id
WHERE ec.evidence_id = %s
ORDER BY ec.transfer_date ASC
"""

INSERT_EVIDENCE_CHAIN = """
INSERT INTO evidence_chains (evidence_id, transferred_from, transferred_to, transfer_date, purpose, officer_in_charge_id)
VALUES (%s, %s, %s, %s, %s, %s)
"""

# =============================================================================
# COURT PROCEEDINGS & CHARGESHEET QUERIES
# =============================================================================
GET_COURT_CASE_DETAILS = """
SELECT cc.*, c.case_number, c.case_title, j.full_name AS judge_name,
       pl.full_name AS prosecutor_name, dl.full_name AS defense_lawyer_name,
       cs.chargesheet_number, cs.charges_summary, cs.sections_applied
FROM court_cases cc
JOIN cases c ON cc.case_id = c.case_id
LEFT JOIN judges j ON cc.judge_id = j.judge_id
LEFT JOIN lawyers pl ON cc.prosecutor_id = pl.lawyer_id
LEFT JOIN lawyers dl ON cc.defense_lawyer_id = dl.lawyer_id
LEFT JOIN chargesheets cs ON cs.case_id = c.case_id
WHERE cc.case_id = %s
"""

INSERT_CHARGESHEET = """
INSERT INTO chargesheets (chargesheet_number, case_id, filing_date, court_name, charges_summary, sections_applied, investigating_officer_id)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

INSERT_COURT_CASE = """
INSERT INTO court_cases (case_id, court_case_number, judge_id, prosecutor_id, defense_lawyer_id, filing_date, verdict, sentence_summary)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

GET_HEARINGS_BY_COURT_CASE = """
SELECT * FROM hearings WHERE court_case_id = %s ORDER BY hearing_date ASC
"""

# =============================================================================
# ADVANCED ANALYTICS & COMPLEX SQL QUERIES
# (CTEs, Window Functions, Correlated Subqueries, Having, Group By)
# =============================================================================

# CTE + Window Function: Rank Officers by Solved Cases per Station
RANK_OFFICERS_BY_PERFORMANCE = """
WITH OfficerStats AS (
    SELECT 
        o.officer_id,
        CONCAT(o.first_name, ' ', o.last_name) AS officer_name,
        ps.station_name,
        COUNT(c.case_id) AS total_assigned_cases,
        SUM(CASE WHEN c.status = 'Closed' THEN 1 ELSE 0 END) AS solved_cases,
        ROUND(AVG(DATEDIFF(IFNULL(c.closing_date, CURRENT_DATE), c.opening_date)), 1) AS avg_days_to_close
    FROM officers o
    JOIN police_stations ps ON o.station_id = ps.station_id
    LEFT JOIN cases c ON c.lead_officer_id = o.officer_id
    GROUP BY o.officer_id, o.first_name, o.last_name, ps.station_name
)
SELECT 
    officer_id,
    officer_name,
    station_name,
    total_assigned_cases,
    solved_cases,
    avg_days_to_close,
    RANK() OVER (PARTITION BY station_name ORDER BY solved_cases DESC) as station_rank
FROM OfficerStats
ORDER BY station_name, station_rank;
"""

# Correlated Subquery + Group By / Having: High Crime Stations Above Overall Average
HIGH_CRIME_STATIONS_ABOVE_AVG = """
SELECT 
    ps.station_id,
    ps.station_name,
    ps.city,
    COUNT(f.fir_id) AS station_fir_count
FROM police_stations ps
JOIN firs f ON ps.station_id = f.station_id
GROUP BY ps.station_id, ps.station_name, ps.city
HAVING COUNT(f.fir_id) > (
    SELECT AVG(fir_count) FROM (
        SELECT COUNT(fir_id) AS fir_count FROM firs GROUP BY station_id
    ) AS sub
)
ORDER BY station_fir_count DESC;
"""

# Station Performance Summary CTE
STATION_KPI_SUMMARY = """
WITH StationMetrics AS (
    SELECT 
        ps.station_id,
        ps.station_name,
        ps.city,
        COUNT(DISTINCT f.fir_id) AS total_firs,
        COUNT(DISTINCT c.case_id) AS total_cases,
        SUM(CASE WHEN c.status = 'Closed' THEN 1 ELSE 0 END) AS closed_cases,
        SUM(CASE WHEN c.status = 'Open' THEN 1 ELSE 0 END) AS open_cases,
        COUNT(DISTINCT e.evidence_id) AS total_evidence_logged
    FROM police_stations ps
    LEFT JOIN firs f ON ps.station_id = f.station_id
    LEFT JOIN cases c ON c.fir_id = f.fir_id
    LEFT JOIN evidence e ON c.case_id = e.case_id
    GROUP BY ps.station_id, ps.station_name, ps.city
)
SELECT 
    station_name,
    city,
    total_firs,
    total_cases,
    closed_cases,
    open_cases,
    total_evidence_logged,
    ROUND((closed_cases * 100.0 / NULLIF(total_cases, 0)), 2) AS clearance_rate_pct
FROM StationMetrics
ORDER BY total_firs DESC;
"""
