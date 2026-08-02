-- =============================================================================
-- CICMS DATABASE TRIGGERS
-- =============================================================================

USE cicms_db;

DELIMITER //

-- Trigger on Case Status Change
CREATE TRIGGER trg_after_case_status_update
AFTER UPDATE ON cases
FOR EACH ROW
BEGIN
    IF OLD.status <> NEW.status THEN
        INSERT INTO case_status_history (case_id, previous_status, new_status, change_reason, changed_by_user)
        VALUES (NEW.case_id, OLD.status, NEW.status, 'Status updated via case management module', 'SYSTEM');
        
        INSERT INTO audit_logs (username, action_performed, target_table, details)
        VALUES ('SYSTEM', CONCAT('Updated Case Status: ', NEW.case_number), 'cases', CONCAT('Status changed from ', OLD.status, ' to ', NEW.status));
    END IF;
END //

-- Trigger on Evidence Item Insert
CREATE TRIGGER trg_after_evidence_insert
AFTER INSERT ON evidence
FOR EACH ROW
BEGIN
    INSERT INTO evidence_chains (evidence_id, transferred_from, transferred_to, purpose, officer_in_charge_id)
    VALUES (NEW.evidence_id, 'Scene of Crime / Field', NEW.storage_location, 'Initial Evidence Custody Vault Deposit', NEW.collected_by_officer_id);
    
    INSERT INTO audit_logs (username, action_performed, target_table, details)
    VALUES ('SYSTEM', CONCAT('Registered Evidence: ', NEW.evidence_code), 'evidence', CONCAT('Logged initial chain of custody for type ', NEW.evidence_type));
END //

DELIMITER ;
