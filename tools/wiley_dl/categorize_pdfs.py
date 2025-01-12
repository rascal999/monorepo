#!/usr/bin/env python3
import argparse
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2

# Medical specialty keywords
SPECIALTY_KEYWORDS = {
    'cardiology': ['heart', 'cardiac', 'cardiovascular', 'arrhythmia', 'myocardial'],
    'neurology': ['brain', 'neural', 'nervous', 'seizure', 'neurological'],
    'pulmonology': ['lung', 'respiratory', 'pulmonary', 'bronchial', 'airway'],
    'endocrinology': ['hormone', 'thyroid', 'diabetes', 'endocrine', 'metabolic'],
    'gastroenterology': ['stomach', 'intestinal', 'digestive', 'gastrointestinal', 'bowel'],
    'hepatology': ['liver', 'hepatic', 'biliary', 'gallbladder'],
    'haematology': ['blood', 'anemia', 'coagulation', 'platelet'],
    'immunology': ['immune', 'allergy', 'autoimmune', 'lymphocyte'],
    'nephrology': ['kidney', 'renal', 'urinary'],
    'urology': ['bladder', 'prostate', 'urinary tract'],
    'oncology': ['cancer', 'tumor', 'neoplasm', 'malignant']
}

def extract_text_from_pdf(pdf_path: str, max_pages: int = 3) -> str:
    """
    Extract text from the first few pages of a PDF file.
    
    Args:
        pdf_path: Path to PDF file
        max_pages: Maximum number of pages to extract (default: 3)
    
    Returns:
        Extracted text as string
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = min(len(reader.pages), max_pages)
            text = ''
            for i in range(num_pages):
                text += reader.pages[i].extract_text()
            return text.lower()
    except Exception as e:
        print(f"Warning: Could not extract text from PDF: {str(e)}")
        return ''

def analyze_text(text: str) -> Dict[str, int]:
    """
    Analyze text for medical specialty keywords.
    
    Args:
        text: Text to analyze
    
    Returns:
        Dictionary mapping specialties to keyword match counts
    """
    specialty_counts = {specialty: 0 for specialty in SPECIALTY_KEYWORDS}
    
    for specialty, keywords in SPECIALTY_KEYWORDS.items():
        for keyword in keywords:
            specialty_counts[specialty] += text.count(keyword)
            
    return specialty_counts

def determine_specialty(text: str, filename: str) -> List[str]:
    """
    Determine medical specialties based on text content and filename.
    
    Args:
        text: Text content to analyze
        filename: Filename to check for keywords
    
    Returns:
        List of matching specialties, sorted by relevance
    """
    # Analyze both content and filename
    content_counts = analyze_text(text)
    filename_counts = analyze_text(filename.lower())
    
    # Combine counts, giving more weight to filename matches
    combined_counts = content_counts.copy()
    for specialty, count in filename_counts.items():
        combined_counts[specialty] += count * 2
    
    # Filter out specialties with no matches
    matches = [(specialty, count) for specialty, count in combined_counts.items() if count > 0]
    
    # Sort by count in descending order
    matches.sort(key=lambda x: x[1], reverse=True)
    
    # Return specialties that have matches
    return [specialty for specialty, count in matches]

def categorize_pdf(pdf_path: str, base_dir: str) -> Optional[str]:
    """
    Categorize PDF file based on content and move to appropriate directory.
    
    Args:
        pdf_path: Path to PDF file
        base_dir: Base directory for categorized files
    
    Returns:
        New path of categorized file or None if categorization failed
    """
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        filename = os.path.basename(pdf_path)
        
        # Determine specialties
        specialties = determine_specialty(text, filename)
        
        if not specialties:
            print(f"Warning: Could not determine specialty for {filename}")
            specialty_dir = 'uncategorized'
        else:
            # Use primary specialty for directory
            specialty_dir = specialties[0]
            if len(specialties) > 1:
                print(f"Note: {filename} matches multiple specialties: {', '.join(specialties)}")
        
        # Create specialty directory
        target_dir = os.path.join(base_dir, specialty_dir)
        os.makedirs(target_dir, exist_ok=True)
        
        # Move file to specialty directory
        new_path = os.path.join(target_dir, filename)
        os.rename(pdf_path, new_path)
        print(f"Moved {filename} to {specialty_dir}/")
        
        return new_path
        
    except Exception as e:
        print(f"Error categorizing {pdf_path}: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Categorize medical PDFs by specialty')
    parser.add_argument('input_dir', help='Directory containing PDF files')
    parser.add_argument('-o', '--output-dir', help='Output directory for categorized files (default: input_dir)')
    
    args = parser.parse_args()
    output_dir = args.output_dir or args.input_dir
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all PDFs recursively
    for root, _, files in os.walk(args.input_dir):
        for filename in files:
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, filename)
                categorize_pdf(pdf_path, output_dir)

if __name__ == '__main__':
    main()
