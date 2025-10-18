"""
Integration tests for EngineShelob pathogen import functionality.
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from Engines.EngineShelob import apply_import, ingest_file


class TestEngineShelob:
    """Test suite for EngineShelob pathogen import."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        # Apply pathogen schema
        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")

            # Create pathogen tables
            conn.execute(
                """
                CREATE TABLE pathogens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    classification TEXT,
                    nt TEXT,
                    pathogen_id TEXT,
                    pathogen_name TEXT NOT NULL,
                    vaccine TEXT,
                    toxin TEXT,
                    transmission TEXT,
                    ab_resistance TEXT,
                    host TEXT,
                    commensal TEXT,
                    disease TEXT,
                    incubation TEXT,
                    diagnosis TEXT,
                    treatment TEXT,
                    prevention TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE association_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE pathogen_associations (
                    pathogen_id INTEGER NOT NULL,
                    association_type_id INTEGER NOT NULL,
                    value INTEGER NOT NULL CHECK(value IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                    PRIMARY KEY (pathogen_id, association_type_id),
                    FOREIGN KEY (pathogen_id) REFERENCES pathogens(id) ON DELETE CASCADE,
                    FOREIGN KEY (association_type_id) REFERENCES association_types(id) ON DELETE CASCADE
                )
            """
            )

            conn.commit()

        yield db_path

        # Cleanup
        Path(db_path).unlink(missing_ok=True)

    def test_csv_ingestion(self, temp_db):
        """Test CSV file ingestion."""
        # Create sample CSV data
        csv_content = """classification,nt,pathogen_id,pathogen_name,vaccine,toxin,transmission,ab_resistance,host,commensal,disease,incubation,diagnosis,treatment,prevention,notes,meningitis,fever,cough
xd,Actinobacteria,2205725,BACTERIA Actinobacteria Actinomycetales Actinomycineae Actinomyces gravenitzii C83,No,No,Dental work trauma surgery aspiration,Ubiquitous soil commensal human and animal,Normal commensal flora oral respiratory tract,Lump Jaw Actinomycosis is a chronic suppurative,days to years,Oral Periodontal Infection post dental work,Immunocompromised,No,oral-cervicofacial disease,1,0,1
yb,Proteobacteria,1234567,Escherichia coli,Yes,No,Fecal-oral transmission,Resistant to ampicillin,Human gut,Commensal in human gut,Urinary tract infection,1-3 days,Urine culture,Antibiotics,Good hygiene,Common UTI pathogen,0,1,0"""

        # Test ingestion
        result = ingest_file(csv_content.encode("utf-8"), "test.csv")

        assert result["success"] is True
        assert result["total_rows"] == 2
        assert result["valid_pathogens"] == 2
        assert len(result["data"]["pathogens"]) == 2
        assert len(result["data"]["association_types"]) == 3  # meningitis, fever, cough

        # Check first pathogen data
        pathogen1 = result["data"]["pathogens"][0]
        assert (
            pathogen1["properties"]["pathogen_name"]
            == "BACTERIA Actinobacteria Actinomycetales Actinomycineae Actinomyces gravenitzii C83"
        )
        assert pathogen1["properties"]["classification"] == "xd"
        assert pathogen1["associations"]["meningitis"] == 1
        assert pathogen1["associations"]["fever"] == 0
        assert pathogen1["associations"]["cough"] == 1

    def test_database_storage(self, temp_db):
        """Test storing ingested data in database."""
        # Create sample data
        csv_content = """classification,nt,pathogen_id,pathogen_name,vaccine,toxin,transmission,ab_resistance,host,commensal,disease,incubation,diagnosis,treatment,prevention,notes,meningitis,fever
xd,Actinobacteria,2205725,Actinomyces gravenitzii,No,No,Dental work trauma,Ubiquitous soil commensal,Normal commensal flora,Lump Jaw Actinomycosis,days to years,Oral Periodontal Infection,Immunocompromised,No,oral-cervicofacial disease,1,0"""

        # Ingest and store
        ingested_data = ingest_file(csv_content.encode("utf-8"), "test.csv")
        result = apply_import(temp_db, ingested_data)

        assert result.pathogens_processed == 1
        assert result.pathogens_created == 1
        assert result.associations_created == 1  # Only meningitis=1 is stored
        assert len(result.errors) == 0

        # Verify database content
        with sqlite3.connect(temp_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Check pathogen
            cursor.execute(
                "SELECT * FROM pathogens WHERE pathogen_name = ?", ("Actinomyces gravenitzii",)
            )
            pathogen = cursor.fetchone()
            assert pathogen is not None
            assert pathogen["classification"] == "xd"
            assert pathogen["nt"] == "Actinobacteria"

            # Check association type
            cursor.execute("SELECT * FROM association_types WHERE name = ?", ("meningitis",))
            assoc_type = cursor.fetchone()
            assert assoc_type is not None

            # Check association
            cursor.execute(
                """
                SELECT pa.value
                FROM pathogen_associations pa
                JOIN association_types at ON pa.association_type_id = at.id
                WHERE at.name = ? AND pa.pathogen_id = ?
            """,
                ("meningitis", pathogen["id"]),
            )
            assoc = cursor.fetchone()
            assert assoc is not None
            assert assoc["value"] == 1

    def test_idempotent_import(self, temp_db):
        """Test that re-importing the same data is idempotent."""
        csv_content = """classification,nt,pathogen_id,pathogen_name,vaccine,toxin,transmission,ab_resistance,host,commensal,disease,incubation,diagnosis,treatment,prevention,notes,meningitis,fever
xd,Actinobacteria,2205725,Actinomyces gravenitzii,No,No,Dental work trauma,Ubiquitous soil commensal,Normal commensal flora,Lump Jaw Actinomycosis,days to years,Oral Periodontal Infection,Immunocompromised,No,oral-cervicofacial disease,1,0"""

        # First import
        ingested_data = ingest_file(csv_content.encode("utf-8"), "test.csv")
        result1 = apply_import(temp_db, ingested_data)

        assert result1.pathogens_created == 1
        assert result1.pathogens_updated == 0

        # Second import (should update, not create)
        result2 = apply_import(temp_db, ingested_data)

        assert result2.pathogens_created == 0
        assert result2.pathogens_updated == 1

        # Verify only one pathogen exists
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM pathogens")
            count = cursor.fetchone()[0]
            assert count == 1

    def test_association_detection(self, temp_db):
        """Test detection of property vs association columns."""
        # Test with clear breakpoint after "notes"
        csv_content = """classification,nt,pathogen_id,pathogen_name,vaccine,toxin,transmission,ab_resistance,host,commensal,disease,incubation,diagnosis,treatment,prevention,notes,meningitis,fever,cough,diarrhea
xd,Actinobacteria,2205725,Actinomyces gravenitzii,No,No,Dental work trauma,Ubiquitous soil commensal,Normal commensal flora,Lump Jaw Actinomycosis,days to years,Oral Periodontal Infection,Immunocompromised,No,oral-cervicofacial disease,1,0,1,0"""

        result = ingest_file(csv_content.encode("utf-8"), "test.csv")

        assert result["success"] is True
        assert result["data"]["breakpoint"] == 16  # After "notes" column
        assert len(result["data"]["association_types"]) == 4  # meningitis, fever, cough, diarrhea

        # Check that properties are correctly identified
        pathogen = result["data"]["pathogens"][0]
        assert "classification" in pathogen["properties"]
        assert "pathogen_name" in pathogen["properties"]
        assert "notes" in pathogen["properties"]

        # Check that associations are correctly identified
        assert "meningitis" in pathogen["associations"]
        assert "fever" in pathogen["associations"]
        assert "cough" in pathogen["associations"]
        assert "diarrhea" in pathogen["associations"]

    def test_empty_file_handling(self, temp_db):
        """Test handling of empty files."""
        result = ingest_file(b"", "empty.csv")

        assert result["success"] is True
        assert result["total_rows"] == 0
        assert result["valid_pathogens"] == 0
        assert len(result["data"]["pathogens"]) == 0

    def test_malformed_data_handling(self, temp_db):
        """Test handling of malformed data."""
        # CSV with missing required pathogen_name
        csv_content = """classification,nt,pathogen_id,pathogen_name,vaccine,toxin,transmission,ab_resistance,host,commensal,disease,incubation,diagnosis,treatment,prevention,notes,meningitis
xd,Actinobacteria,2205725,,No,No,Dental work trauma,Ubiquitous soil commensal,Normal commensal flora,Lump Jaw Actinomycosis,days to years,Oral Periodontal Infection,Immunocompromised,No,oral-cervicofacial disease,1"""

        result = ingest_file(csv_content.encode("utf-8"), "test.csv")

        # Should succeed but skip rows without pathogen_name
        assert result["success"] is True
        assert result["valid_pathogens"] == 0
        assert len(result["data"]["pathogens"]) == 0

    def test_binary_association_normalization(self, temp_db):
        """Test normalization of various binary association formats."""
        csv_content = """classification,nt,pathogen_id,pathogen_name,vaccine,toxin,transmission,ab_resistance,host,commensal,disease,incubation,diagnosis,treatment,prevention,notes,meningitis,fever,cough
xd,Actinobacteria,2205725,Actinomyces gravenitzii,No,No,Dental work trauma,Ubiquitous soil commensal,Normal commensal flora,Lump Jaw Actinomycosis,days to years,Oral Periodontal Infection,Immunocompromised,No,oral-cervicofacial disease,yes,no,true"""

        result = ingest_file(csv_content.encode("utf-8"), "test.csv")

        assert result["success"] is True
        pathogen = result["data"]["pathogens"][0]

        # Check normalization of different formats
        assert pathogen["associations"]["meningitis"] == 1  # "yes" -> 1
        assert pathogen["associations"]["fever"] == 0  # "no" -> 0
        assert pathogen["associations"]["cough"] == 1  # "true" -> 1
