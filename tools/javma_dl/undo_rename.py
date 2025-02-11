#!/usr/bin/env python3

import os
from pathlib import Path
import sys

def get_original_name(filename):
    """Extract original name from renamed file (part before first underscore)."""
    return filename.split('_')[0] + '.pdf'

def undo_rename():
    script_dir = Path(__file__).parent
    pdf_dir = script_dir / 'output' / 'pdfs'
    
    if not pdf_dir.exists():
        print(f"Error: PDF directory {pdf_dir} not found!")
        sys.exit(1)
    
    # Process each PDF file
    renamed = 0
    skipped = 0
    
    for pdf_path in pdf_dir.glob('*.pdf'):
        try:
            # Skip files that don't contain an underscore (likely not renamed)
            if '_' not in pdf_path.stem:
                print(f"Skipping {pdf_path.name} - appears to not be renamed")
                skipped += 1
                continue
            
            # Get original name
            original_name = get_original_name(pdf_path.name)
            new_path = pdf_path.parent / original_name
            
            # Check if target name already exists
            if new_path.exists():
                print(f"Skipping {pdf_path.name} - target name {original_name} already exists")
                skipped += 1
                continue
            
            # Rename file back to original name
            pdf_path.rename(new_path)
            print(f"Restored: {pdf_path.name} -> {new_path.name}")
            renamed += 1
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}", file=sys.stderr)
            skipped += 1
    
    return renamed, skipped

def main():
    print("Starting to undo PDF renaming...")
    renamed, skipped = undo_rename()
    print(f"\nComplete! Restored {renamed} files to original names")
    if skipped > 0:
        print(f"Skipped {skipped} files")

if __name__ == "__main__":
    main()