-- =============================================================================
-- CICMS DATABASE STORED PROCEDURES
-- =============================================================================

USE cicms_db;

DELIMITER //

-- Procedure to Register FIR and Auto-Open Case
CREATE PROCEDURE sp_register_fir(
    IN p_station_id INT,
    IN p_category_id INT,
    IN p_complainant_name VARCHAR(100),
    IN p_incident_date DATETIME,
    IN p_incident_location VARCHAR(200),
    IN p_crime_description TEXT,
    IN p_priority VARCHAR(20),
    OUT p_fir_id INT,
    OUT p_case_id INT
)
BEGIN
    DECLARE v_fir_seq INT;
    DECLARE v_fir_num VARCHAR(30);
    DECLARE v_case_num VARCHAR(30);
    
    -- Transaction handling
    START TRANSACTION;
    
    SELECT IFNULL(MAX(fir_id), 0) + 1 INTO v_fir_seq FROM firs;
    SET v_fir_num = CONCAT('FIR-', YEAR(CURRENT_DATE), '-', LPAD(v_fir_seq, 5, '0'));
    
    INSERT INTO firs (fir_number, station_id, category_id, complainant_name, incident_date, incident_location, crime_description, status)
    VALUES (v_fir_num, p_station_id, p_category_id, p_complainant_name, p_incident_date, p_incident_location, p_crime_description, 'Registered');
    
    SET p_fir_id = LAST_INSERT_ID();
    
    SET v_case_num = CONCAT('CASE-', YEAR(CURRENT_DATE), '-', LPAD(p_fir_id, 5, '0'));
    
    INSERT INTO cases (case_number, fir_id, case_title, priority, status, opening_date, summary)
    VALUES (v_case_num, p_fir_id, CONCAT('Investigation for ', v_fir_num), p_priority, 'Open', CURRENT_DATE, p_crime_description);
    
    SET p_case_id = LAST_INSERT_ID();
    
    COMMIT;
END //

-- Procedure to Transfer Case
CREATE PROCEDURE sp_transfer_case(
    IN p_case_id INT,
    IN p_new_lead_officer_id INT,
    IN p_reason TEXT,
    IN p_user_name VARCHAR(50)
)
BEGIN
    DECLARE v_old_status VARCHAR(30);
    
    START TRANSACTION;
    
    SELECT status INTO v_old_status FROM cases WHERE case_id = p_case_id;
    
    UPDATE cases 
    SET lead_officer_id = p_new_lead_officer_id, status = 'Transferred'
    WHERE case_id = p_case_id;
    
    INSERT INTO case_status_history (case_id, previous_status, new_status, change_reason, changed_by_user)
    VALUES (p_case_id, v_old_status, 'Transferred', p_reason, p_user_name);
    
    INSERT INTO case_assignments (case_id, officer_id, role_in_case, status)
    VALUES (p_case_id, p_new_lead_officer_id, 'Lead Investigating Officer', 'Active');
    
    COMMIT;
END //

DELIMITER ;
