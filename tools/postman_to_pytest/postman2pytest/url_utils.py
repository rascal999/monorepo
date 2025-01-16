"""
Utilities for processing and formatting URLs.
"""
import re

def process_url(url: str) -> str:
    """Process URL template variables."""
    # Handle environment variables
    url = url.replace('{{ENV_URL}}', '{env_vars["ENV_URL"]}')
    url = url.replace('{{CLIENT_ID}}', '{env_vars["CLIENT_ID"]}')
    
    # Handle URL-encoded dynamic variables
    url = url.replace('%7B', '{').replace('%7D', '}')
    
    # Replace dynamic variables with proper references
    for match in re.finditer(r'{{([^}]+)}}', url):
        var = match.group(1)
        if var not in ('ENV_URL', 'CLIENT_ID'):
            url = url.replace(f'{{{{{var}}}}}', f'{{dynamic_vars["{var}"]}}')
    
    return f'    url = f"{url}"'
