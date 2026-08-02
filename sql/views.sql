-- =============================================================================
-- CICMS DATABASE VIEWS
-- =============================================================================

USE cicms_db;

-- 1. Detailed Case Summary View
CREATE OR REPLACE VIEW vw_case_summary AS
SELECT 
    c.case_id,
    c.case_number,
    f.fir_number,
    f.complainant_name,
    cc.category_name,
    cc.severity_level,
    ps.station_name,
    ps.city,
    c.case_title,
    c.priority,
    c.status AS case_status,
    c.opening_date,
    c.closing_date,
    CONCAT(o.first_name, ' ', o.last_name) AS lead_officer_name,
    o.badge_number AS lead_officer_badge,
    COUNT(DISTINCT e.evidence_id) AS total_evidence_items,
    COUNT(DISTINCT s.suspect_id) AS total_suspects,
    COUNT(DISTINCT w.witness_id) AS total_witnesses
FROM cases c
JOIN firs f ON c.fir_id = f.fir_id
JOIN crime_categories cc ON f.category_id = cc.category_id
JOIN police_stations ps ON f.station_id = ps.station_id
LEFT JOIN officers o ON c.lead_officer_id = o.officer_id
LEFT JOIN evidence e ON c.case_id = e.case_id
LEFT JOIN suspects s ON c.case_id = s.case_id
LEFT JOIN witnesses w ON c.case_id = w.case_id
GROUP BY c.case_id, c.case_number, f.fir_number, f.complainant_name, cc.category_name, cc.severity_level, ps.station_name, ps.city, c.case_title, c.priority, c.status, c.opening_date, c.closing_date, o.first_name, o.last_name, o.badge_number;

-- 2. Officer Workload & Performance View
CREATE OR REPLACE VIEW vw_officer_workload AS
SELECT 
    o.officer_id,
    o.badge_number,
    CONCAT(o.first_name, ' ', o.last_name) AS officer_name,
    o.rank_title,
    ps.station_name,
    d.department_name,
    COUNT(DISTINCT c.case_id) AS active_cases_assigned,
    SUM(CASE WHEN c.status = 'Closed' THEN 1 ELSE 0 END) AS closed_cases_count,
    COUNT(DISTINCT arr.arrest_id) AS total_arrests_made
FROM officers o
JOIN police_stations ps ON o.station_id = ps.station_id
JOIN departments d ON o.department_id = d.department_id
LEFT JOIN cases c ON c.lead_officer_id = o.officer_id
LEFT JOIN arrests arr ON arr.arresting_officer_id = o.officer_id
GROUP BY o.officer_id, o.badge_number, o.first_name, o.last_name, o.rank_title, ps.station_name, d.department_name;

-- 3. Crime Category Analytics View
CREATE OR REPLACE VIEW vw_crime_analytics_summary AS
SELECT 
    cc.category_name,
    cc.severity_level,
    COUNT(f.fir_id) AS total_firs_registered,
    SUM(CASE WHEN c.status = 'Closed' THEN 1 ELSE 0 END) AS total_cases_closed,
    ROUND(AVG(DATEDIFF(IFNULL(c.closing_date, CURRENT_DATE), c.opening_date)), 1) AS avg_resolution_days
FROM crime_categories cc
LEFT JOIN firs f ON f.category_id = cc.category_id
LEFT JOIN cases c ON c.fir_id = f.fir_id
GROUP BY cc.category_id, cc.category_name, cc.severity_level;
