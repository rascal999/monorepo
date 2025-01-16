"""
Converter module for transforming Postman elements to pytest equivalents.
"""
import re
import json
from typing import List, Dict, Any

def sanitize_name(name: str) -> str:
    """Convert a request name to a valid Python function name."""
    # Remove HTTP method prefix if present
    name = re.sub(r'^(GET|POST|PUT|DELETE|PATCH)\s+', '', name)
    # Replace non-alphanumeric chars with underscore
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Ensure name starts with test_
    if not name.startswith('test_'):
        name = 'test_' + name
    return name.lower()

def convert_test_script(script: Dict[str, Any]) -> List[str]:
    """Convert Postman test script to pytest assertions."""
    js_code = script.get('exec', [])
    if not js_code:
        return []
    
    assertions = []
    for line in js_code:
        # Convert pm.response.code assertion
        if 'pm.response.code' in line:
            assertions.append('assert response.status_code == 200')
        
        # Convert pm.environment.set
        if 'pm.environment.set' in line:
            match = re.search(r'set\("([^"]+)",\s*([^)]+)\)', line)
            if match:
                var_name, var_value = match.groups()
                if 'response.json()' in var_value:
                    assertions.append(f'dynamic_vars["{var_name}"] = response.json()["Id"]')

    return assertions

def convert_request_body(body: Dict[str, Any]) -> str:
    """Convert Postman request body to Python dict string."""
    if not body or not body.get('raw'):
        return ''
    
    raw_body = body['raw']
    # Remove comments
    body_lines = [line for line in raw_body.split('\n') if not line.strip().startswith('//')]
    body_str = '\n'.join(body_lines)
    
    try:
        body_dict = json.loads(body_str)
        # Convert to Python dict format
        body_str = json.dumps(body_dict, indent=4)
        # Replace JSON null with Python None
        body_str = body_str.replace('null', 'None')
        # Format as Python dict with proper indentation
        lines = ['    body = {']
        for line in body_str.split('\n')[1:-1]:  # Skip first and last braces
            lines.append(f'        {line}')
        lines.append('    }')
        return '\n'.join(lines)
    except json.JSONDecodeError:
        # If JSON parsing fails, use raw body
        return f'    body = {body_str}'

def get_request_description(request_name: str, description: str = None) -> str:
    """Get the description for a request."""
    if description:
        return description
    # Generate description from request name
    name = request_name.lower()
    # Remove HTTP method if present at start
    name = re.sub(r'^(get|post|put|delete|patch)\s+', '', name)
    return f"Test for {name}."

def process_url(url: str) -> str:
    """Process URL template variables."""
    url = url.replace('{{ENV_URL}}', '{env_vars["ENV_URL"]}')
    url = url.replace('{{CLIENT_ID}}', '{env_vars["CLIENT_ID"]}')
    return f'    url = f"{url}"'
