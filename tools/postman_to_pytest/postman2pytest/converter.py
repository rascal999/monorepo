"""
Converter module for transforming Postman elements to pytest code.
"""
import re
import os
import json
from typing import List, Dict, Any, Optional

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

def convert_test_script(script: Dict[str, Any], request_name: str, url: str) -> List[str]:
    """Convert Postman test script to pytest assertions."""
    js_code = script.get('exec', [])
    if not js_code:
        return []
    
    # Join all lines and normalize whitespace
    js_code = ' '.join(line.strip() for line in js_code if line.strip())
    
    # Extract variable assignments from response.json()
    assertions = []
    
    # Handle if statement with variable assignment
    if 'if (pm.response.code === 200)' in js_code or 'if (response.status_code === 200)' in js_code:
        assertions.extend([
            'assert response.status_code == 200',
            f'dynamic_vars["{extract_var_name(js_code)}"] = response.json()["Id"]'
        ])
    else:
        # Add default status code assertion
        assertions.append('assert response.status_code == 200')
    
    return assertions

def get_request_description(request_name: str, description: Optional[str] = None) -> str:
    """Get the description for a request."""
    if description:
        return description
    # Generate description from request name
    name = request_name.lower()
    # Remove HTTP method if present at start
    name = re.sub(r'^(get|post|put|delete|patch)\s+', '', name)
    # Convert to title case and add period
    name = name.title()
    return f"Tests for {name}."

def process_url(url: str) -> str:
    """Process URL to use environment or dynamic variables."""
    def replace_var(match):
        var_name = match.group(1)
        # If variable is defined in .env, use env_vars, otherwise use dynamic_vars
        if var_name in ENV_VARS:
            return f'{{env_vars["{var_name}"]}}'
        return f'{{dynamic_vars["{var_name}"]}}'
    
    # Replace variables with appropriate dict access
    url = re.sub(r'\{\{([^}]+)\}\}', replace_var, url)
    return f'    url = f"{url}"'

def extract_var_name(js_code: str) -> str:
    """Extract variable name from JavaScript code."""
    # Look for pm.environment.set("VAR_NAME", ...) pattern
    match = re.search(r'pm\.environment\.set\("([^"]+)"', js_code)
    if match:
        return match.group(1)
    return "UNKNOWN_VAR"
