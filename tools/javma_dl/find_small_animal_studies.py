#!/usr/bin/env python3

import os
from pathlib import Path
import PyPDF2
import sys
import argparse
import re
from datetime import datetime

def extract_text(pdf_path):
    """Extract text from all pages of PDF."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}", file=sys.stderr)
    return None

def check_criteria(text, debug=False):
    """
    Check if text meets criteria:
    1. (Objective AND Results) OR (Abstract)
    2. Not focused on equine/horses
    3. Focused on dogs/cats
    """
    if not text:
        if debug:
            print("  No text extracted")
        return False, {}
    
    results = {
        'has_abstract': False,
        'has_objective': False,
        'has_results': False,
        'has_equine_focus': False,
        'has_small_animal_focus': False,
        'contexts': {
            'abstract': [],
            'objective': [],
            'results': [],
            'animals': []
        }
    }
    
    # Check for sections
    abstract_matches = list(re.finditer(r'\bAbstract\b', text, re.IGNORECASE))
    objective_matches = list(re.finditer(r'\b(Objective|Objectives)\b', text, re.IGNORECASE))
    results_matches = list(re.finditer(r'\bResults\b', text, re.IGNORECASE))
    
    results['has_abstract'] = bool(abstract_matches)
    results['has_objective'] = bool(objective_matches)
    results['has_results'] = bool(results_matches)
    
    # Store contexts
    if results['has_abstract']:
        results['contexts']['abstract'] = [get_context(text, m) for m in abstract_matches]
    if results['has_objective']:
        results['contexts']['objective'] = [get_context(text, m) for m in objective_matches]
    if results['has_results']:
        results['contexts']['results'] = [get_context(text, m) for m in results_matches]
    
    # Check for equine focus (exclude these)
    equine_terms = r'\b(horse|horses|equine|mare|stallion|foal)\b'
    equine_matches = list(re.finditer(equine_terms, text, re.IGNORECASE))
    equine_count = len(equine_matches)
    
    # Check for small animal focus (require these)
    small_animal_terms = r'\b(dog|dogs|cat|cats|canine|feline|puppy|kitten|puppies|kittens)\b'
    small_animal_matches = list(re.finditer(small_animal_terms, text, re.IGNORECASE))
    small_animal_count = len(small_animal_matches)
    
    # Store animal contexts
    results['contexts']['animals'] = [get_context(text, m) for m in small_animal_matches[:5]]
    
    # Determine focus based on relative mention counts
    results['has_equine_focus'] = equine_count > small_animal_count
    results['has_small_animal_focus'] = small_animal_count > 0 and small_animal_count > equine_count
    
    if debug:
        print(f"  Has Abstract: {results['has_abstract']}")
        print(f"  Has Objective: {results['has_objective']}")
        print(f"  Has Results: {results['has_results']}")
        print(f"  Equine mentions: {equine_count}")
        print(f"  Small animal mentions: {small_animal_count}")
    
    # Check section requirements: (Objective AND Results) OR Abstract
    has_required_sections = (
        (results['has_objective'] and results['has_results']) or
        results['has_abstract']
    )
    
    # Article must have required sections, focus on small animals, and not be equine-focused
    matches = (has_required_sections and 
              results['has_small_animal_focus'] and 
              not results['has_equine_focus'])
    
    if debug and matches:
        print("  Matched due to:")
        if results['has_abstract']:
            print("  - Has Abstract")
        elif results['has_objective'] and results['has_results']:
            print("  - Has both Objective and Results")
        print(f"  - Has small animal focus ({small_animal_count} mentions)")
        print(f"  - Not equine focused ({equine_count} mentions)")
    
    return matches, results

def get_context(text, match, context_chars=50):
    """Get surrounding context for a regex match."""
    start = max(0, match.start() - context_chars)
    end = min(len(text), match.end() + context_chars)
    return f"...{text[start:end].strip()}..."

def process_pdfs(directory, output_file, debug=False):
    """Process PDFs and save matches to file as they're found."""
    if not Path(directory).exists():
        print(f"Error: Directory {directory} not found!")
        sys.exit(1)
    
    # Find all PDFs recursively
    pdf_files = sorted(Path(directory).rglob('*.pdf'))
    if not pdf_files:
        print(f"No PDF files found in {directory}")
        sys.exit(1)
    
    print(f"Found {len(pdf_files)} PDF files to analyze")
    print("Searching for small animal studies with required sections...")
    print(f"Matching files will be saved to {output_file}\n")
    
    start_time = datetime.now()
    matches_found = 0
    
    # Create output directory if needed
    output_path = Path(output_file)
    os.makedirs(output_path.parent, exist_ok=True)
    
    # Process each PDF file
    with open(output_file, 'w') as f:
        for i, pdf_path in enumerate(pdf_files, 1):
            if not debug:
                print(f"\rProcessing file {i}/{len(pdf_files)}: {pdf_path.name}", end='', flush=True)
            else:
                print(f"\nAnalyzing {pdf_path}:")
            
            # Extract and check text
            text = extract_text(pdf_path)
            matches, results = check_criteria(text, debug)
            
            if matches:
                matches_found += 1
                # Clear the progress line
                print("\r" + " " * 80 + "\r", end='', flush=True)
                
                print(f"\nMATCH FOUND ({matches_found}) - {pdf_path}")
                # Write to output file
                f.write(f"{pdf_path}\n")
                f.flush()  # Ensure it's written immediately
                
                if debug:
                    if results['has_abstract']:
                        print("\nAbstract context:")
                        print(f"  {results['contexts']['abstract'][0]}")
                    if results['has_objective'] and results['has_results']:
                        print("\nObjective context:")
                        print(f"  {results['contexts']['objective'][0]}")
                        print("\nResults context:")
                        print(f"  {results['contexts']['results'][0]}")
                    print("\nSmall animal mentions:")
                    for ctx in results['contexts']['animals'][:3]:  # Show first 3 mentions
                        print(f"  {ctx}")
                    print()
    
    # Clear the progress line
    print("\r" + " " * 80 + "\r", end='', flush=True)
    
    # Print summary
    duration = datetime.now() - start_time
    print(f"\nSearch complete in {duration.total_seconds():.1f} seconds")
    print(f"Found {matches_found} matching studies out of {len(pdf_files)} PDFs")
    print(f"Results saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description='Find small animal studies with required sections.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Criteria:
- Must have either:
  * Both "Objective" AND "Results" sections, OR
  * "Abstract" section
- Must focus on dogs/cats (not equine/horses)
- Must have more small animal mentions than equine mentions

Examples:
  %(prog)s /path/to/pdfs
  %(prog)s -d ~/Documents/papers
""")
    
    parser.add_argument('directory',
                       help='Directory to search for PDF files (searched recursively)')
    parser.add_argument('-d', '--debug',
                       action='store_true',
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    # Convert to absolute path and expand user directory
    pdf_dir = str(Path(args.directory).expanduser().resolve())
    
    # Set output file in script directory
    script_dir = Path(__file__).parent
    output_file = script_dir / 'javma_journal_articles.txt'
    
    # Process PDFs
    process_pdfs(pdf_dir, output_file, args.debug)

if __name__ == "__main__":
    main()