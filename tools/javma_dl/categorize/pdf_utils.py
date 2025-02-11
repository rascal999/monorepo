"""Utilities for PDF operations."""

import PyPDF2
import logging

def extract_first_pages(pdf_path, num_pages=2):
    """Extract text from first N pages of PDF."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for i in range(min(num_pages, len(reader.pages))):
                text += reader.pages[i].extract_text() + "\n"
            return text
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {e}")
        return None