#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re
import sys
from pathlib import Path
import time

def get_xml_links(url):
    """Extract all XML links from the given URL."""
    try:
        # Add headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links that match the pattern
        xml_links = []
        pattern = re.compile(r'/view/journals/javma/\d+/\d+/[^/]+\.xml$')
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if pattern.search(href):
                if not href.startswith('http'):
                    href = 'https://avmajournals.avma.org' + href
                xml_links.append(href)
        
        return xml_links
    
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        return []

def main():
    base_url = "https://avmajournals.avma.org/browse.pagedlist.gridpager/{page}?access=all&f_0=date&pageSize=50&q_0=%7BFROM_DATE%3D%3D2019%7D%2C%7BTO_DATE%3D%3D2024%7D&sort=date&type_0=journalarticle"
    all_xml_links = set()  # Using set to avoid duplicates
    
    print("Fetching XML links from all pages...")
    
    # Iterate through pages 1 to 71
    for page in range(1, 72):
        url = base_url.format(page=page)
        print(f"Processing page {page}/71...")
        
        xml_links = get_xml_links(url)
        all_xml_links.update(xml_links)
        
        # Add a small delay between requests to be polite
        time.sleep(1)
    
    if not all_xml_links:
        print("No XML links found!")
        return
    
    # Create output directory if it doesn't exist
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Save links to file
    output_file = output_dir / 'javma_links.txt'
    with open(output_file, 'w') as f:
        for link in sorted(all_xml_links):  # Sort links for consistency
            f.write(f"{link}\n")
    
    print(f"Found {len(all_xml_links)} unique XML links")
    print(f"Links saved to {output_file}")

if __name__ == "__main__":
    main()