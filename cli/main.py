#!/usr/bin/env python3
"""
Decision Tree CLI - Command line interface for decision tree operations.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from core.constants import (
    EXIT_SUCCESS, EXIT_VALIDATION_ERROR, EXIT_IMPORT_ERROR, 
    EXIT_EXPORT_ERROR, EXIT_SYSTEM_ERROR, APP_VERSION, APP_NAME
)
from core.engine import DecisionTreeEngine
from core.import_export import ImportExportEngine
from .commands import (
    validate_tree, import_excel, import_gsheet, 
    export_excel, export_csv, fix_tree
)

def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - Manage decision tree structures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  dt validate                    # Validate tree structure
  dt import-excel data.xlsx     # Import from Excel file
  dt export-csv output.csv      # Export to CSV
  dt fix --enforce-five         # Fix tree violations

Version: {APP_VERSION}
        """
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands'
    )
    
    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate tree structure and print counts'
    )
    validate_parser.add_argument(
        '--exit-on-violations',
        action='store_true',
        help='Exit with error code if violations found'
    )
    
    # Import Excel command
    import_excel_parser = subparsers.add_parser(
        'import-excel',
        help='Import decision tree from Excel file'
    )
    import_excel_parser.add_argument(
        'file',
        type=str,
        help='Excel file path (.xlsx or .xls)'
    )
    import_excel_parser.add_argument(
        '--strategy',
        choices=['placeholder', 'prune', 'prompt'],
        default='placeholder',
        help='Strategy for handling missing nodes (default: placeholder)'
    )
    
    # Import Google Sheets command
    import_gsheet_parser = subparsers.add_parser(
        'import-gsheet',
        help='Import decision tree from Google Sheets'
    )
    import_gsheet_parser.add_argument(
        'sheet_id',
        type=str,
        help='Google Sheets ID'
    )
    import_gsheet_parser.add_argument(
        'worksheet',
        type=str,
        help='Worksheet name'
    )
    import_gsheet_parser.add_argument(
        '--strategy',
        choices=['placeholder', 'prune', 'prompt'],
        default='placeholder',
        help='Strategy for handling missing nodes (default: placeholder)'
    )
    
    # Export Excel command
    export_excel_parser = subparsers.add_parser(
        'export-excel',
        help='Export decision tree to Excel file'
    )
    export_excel_parser.add_argument(
        'file',
        type=str,
        help='Output Excel file path (.xlsx)'
    )
    
    # Export CSV command
    export_csv_parser = subparsers.add_parser(
        'export-csv',
        help='Export decision tree to CSV file'
    )
    export_csv_parser.add_argument(
        'file',
        type=str,
        help='Output CSV file path (.csv)'
    )
    
    # Fix command
    fix_parser = subparsers.add_parser(
        'fix',
        help='Fix tree violations'
    )
    fix_parser.add_argument(
        '--enforce-five',
        action='store_true',
        help='Enforce exactly 5 children per parent'
    )
    fix_parser.add_argument(
        '--strategy',
        choices=['placeholder', 'prune'],
        default='placeholder',
        help='Strategy for fixing violations (default: placeholder)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return EXIT_SUCCESS
    
    try:
        # Initialize real storage layer
        from storage.sqlite import SQLiteRepository
        repo = SQLiteRepository()
        
        # Execute command
        if args.command == 'validate':
            return validate_tree(repo, args.exit_on_violations)
        elif args.command == 'import-excel':
            return import_excel(repo, args.file, args.strategy)
        elif args.command == 'import-gsheet':
            return import_gsheet(repo, args.sheet_id, args.worksheet, args.strategy)
        elif args.command == 'export-excel':
            return export_excel(repo, args.file)
        elif args.command == 'export-csv':
            return export_csv(repo, args.file)
        elif args.command == 'fix':
            return fix_tree(repo, args.enforce_five, args.strategy)
        else:
            print(f"Unknown command: {args.command}")
            return EXIT_SYSTEM_ERROR
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return EXIT_SYSTEM_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return EXIT_SYSTEM_ERROR

if __name__ == "__main__":
    sys.exit(main())
