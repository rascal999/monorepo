#!/usr/bin/env python3

import requests
import sys
from pathlib import Path
import time
import os

def download_pdf(url, output_dir):
    """Download a PDF file from the given URL."""
    try:
        # Extract filename from URL
        filename = url.split('/')[-1]
        output_path = output_dir / filename
        
        # Skip if file already exists
        if output_path.exists():
            print(f"Skipping {filename} - already exists")
            return True
        
        # Add headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Stream the download to handle large files
        print(f"Downloading {filename}...")
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Check if the response is actually a PDF
        content_type = response.headers.get('content-type', '').lower()
        if 'pdf' not in content_type:
            print(f"Warning: {filename} might not be a PDF (Content-Type: {content_type})")
        
        # Save the PDF
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"Successfully downloaded {filename}")
        return True
        
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}", file=sys.stderr)
        return False

def main():
    # Setup paths
    script_dir = Path(__file__).parent
    input_file = script_dir / 'output' / 'javma_links.txt'
    output_dir = script_dir / 'output' / 'pdfs'
    
    # Check if input file exists
    if not input_file.exists():
        print(f"Error: Input file {input_file} not found!")
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read URLs from file
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    total_urls = len(urls)
    print(f"Found {total_urls} URLs to process")
    
    # Download PDFs
    successful = 0
    for i, url in enumerate(urls, 1):
        print(f"\nProcessing {i}/{total_urls}")
        if download_pdf(url, output_dir):
            successful += 1
        
        # Add a small delay between downloads to be polite
        if i < total_urls:
            time.sleep(1)
    
    print(f"\nDownload complete! Successfully downloaded {successful}/{total_urls} PDFs")
    print(f"PDFs saved to: {output_dir}")

if __name__ == "__main__":
    main()