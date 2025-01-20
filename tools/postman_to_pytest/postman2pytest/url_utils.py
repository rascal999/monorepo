"""
Utilities for processing and formatting URLs.
"""
import re
import os

def _get_env_vars() -> set:
    """Get environment variables from .env file."""
    env_vars = set()
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key = line.split('=')[0].strip()
                    env_vars.add(key)
    return env_vars

# Load environment variables once at module import
ENV_VARS = _get_env_vars()

def process_url(url: str) -> str:
    """Process URL template variables."""
    # Handle URL-encoded dynamic variables
    url = url.replace('%7B', '{').replace('%7D', '}')
    
    # Replace variables with proper references
    for match in re.finditer(r'{{([^}]+)}}', url):
        var = match.group(1)
        if var in ENV_VARS:
            url = url.replace(f'{{{{{var}}}}}', f'{{env_vars["{var}"]}}')
        else:
            url = url.replace(f'{{{{{var}}}}}', f'{{dynamic_vars["{var}"]}}')
    
    return f'    url = f"{url}"'
