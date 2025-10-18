#!/usr/bin/env python3
"""
CLI tool for importing pathogen data using EngineShelob.
"""

import argparse
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.settings import get_db_path
from Engines.EngineShelob import apply_import, ingest_file


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Import pathogen data using EngineShelob")
    parser.add_argument("file", help="Path to CSV or Excel file containing pathogen data")
    parser.add_argument(
        "--strategy", default="upsert", choices=["upsert"], help="Import strategy (default: upsert)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Parse file but don't import to database"
    )
    parser.add_argument("--db-path", help="Database path (default: from environment)")

    args = parser.parse_args()

    # Validate file exists
    if not os.path.exists(args.file):
        print(f"❌ Error: File not found: {args.file}")
        sys.exit(1)

    # Get database path
    if args.db_path:
        db_path = args.db_path
    else:
        try:
            db_path = get_db_path()
        except Exception as e:
            print(f"❌ Error getting database path: {e}")
            sys.exit(1)

    # Read file
    try:
        with open(args.file, "rb") as f:
            file_content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)

    print(f"📁 Processing file: {args.file}")
    print(f"🗄️  Database: {db_path}")

    # Ingest file
    print("🔄 Ingesting file...")
    ingested_data = ingest_file(file_content, args.file)

    if not ingested_data["success"]:
        print("❌ Ingestion failed:")
        for error in ingested_data.get("errors", []):
            print(f"   - {error}")
        sys.exit(1)

    print("✅ Ingestion successful:")
    print(f"   - Total rows: {ingested_data['total_rows']}")
    print(f"   - Valid pathogens: {ingested_data['valid_pathogens']}")
    print(f"   - Association types: {len(ingested_data['data']['association_types'])}")
    print(f"   - Breakpoint at column: {ingested_data['data']['breakpoint']}")

    if args.dry_run:
        print("🔍 Dry run mode - not importing to database")
        return

    # Apply import
    print("💾 Importing to database...")
    result = apply_import(db_path, ingested_data, args.strategy)

    if result.errors:
        print("⚠️  Import completed with errors:")
        for error in result.errors:
            print(f"   - {error}")
    else:
        print("✅ Import completed successfully!")

    print("📊 Summary:")
    print(f"   - Pathogens processed: {result.pathogens_processed}")
    print(f"   - Pathogens created: {result.pathogens_created}")
    print(f"   - Pathogens updated: {result.pathogens_updated}")
    print(f"   - Associations processed: {result.associations_processed}")
    print(f"   - Associations created: {result.associations_created}")

    if result.warnings:
        print("⚠️  Warnings:")
        for warning in result.warnings:
            print(f"   - {warning}")


if __name__ == "__main__":
    main()
