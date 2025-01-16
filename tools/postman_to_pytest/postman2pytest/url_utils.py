"""
Utilities for processing and formatting URLs.
"""
import re

def process_url(url: str) -> str:
    """Process URL template variables."""
    # First handle environment variables
    url = url.replace('{{ENV_URL}}', '{env_vars["ENV_URL"]}')
    url = url.replace('{{CLIENT_ID}}', '{env_vars["CLIENT_ID"]}')
    
    # Handle URL-encoded dynamic variables
    url = url.replace('%7B', '{').replace('%7D', '}')
    
    # Extract all dynamic variables
    dynamic_vars = re.findall(r'{([^}]+)}', url)
    
    # Generate the complete URL string with proper variable references
    lines = [
        '    # Create dynamic variable references',
    ]
    
    # Add dynamic variable assignments
    for var in dynamic_vars:
        if var not in ('env_vars["ENV_URL"]', 'env_vars["CLIENT_ID"]'):
            clean_var = var.strip('{}')
            lines.append(f'    dyn_{clean_var} = dynamic_vars["{clean_var}"]')
    
    # Build URL using format strings
    url_parts = []
    current_pos = 0
    for match in re.finditer(r'{([^}]+)}', url):
        var = match.group(1)
        # Add text before the variable
        url_parts.append(url[current_pos:match.start()])
        # Add the variable reference
        if var not in ('env_vars["ENV_URL"]', 'env_vars["CLIENT_ID"]'):
            clean_var = var.strip('{}')
            url_parts.append(f'{{dyn_{clean_var}}}')
        else:
            url_parts.append(f'{{{var}}}')
        current_pos = match.end()
    # Add remaining text
    url_parts.append(url[current_pos:])
    
    # Join URL parts and create f-string
    url = ''.join(url_parts)
    # Remove any extra closing braces
    url = url.replace('}}}', '}').replace('}}', '}')
    lines.append(f'    url = f"{url}"')
    
    return '\n'.join(lines)
