"""
Archive stale documentation files with tombstone headers.

This script moves stale documentation files to docs/_archive/ and adds
tombstone headers explaining why they were archived.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# Stale files to archive
STALE_FILES = [
    "docs/Phase2_Completion.md",
    "docs/Phase3_Completion.md", 
    "docs/Phase4_Completion.md",
    "docs/PreBeta_Execution_Tracker.md",
    "docs/ReleaseNotes_v6.7.md",
]

# Archive directory
ARCHIVE_DIR = "docs/_archive"

def create_tombstone_header(original_path: str, reason: str, replacement: str = None) -> str:
    """Create a tombstone header for archived files."""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    header = f"""# ARCHIVED DOCUMENT

**Archived on:** {timestamp}
**Original path:** {original_path}
**Reason:** {reason}
"""
    
    if replacement:
        header += f"**Replacement:** {replacement}\n"
    
    header += f"""
**Note:** This file has been archived and is no longer maintained.
Please refer to current documentation for up-to-date information.

---

"""
    
    return header

def archive_file(file_path: str, reason: str, replacement: str = None) -> bool:
    """Archive a single file with tombstone header."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    # Create archive directory if it doesn't exist
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    # Get filename for archive
    filename = os.path.basename(file_path)
    archive_path = os.path.join(ARCHIVE_DIR, filename)
    
    # Read original content
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Create tombstone header
    tombstone = create_tombstone_header(file_path, reason, replacement)
    
    # Write archived file with tombstone
    with open(archive_path, 'w', encoding='utf-8') as f:
        f.write(tombstone + original_content)
    
    # Remove original file
    os.remove(file_path)
    
    print(f"Archived: {file_path} -> {archive_path}")
    return True

def main():
    """Archive all stale documentation files."""
    print("Archiving stale documentation files...")
    
    # Define reasons and replacements
    archive_plan = {
        "docs/Phase2_Completion.md": {
            "reason": "Phase completion file - outdated",
            "replacement": "Current phase status in PHASE6_README.md"
        },
        "docs/Phase3_Completion.md": {
            "reason": "Phase completion file - outdated", 
            "replacement": "Current phase status in PHASE6_README.md"
        },
        "docs/Phase4_Completion.md": {
            "reason": "Phase completion file - outdated",
            "replacement": "Current phase status in PHASE6_README.md"
        },
        "docs/PreBeta_Execution_Tracker.md": {
            "reason": "Pre-beta execution tracker - outdated",
            "replacement": "Current status in PHASE6_README.md and project tracking"
        },
        "docs/ReleaseNotes_v6.7.md": {
            "reason": "Old release notes - superseded by v6.8.0-beta.1",
            "replacement": "docs/Release_Notes_v6.8.0-beta.1.md"
        }
    }
    
    archived_count = 0
    
    for file_path, info in archive_plan.items():
        if archive_file(file_path, info["reason"], info["replacement"]):
            archived_count += 1
    
    print(f"\nArchived {archived_count} files to {ARCHIVE_DIR}/")
    print("All archived files include tombstone headers explaining the archival.")

if __name__ == "__main__":
    main()
