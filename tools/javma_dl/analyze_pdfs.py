#!/usr/bin/env python3

import os
from pathlib import Path
import PyPDF2
import sys
import json
import requests
import argparse

# Define valid document types and categories
DOCUMENT_TYPES = {
    "JAVMA News Digest",
    "Book Reviews",
    "Review Article",
    "Special Report",
    "Editorial",
    "Correction"
}

CATEGORIES = {
    "Analytic Techniques",
    "Anatomy – Gross and Microscopic",
    "Anesthesia – Analgesia",
    "Animal Welfare",
    "Antimicrobials",
    "Biomechanics",
    "Bone, Joint, and Cartilage",
    "Cardiovascular System",
    "Clinical Pathology",
    "Diagnostic Imaging",
    "Digestive System – Nutrition",
    "Endocrinology",
    "Hematology",
    "Immunology",
    "Infectious Disease",
    "Microbiology",
    "Musculoskeletal System",
    "Neurology",
    "Oncology",
    "Ophthalmology",
    "Pharmacology",
    "Physiology",
    "Respiratory System",
    "Surgery",
    "Theriogenology",
    "Tissue Regeneration – Healing",
    "Urology",
    "Vaccinology"
}

def extract_first_page(pdf_path):
    """Extract text from first page of PDF."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if len(reader.pages) > 0:
                return reader.pages[0].extract_text()
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}", file=sys.stderr)
    return None

def analyze_text(text):
    """Use Ollama to analyze text and determine document type, category, and title."""
    categories_str = "\n".join(sorted(CATEGORIES))
    types_str = "\n".join(sorted(DOCUMENT_TYPES))
    
    prompt = f"""Analyze this text from a veterinary journal article and extract:
1. Document type (must be one of):
{types_str}

2. Category (must be one of, if applicable):
{categories_str}

3. Title of the article

Important: 
- If type is unclear, classify as "Special Report"
- Category is optional, use "None" if unclear
- Some articles may be purely administrative (like Corrections)

Text:
{text}

Respond in this JSON format:
{{"type": "document type", "category": "category or None", "title": "article title"}}

Example response:
{{"type": "Special Report", "category": "Surgery", "title": "Surgical techniques in canine orthopedics"}}
"""
    
    try:
        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   'model': 'qwen2.5:14b',
                                   'prompt': prompt,
                                   'stream': False
                               })
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        if 'response' in result:
            try:
                # Parse the JSON response from the model
                analysis = json.loads(result['response'])
                
                # Validate document type
                if analysis.get('type') not in DOCUMENT_TYPES:
                    analysis['type'] = "Special Report"
                
                # Validate category
                if analysis.get('category') not in CATEGORIES:
                    analysis['category'] = None
                    
                return analysis
            except json.JSONDecodeError:
                print("Error: Could not parse model response as JSON", file=sys.stderr)
                return None
    except Exception as e:
        print(f"Error calling Ollama API: {e}", file=sys.stderr)
    return None

def find_pdfs(directory):
    """Recursively find all PDF files in directory."""
    pdf_files = []
    for path in Path(directory).rglob('*.pdf'):
        if path.is_file():
            pdf_files.append(path)
    return sorted(pdf_files)

def analyze_pdfs(pdf_dir, output_file=None):
    """Analyze PDFs in directory and save results."""
    if not Path(pdf_dir).exists():
        print(f"Error: Directory {pdf_dir} not found!")
        sys.exit(1)
    
    # Find all PDFs recursively
    pdf_files = find_pdfs(pdf_dir)
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        sys.exit(1)
    
    print(f"Found {len(pdf_files)} PDF files")
    
    # Process each PDF file
    results = []
    for pdf_path in pdf_files:
        print(f"\nAnalyzing {pdf_path}...")
        
        # Extract text from first page
        text = extract_first_page(pdf_path)
        if not text:
            print(f"Could not extract text from {pdf_path}")
            continue
        
        # Analyze text
        analysis = analyze_text(text)
        if analysis:
            results.append({
                'file': str(pdf_path),
                'type': analysis.get('type', 'Special Report'),
                'category': analysis.get('category'),
                'title': analysis.get('title', 'Unknown')
            })
            print(f"Type: {analysis.get('type', 'Special Report')}")
            if analysis.get('category'):
                print(f"Category: {analysis['category']}")
            print(f"Title: {analysis.get('title', 'Unknown')}")
        else:
            print(f"Could not analyze {pdf_path}")
    
    # Save results if output file specified
    if output_file:
        output_path = Path(output_file)
        os.makedirs(output_path.parent, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_path}")
    
    # Print summary
    print("\nDocument type counts:")
    type_counts = {}
    for result in results:
        doc_type = result['type']
        type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
    for doc_type, count in sorted(type_counts.items()):
        print(f"{doc_type}: {count}")
    
    print("\nCategory counts:")
    category_counts = {}
    for result in results:
        if result.get('category'):
            category = result['category']
            category_counts[category] = category_counts.get(category, 0) + 1
    for category, count in sorted(category_counts.items()):
        print(f"{category}: {count}")
    
    return results

def main():
    parser = argparse.ArgumentParser(
        description='Analyze PDF files to determine document type, category, and title.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/pdfs
  %(prog)s /path/to/pdfs -o results.json
  %(prog)s ~/Documents/papers
""")
    
    parser.add_argument('directory',
                       help='Directory to search for PDF files (searched recursively)')
    parser.add_argument('-o', '--output',
                       help='Output file for JSON results (optional)')
    
    args = parser.parse_args()
    
    # Convert to absolute path and expand user directory
    pdf_dir = str(Path(args.directory).expanduser().resolve())
    
    print(f"Starting PDF analysis in {pdf_dir}...")
    analyze_pdfs(pdf_dir, args.output)

if __name__ == "__main__":
    main()