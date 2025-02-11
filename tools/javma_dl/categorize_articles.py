#!/usr/bin/env python3

import os
from pathlib import Path
import PyPDF2
import sys
import json
import requests
import re

# Keywords for categorization
SURGICAL_KEYWORDS = {
    'surgery', 'surgical', 'postoperative', 'preoperative', 'intraoperative',
    'incision', 'suture', 'anastomosis', 'resection', 'amputation',
    'laparoscopic', 'laparotomy', 'arthroscopy', 'implant', 'graft',
    'reconstruction', 'repair', 'procedure', 'technique', 'approach',
    'dissection', 'excision', 'removal', 'fixation', 'debridement'
}

INTERNAL_MEDICINE_KEYWORDS = {
    'diagnosis', 'treatment', 'therapy', 'medication', 'drug',
    'clinical signs', 'symptoms', 'prognosis', 'management',
    'pathology', 'disease', 'condition', 'syndrome', 'disorder',
    'infection', 'inflammatory', 'chronic', 'acute', 'assessment',
    'evaluation', 'diagnostic', 'laboratory', 'imaging', 'medicine'
}

def extract_text(pdf_path):
    """Extract text from PDF."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.lower()  # Convert to lowercase for easier matching
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}", file=sys.stderr)
    return None

def count_keywords(text, keywords):
    """Count occurrences of keywords in text."""
    if not text:
        return 0
    count = 0
    for keyword in keywords:
        count += len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
    return count

def analyze_with_ollama(text):
    """Use Ollama to analyze text and determine if it's surgical or internal medicine."""
    prompt = f"""Analyze this veterinary journal article text and determine if it's primarily about:
1. Surgery/surgical procedures
2. Internal medicine/medical management

Consider the main focus of the study, not just mentioned procedures or treatments.

Text:
{text[:2000]}  # Use first 2000 chars for context

Respond with just one word: either "surgical" or "medical"
"""
    
    try:
        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   'model': 'qwen2.5:14b',
                                   'prompt': prompt,
                                   'stream': False
                               })
        response.raise_for_status()
        
        result = response.json()
        if 'response' in result:
            answer = result['response'].strip().lower()
            if answer in ['surgical', 'medical']:
                return 'surgical' if answer == 'surgical' else 'internal_medicine'
    except Exception as e:
        print(f"Error calling Ollama API: {e}", file=sys.stderr)
    return None

def categorize_article(pdf_path):
    """Categorize article as surgical or internal medicine."""
    text = extract_text(pdf_path)
    if not text:
        return None
    
    # Count keywords
    surgical_count = count_keywords(text, SURGICAL_KEYWORDS)
    internal_count = count_keywords(text, INTERNAL_MEDICINE_KEYWORDS)
    
    # If one category has significantly more matches
    if surgical_count > internal_count * 1.5:
        return 'surgical'
    elif internal_count > surgical_count * 1.5:
        return 'internal_medicine'
    
    # If it's close, use Ollama for more nuanced analysis
    return analyze_with_ollama(text)

def main():
    script_dir = Path(__file__).parent
    input_file = script_dir / 'javma_journal_articles.txt'
    
    if not input_file.exists():
        print(f"Error: Input file {input_file} not found!")
        sys.exit(1)
    
    # Create output files
    surgical_file = script_dir / 'surgical_articles.txt'
    internal_file = script_dir / 'internal_medicine_articles.txt'
    unknown_file = script_dir / 'uncategorized_articles.txt'
    
    # Read and process articles
    with open(input_file, 'r') as f:
        articles = [line.strip() for line in f if line.strip()]
    
    total = len(articles)
    print(f"Found {total} articles to categorize")
    
    surgical_articles = []
    internal_articles = []
    unknown_articles = []
    
    for i, article_path in enumerate(articles, 1):
        print(f"\rProcessing article {i}/{total}: {Path(article_path).name}", end='', flush=True)
        
        category = categorize_article(article_path)
        
        # Clear progress line before printing result
        print("\r" + " " * 80 + "\r", end='', flush=True)
        
        if category == 'surgical':
            surgical_articles.append(article_path)
            print(f"Surgical: {Path(article_path).name}")
        elif category == 'internal_medicine':
            internal_articles.append(article_path)
            print(f"Internal Medicine: {Path(article_path).name}")
        else:
            unknown_articles.append(article_path)
            print(f"Uncategorized: {Path(article_path).name}")
    
    # Save results
    with open(surgical_file, 'w') as f:
        f.write('\n'.join(surgical_articles) + '\n')
    
    with open(internal_file, 'w') as f:
        f.write('\n'.join(internal_articles) + '\n')
    
    if unknown_articles:
        with open(unknown_file, 'w') as f:
            f.write('\n'.join(unknown_articles) + '\n')
    
    # Print summary
    print("\nCategorization complete!")
    print(f"Surgical articles: {len(surgical_articles)}")
    print(f"Internal medicine articles: {len(internal_articles)}")
    if unknown_articles:
        print(f"Uncategorized articles: {len(unknown_articles)}")
    
    print(f"\nResults saved to:")
    print(f"- {surgical_file}")
    print(f"- {internal_file}")
    if unknown_articles:
        print(f"- {unknown_file}")

if __name__ == "__main__":
    main()