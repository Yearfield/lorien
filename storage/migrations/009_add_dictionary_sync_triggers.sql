-- Migration: Add bidirectional sync triggers between dictionary and tree nodes
-- Date: 2025-01-27
-- Purpose: Keep medical_dictionary and nodes tables in sync when terms are updated

-- Function to update dictionary metrics for a term
-- This will be called when nodes are updated to refresh dictionary statistics
CREATE TRIGGER IF NOT EXISTS tr_sync_dictionary_on_node_change
AFTER UPDATE OF label ON nodes
FOR EACH ROW
WHEN OLD.label != NEW.label
BEGIN
    -- Update the dictionary entry if it exists
    UPDATE medical_dictionary
    SET
        term = NEW.label,
        avg_children_count = (
            SELECT COUNT(*)
            FROM nodes children
            WHERE children.parent_id IN (
                SELECT id FROM nodes
                WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label))
            )
        ),
        conflicts_count = (
            SELECT COUNT(*) - 1
            FROM nodes
            WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label))
        ),
        updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
    WHERE LOWER(TRIM(term)) = LOWER(TRIM(OLD.label));

    -- If no dictionary entry exists, create one
    INSERT OR IGNORE INTO medical_dictionary (
        term,
        definition,
        synonyms,
        is_red_flag,
        avg_children_count,
        conflicts_count,
        created_at,
        updated_at
    )
    SELECT
        NEW.label,
        NULL,
        '[]',
        0,
        (
            SELECT COUNT(*)
            FROM nodes children
            WHERE children.parent_id IN (
                SELECT id FROM nodes
                WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label))
            )
        ),
        (
            SELECT COUNT(*) - 1
            FROM nodes
            WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label))
        ),
        strftime('%Y-%m-%dT%H:%M:%fZ','now'),
        strftime('%Y-%m-%dT%H:%M:%fZ','now')
    WHERE NOT EXISTS (
        SELECT 1 FROM medical_dictionary
        WHERE LOWER(TRIM(term)) = LOWER(TRIM(NEW.label))
    );
END;

-- Trigger to create dictionary entry when new nodes are inserted
CREATE TRIGGER IF NOT EXISTS tr_sync_dictionary_on_node_insert
AFTER INSERT ON nodes
FOR EACH ROW
BEGIN
    -- Create dictionary entry if it doesn't exist
    INSERT OR IGNORE INTO medical_dictionary (
        term,
        definition,
        synonyms,
        is_red_flag,
        avg_children_count,
        conflicts_count,
        created_at,
        updated_at
    )
    SELECT
        NEW.label,
        NULL,
        '[]',
        0,
        (
            SELECT COUNT(*)
            FROM nodes children
            WHERE children.parent_id IN (
                SELECT id FROM nodes
                WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label))
            )
        ),
        (
            SELECT COUNT(*) - 1
            FROM nodes
            WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label))
        ),
        strftime('%Y-%m-%dT%H:%M:%fZ','now'),
        strftime('%Y-%m-%dT%H:%M:%fZ','now')
    WHERE NOT EXISTS (
        SELECT 1 FROM medical_dictionary
        WHERE LOWER(TRIM(term)) = LOWER(TRIM(NEW.label))
    );

    -- Update existing dictionary entries for this term
    UPDATE medical_dictionary
    SET
        avg_children_count = (
            SELECT COUNT(*)
            FROM nodes children
            WHERE children.parent_id IN (
                SELECT id FROM nodes
                WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label))
            )
        ),
        conflicts_count = (
            SELECT COUNT(*) - 1
            FROM nodes
            WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label))
        ),
        updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
    WHERE LOWER(TRIM(term)) = LOWER(TRIM(NEW.label));
END;

-- Trigger to update dictionary when nodes are deleted
CREATE TRIGGER IF NOT EXISTS tr_sync_dictionary_on_node_delete
AFTER DELETE ON nodes
FOR EACH ROW
BEGIN
    -- Update dictionary entries for the deleted term
    UPDATE medical_dictionary
    SET
        avg_children_count = (
            SELECT COUNT(*)
            FROM nodes children
            WHERE children.parent_id IN (
                SELECT id FROM nodes
                WHERE LOWER(TRIM(label)) = LOWER(TRIM(OLD.label))
            )
        ),
        conflicts_count = (
            SELECT COUNT(*) - 1
            FROM nodes
            WHERE LOWER(TRIM(label)) = LOWER(TRIM(OLD.label))
        ),
        updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
    WHERE LOWER(TRIM(term)) = LOWER(TRIM(OLD.label));

    -- If no more nodes exist for this term, remove from dictionary
    DELETE FROM medical_dictionary
    WHERE LOWER(TRIM(term)) = LOWER(TRIM(OLD.label))
    AND NOT EXISTS (
        SELECT 1 FROM nodes
        WHERE LOWER(TRIM(label)) = LOWER(TRIM(OLD.label))
    );
END;

-- Trigger to sync tree nodes when dictionary terms are updated
CREATE TRIGGER IF NOT EXISTS tr_sync_nodes_on_dictionary_change
AFTER UPDATE OF term ON medical_dictionary
FOR EACH ROW
WHEN OLD.term != NEW.term
BEGIN
    -- Update all nodes with the old term to use the new term
    UPDATE nodes
    SET
        label = NEW.term,
        updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
    WHERE LOWER(TRIM(label)) = LOWER(TRIM(OLD.term));
END;

-- Trigger to sync red flag status when dictionary is updated
CREATE TRIGGER IF NOT EXISTS tr_sync_red_flags_on_dictionary_change
AFTER UPDATE OF is_red_flag ON medical_dictionary
FOR EACH ROW
WHEN OLD.is_red_flag != NEW.is_red_flag
BEGIN
    -- If setting as red flag, create red flag entries for all nodes with this term
    -- If removing red flag, remove red flag entries for all nodes with this term

    -- First, remove existing red flag associations for this term
    DELETE FROM node_red_flags
    WHERE node_id IN (
        SELECT id FROM nodes
        WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.term))
    );

    -- If setting as red flag, add red flag associations
    -- Note: We'll use a generic red flag for dictionary terms
    -- In a real implementation, you might want to create specific red flags per term
    INSERT OR IGNORE INTO red_flags (name, description, severity)
    VALUES (
        'Dictionary Term: ' || NEW.term,
        'Medical term flagged in dictionary',
        'medium'
    );

    -- Add red flag associations if is_red_flag is true
    INSERT OR IGNORE INTO node_red_flags (node_id, red_flag_id)
    SELECT
        n.id,
        rf.id
    FROM nodes n
    CROSS JOIN red_flags rf
    WHERE LOWER(TRIM(n.label)) = LOWER(TRIM(NEW.term))
    AND rf.name = 'Dictionary Term: ' || NEW.term
    AND NEW.is_red_flag = 1;
END;
