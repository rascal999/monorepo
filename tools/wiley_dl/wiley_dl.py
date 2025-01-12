#!/usr/bin/env python3
import argparse
import os
import re
import requests
import sys
from typing import Optional

def parse_request_file(filepath: str) -> tuple[dict, dict]:
    """
    Parse HTTP request file to extract headers and cookies.
    
    Args:
        filepath: Path to request file
        
    Returns:
        Tuple of (headers dict, cookies dict)
    """
    headers = {}
    cookies = {}
    
    with open(filepath) as f:
        lines = f.readlines()
    
    # Skip first line (request line)
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
            
        key, value = line.split(': ', 1)
        if key == 'Cookie':
            # Parse cookies
            cookie_pairs = value.split('; ')
            for pair in cookie_pairs:
                cookie_key, cookie_value = pair.split('=', 1)
                cookies[cookie_key] = cookie_value
        else:
            headers[key] = value
            
    return headers, cookies

def load_request_data(request_file: str = 'example_reqs.txt') -> tuple[dict, dict]:
    """
    Load headers and cookies from request file.
    
    Args:
        request_file: Name of request file in same directory as script
        
    Returns:
        Tuple of (headers dict, cookies dict)
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    request_path = os.path.join(script_dir, request_file)
    return parse_request_file(request_path)

def download_pdf(prefix: str, number: int, output_dir: str = '.', headers: dict = None, cookies: dict = None) -> Optional[str]:
    """
    Download PDF for a specific DOI number.
    
    Args:
        prefix: DOI prefix (e.g., 'jvim')
        number: DOI number (e.g., 15531)
        output_dir: Directory to save the PDF
    
    Returns:
        Path to downloaded file or None if download failed
    """
    base_url = 'https://onlinelibrary.wiley.com'
    doi = f'{prefix}.{number}'
    url = f'{base_url}/doi/pdfdirect/10.1111/{doi}?download=true'
    
    try:
        if headers is None or cookies is None:
            headers, cookies = load_request_data()
            
        response = requests.get(
            url,
            headers=headers,
            cookies=cookies,
            stream=True
        )
        response.raise_for_status()
        
        # Extract and sanitize filename from Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[-1].strip('"')
        else:
            filename = f'{doi}.pdf'
            
        # Sanitize filename (remove invalid characters)
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filepath using os.path.join for proper path handling
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f'Successfully downloaded {filepath}')
        return filepath
    
    except requests.exceptions.RequestException as e:
        print(f'Failed to download {doi}: {str(e)}', file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description='Download PDFs from Wiley Online Library')
    parser.add_argument('-r', '--request-file', default='example_reqs.txt',
                       help='Request file containing headers (default: example_reqs.txt)')
    parser.add_argument('prefix', help='DOI prefix (e.g., jvim)')
    parser.add_argument('start', type=int, help='Starting DOI number')
    parser.add_argument('end', type=int, nargs='?', help='Ending DOI number (optional)')
    parser.add_argument('-o', '--output-dir', default='.', help='Output directory (default: current directory)')
    
    args = parser.parse_args()
    
    # Load request data once
    try:
        headers, cookies = load_request_data(args.request_file)
    except Exception as e:
        print(f'Error loading request file: {str(e)}', file=sys.stderr)
        sys.exit(1)

    # Handle single number case
    if args.end is None:
        download_pdf(args.prefix, args.start, args.output_dir, headers, cookies)
        return
    
    # Handle range case
    if args.end < args.start:
        print('Error: End number must be greater than or equal to start number', file=sys.stderr)
        sys.exit(1)
    
    for number in range(args.start, args.end + 1):
        download_pdf(args.prefix, number, args.output_dir, headers, cookies)

if __name__ == '__main__':
    main()
