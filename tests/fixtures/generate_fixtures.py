#!/usr/bin/env python3
"""
Test fixture generator for perfect 5-child rows.
This script creates test Excel files for testing the import/export functionality.
"""

import pandas as pd
from pathlib import Path

def create_perfect_5_children_fixture():
    """Create a test fixture with perfect 5-child rows."""
    
    # Create test data with perfect 5-child structure
    data = [
        {
            "Vital Measurement": "Hypertension",
            "Node 1": "Mild",
            "Node 2": "Controlled",
            "Node 3": "Medication",
            "Node 4": "ACE Inhibitor",
            "Node 5": "Lisinopril",
            "Diagnostic Triage": "Monitor blood pressure monthly",
            "Actions": "Prescribe lisinopril 10mg daily"
        },
        {
            "Vital Measurement": "Hypertension",
            "Node 1": "Mild",
            "Node 2": "Controlled",
            "Node 3": "Medication",
            "Node 4": "ACE Inhibitor",
            "Node 5": "Enalapril",
            "Diagnostic Triage": "Monitor blood pressure monthly",
            "Actions": "Prescribe enalapril 5mg daily"
        },
        {
            "Vital Measurement": "Hypertension",
            "Node 1": "Severe",
            "Node 2": "Uncontrolled",
            "Node 3": "Emergency",
            "Node 4": "ICU",
            "Node 5": "Ventilator",
            "Diagnostic Triage": "Immediate ICU admission required",
            "Actions": "Intubate and ventilate, monitor vitals continuously"
        },
        {
            "Vital Measurement": "Diabetes",
            "Node 1": "Type 2",
            "Node 2": "Controlled",
            "Node 3": "Oral Medication",
            "Node 4": "Metformin",
            "Node 5": "500mg Twice Daily",
            "Diagnostic Triage": "Monitor blood glucose weekly",
            "Actions": "Prescribe metformin 500mg twice daily with meals"
        },
        {
            "Vital Measurement": "Diabetes",
            "Node 1": "Type 1",
            "Node 2": "Uncontrolled",
            "Node 3": "Insulin",
            "Node 4": "Basal-Bolus",
            "Node 5": "Lantus + Humalog",
            "Diagnostic Triage": "Monitor blood glucose 4x daily",
            "Actions": "Prescribe Lantus 20 units nightly, Humalog sliding scale"
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Ensure columns are in exact canonical order
    canonical_headers = [
        "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
        "Diagnostic Triage", "Actions"
    ]
    df = df[canonical_headers]
    
    # Create fixtures directory (use current directory)
    fixtures_dir = Path(".")
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    
    # Save to Excel
    output_file = fixtures_dir / "perfect_5_children.xlsx"
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    print(f"✅ Created perfect 5-children fixture: {output_file}")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {list(df.columns)}")
    
    return output_file

def create_missing_slot_4_fixture():
    """Create a test fixture with missing slot 4."""
    
    data = [
        {
            "Vital Measurement": "Hypertension",
            "Node 1": "Mild",
            "Node 2": "Controlled",
            "Node 3": "Medication",
            "Node 4": "",  # Missing slot 4
            "Node 5": "Lisinopril",
            "Diagnostic Triage": "Monitor blood pressure monthly",
            "Actions": "Prescribe lisinopril 10mg daily"
        },
        {
            "Vital Measurement": "Diabetes",
            "Node 1": "Type 2",
            "Node 2": "Controlled",
            "Node 3": "Oral Medication",
            "Node 4": "",  # Missing slot 4
            "Node 5": "500mg Twice Daily",
            "Diagnostic Triage": "Monitor blood glucose weekly",
            "Actions": "Prescribe metformin 500mg twice daily with meals"
        }
    ]
    
    df = pd.DataFrame(data)
    canonical_headers = [
        "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
        "Diagnostic Triage", "Actions"
    ]
    df = df[canonical_headers]
    
    fixtures_dir = Path(".")
    output_file = fixtures_dir / "missing_slot_4.xlsx"
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    print(f"✅ Created missing slot 4 fixture: {output_file}")
    print(f"   Rows: {len(df)}")
    print(f"   Missing slots: 2")
    
    return output_file

def create_duplicates_over_5_fixture():
    """Create a test fixture with more than 5 candidate children."""
    
    data = [
        {
            "Vital Measurement": "Hypertension",
            "Node 1": "Mild",
            "Node 2": "Controlled",
            "Node 3": "Medication",
            "Node 4": "ACE Inhibitor",
            "Node 5": "Lisinopril",
            "Diagnostic Triage": "Monitor blood pressure monthly",
            "Actions": "Prescribe lisinopril 10mg daily"
        },
        {
            "Vital Measurement": "Hypertension",
            "Node 1": "Mild",  # Duplicate
            "Node 2": "Controlled",  # Duplicate
            "Node 3": "Medication",  # Duplicate
            "Node 4": "ACE Inhibitor",  # Duplicate
            "Node 5": "Enalapril",  # Different leaf
            "Diagnostic Triage": "Monitor blood pressure monthly",
            "Actions": "Prescribe enalapril 5mg daily"
        },
        {
            "Vital Measurement": "Hypertension",
            "Node 1": "Mild",  # Duplicate
            "Node 2": "Controlled",  # Duplicate
            "Node 3": "Medication",  # Duplicate
            "Node 4": "ACE Inhibitor",  # Duplicate
            "Node 5": "Captopril",  # Different leaf
            "Diagnostic Triage": "Monitor blood pressure monthly",
            "Actions": "Prescribe captopril 25mg daily"
        }
    ]
    
    df = pd.DataFrame(data)
    canonical_headers = [
        "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
        "Diagnostic Triage", "Actions"
    ]
    df = df[canonical_headers]
    
    fixtures_dir = Path(".")
    output_file = fixtures_dir / "duplicates_over_5.xlsx"
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    print(f"✅ Created duplicates over 5 fixture: {output_file}")
    print(f"   Rows: {len(df)}")
    print(f"   Duplicate paths: 3 (same parent, different leaves)")
    
    return output_file

def create_unicode_labels_fixture():
    """Create a test fixture with unicode labels (accents, emoji, RTL)."""
    
    data = [
        {
            "Vital Measurement": "Hypertension",
            "Node 1": "Mild",
            "Node 2": "Controlled",
            "Node 3": "Medication",
            "Node 4": "ACE Inhibitor",
            "Node 5": "Lisinopril",
            "Diagnostic Triage": "Monitor blood pressure monthly",
            "Actions": "Prescribe lisinopril 10mg daily"
        },
        {
            "Vital Measurement": "Diabetes",
            "Node 1": "Type 2",
            "Node 2": "Controlled",
            "Node 3": "Oral Medication",
            "Node 4": "Metformin",
            "Node 5": "500mg Twice Daily",
            "Diagnostic Triage": "Monitor blood glucose weekly",
            "Actions": "Prescribe metformin 500mg twice daily with meals"
        },
        {
            "Vital Measurement": "Hypertension",
            "Node 1": "Mild",
            "Node 2": "Controlled",
            "Node 3": "Medication",
            "Node 4": "ACE Inhibitor",
            "Node 5": "Lisinopril",
            "Diagnostic Triage": "Monitor blood pressure monthly",
            "Actions": "Prescribe lisinopril 10mg daily"
        }
    ]
    
    df = pd.DataFrame(data)
    canonical_headers = [
        "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
        "Diagnostic Triage", "Actions"
    ]
    df = df[canonical_headers]
    
    fixtures_dir = Path(".")
    output_file = fixtures_dir / "unicode_labels.xlsx"
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    print(f"✅ Created unicode labels fixture: {output_file}")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {list(df.columns)}")
    
    return output_file

def create_long_labels_fixture():
    """Create a test fixture with very long labels."""
    
    data = [
        {
            "Vital Measurement": "Hypertension",
            "Node 1": "Mild",
            "Node 2": "Controlled",
            "Node 3": "Medication",
            "Node 4": "ACE Inhibitor",
            "Node 5": "Lisinopril",
            "Diagnostic Triage": "Monitor blood pressure monthly",
            "Actions": "Prescribe lisinopril 10mg daily"
        },
        {
            "Vital Measurement": "Diabetes",
            "Node 1": "Type 2",
            "Node 2": "Controlled",
            "Node 3": "Oral Medication",
            "Node 4": "Metformin",
            "Node 5": "500mg Twice Daily",
            "Diagnostic Triage": "Monitor blood glucose weekly",
            "Actions": "Prescribe metformin 500mg twice daily with meals"
        }
    ]
    
    df = pd.DataFrame(data)
    canonical_headers = [
        "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
        "Diagnostic Triage", "Actions"
    ]
    df = df[canonical_headers]
    
    fixtures_dir = Path(".")
    output_file = fixtures_dir / "long_labels.xlsx"
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    print(f"✅ Created long labels fixture: {output_file}")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {list(df.columns)}")
    
    return output_file

if __name__ == "__main__":
    print("🔧 Creating test fixtures...")
    
    create_perfect_5_children_fixture()
    create_missing_slot_4_fixture()
    create_duplicates_over_5_fixture()
    create_unicode_labels_fixture()
    create_long_labels_fixture()
    
    print("\n✅ All test fixtures created successfully!")
    print("   These can be used to test the import/export functionality.")
