#!/usr/bin/env python3

"""Main script for categorizing veterinary journal articles."""

import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

from categorize.constants import SPECIALTIES, STATUS_CODES
from categorize.file_utils import setup_output_dirs, copy_and_rename
from categorize.pdf_utils import extract_first_pages
from categorize.llm_utils import analyze_with_qwen

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('categorize_pdfs.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def process_pdfs(input_dir, output_dir, debug=False):
    """Process PDFs and categorize them."""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    if not input_dir.exists():
        logging.error(f"Input directory not found: {input_dir}")
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all PDFs recursively
    pdf_files = sorted(input_dir.rglob('*.pdf'))
    if not pdf_files:
        logging.error(f"No PDF files found in {input_dir}")
        sys.exit(1)
    
    logging.info(f"Found {len(pdf_files)} PDF files to analyze")
    logging.info("Categorizing articles using qwen model...")
    
    start_time = datetime.now()
    
    # Create specialty directories
    specialty_dirs, rejected_dir = setup_output_dirs(output_dir)
    
    # Track counts
    counts = {
        'surgical': 0,
        'internal_medicine': 0,
        'rejected': 0
    }
    
    # Process each PDF file
    for i, pdf_path in enumerate(pdf_files, 1):
        if not debug:
            print(f"\rProcessing file {i}/{len(pdf_files)}: {pdf_path.name}", end='', flush=True)
        else:
            logging.info(f"\nAnalyzing {pdf_path}")
        
        # Extract and analyze text
        text = extract_first_pages(pdf_path)
        if not text:
            counts['rejected'] += 1
            copy_and_rename(pdf_path, rejected_dir, STATUS_CODES['error'])
            continue
        
        # Analyze with qwen
        analysis = analyze_with_qwen(text, pdf_path)
        if not analysis:
            counts['rejected'] += 1
            copy_and_rename(pdf_path, rejected_dir, STATUS_CODES['error'])
            continue
        
        # Clear the progress line for output
        if not debug:
            print("\r" + " " * 80 + "\r", end='', flush=True)
        
        # Process analysis results
        if not analysis['is_journal_article']:
            counts['rejected'] += 1
            copy_and_rename(pdf_path, rejected_dir, STATUS_CODES['not_journal'])
            logging.info(f"REJECTED - Not journal: {pdf_path}")
            continue
        
        if not analysis['is_small_animal']:
            counts['rejected'] += 1
            copy_and_rename(pdf_path, rejected_dir, STATUS_CODES['not_small_animal'])
            logging.info(f"REJECTED - Not small animal: {pdf_path}")
            continue
        
        # Categorize based on specialty
        specialty = analysis['specialty']
        confidence = analysis['confidence']
        
        if specialty in specialty_dirs and confidence >= 70:
            # Update counts
            if specialty == 'Surgery':
                counts['surgical'] += 1
            else:
                counts['internal_medicine'] += 1
            
            # Copy file to appropriate directory
            suffix = f"c{confidence}"
            new_path = copy_and_rename(pdf_path, specialty_dirs[specialty], suffix)
            logging.info(f"{specialty.upper()} ({confidence}% confidence) - {new_path}")
        else:
            counts['rejected'] += 1
            copy_and_rename(pdf_path, rejected_dir, STATUS_CODES['unclear_category'])
            logging.info(f"REJECTED - Unclear category: {pdf_path}")
    
    # Print summary
    duration = datetime.now() - start_time
    logging.info(f"\nCategorization complete in {duration.total_seconds():.1f} seconds")
    logging.info("\nResults:")
    logging.info(f"Internal Medicine articles: {counts['internal_medicine']}")
    logging.info(f"Surgical articles: {counts['surgical']}")
    logging.info(f"Rejected articles: {counts['rejected']}")
    logging.info(f"\nResults saved to: {output_dir}/")

def main():
    parser = argparse.ArgumentParser(
        description='Categorize small animal journal articles into surgical and internal medicine.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Requirements:
- Must be a research journal article
- Must focus on dogs and/or cats
- Must be clearly surgical or internal medicine

Examples:
  %(prog)s /path/to/pdfs /path/to/output
  %(prog)s -d ~/Documents/papers ~/categorized_papers
""")
    
    parser.add_argument('input_dir',
                       help='Directory to search for PDF files (searched recursively)')
    parser.add_argument('output_dir',
                       help='Directory to save categorized files')
    parser.add_argument('-d', '--debug',
                       action='store_true',
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    # Convert to absolute paths and expand user directory
    input_dir = str(Path(args.input_dir).expanduser().resolve())
    output_dir = str(Path(args.output_dir).expanduser().resolve())
    
    # Process PDFs
    process_pdfs(input_dir, output_dir, args.debug)

if __name__ == "__main__":
    main()
