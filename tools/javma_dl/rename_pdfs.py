#!/usr/bin/env python3

import os
from pathlib import Path
import PyPDF2
import re
import sys

def sanitize_filename(filename):
    """Clean filename by removing/replacing invalid characters."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple spaces and underscores
    filename = re.sub(r'[\s_]+', '_', filename)
    # Trim to reasonable length (max 200 chars to leave room for extension)
    if len(filename) > 200:
        filename = filename[:197] + "..."
    return filename.strip('._')

def extract_pdf_title(pdf_path):
    """Extract title from PDF metadata or first page text."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Try to get title from metadata
            if reader.metadata and reader.metadata.get('/Title'):
                return reader.metadata['/Title']
            
            # If no metadata title, try to extract from first page
            if len(reader.pages) > 0:
                first_page = reader.pages[0]
                text = first_page.extract_text()
                
                # Take first non-empty line as title
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                if lines:
                    return lines[0]
    except Exception as e:
        print(f"Error extracting title from {pdf_path}: {e}", file=sys.stderr)
    
    return None

def rename_pdfs():
    script_dir = Path(__file__).parent
    pdf_dir = script_dir / 'output' / 'pdfs'
    
    if not pdf_dir.exists():
        print(f"Error: PDF directory {pdf_dir} not found!")
        sys.exit(1)
    
    # Process each PDF file
    for pdf_path in pdf_dir.glob('*.pdf'):
        try:
            original_name = pdf_path.stem
            
            # Extract title
            title = extract_pdf_title(pdf_path)
            if not title:
                print(f"Could not extract title from {pdf_path.name}, skipping...")
                continue
            
            # Create new filename
            new_name = f"{original_name}_{sanitize_filename(title)}.pdf"
            new_path = pdf_path.parent / new_name
            
            # Rename file
            if new_path.exists():
                print(f"Skipping {pdf_path.name} - target name already exists")
                continue
                
            pdf_path.rename(new_path)
            print(f"Renamed: {pdf_path.name} -> {new_path.name}")
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}", file=sys.stderr)

def main():
    print("Starting PDF renaming process...")
    rename_pdfs()
    print("PDF renaming complete!")

if __name__ == "__main__":
    main()