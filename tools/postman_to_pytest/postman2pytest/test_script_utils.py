"""
Utilities for converting Postman test scripts to pytest assertions.
"""
import re
from typing import List, Dict, Any, Optional

def convert_test_script(script: Dict[str, Any], request_name: str, url: str) -> List[str]:
    """Convert Postman test script to pytest assertions."""
    js_code = script.get('exec', [])
    if not js_code:
        return []
    
    # Join all lines and normalize whitespace
    js_code = ' '.join(line.strip() for line in js_code if line.strip())
    
    assertions = []
    
    # Handle conditional variable assignment
    if 'if (pm.response.code === 200)' in js_code or 'if (response.status_code === 200)' in js_code:
        assertions.extend([
            'assert response.status_code == 200',
            'response_data = response.json()',
            f'dynamic_vars["{extract_var_name(js_code)}"] = response_data["Id"]'
        ])
    # Handle direct variable assignment
    elif 'pm.environment.set' in js_code:
        assertions.extend([
            'assert response.status_code == 200',
            f'dynamic_vars["{extract_var_name(js_code)}"] = response.json()["Id"]'
        ])
    # Default case
    else:
        assertions.append('assert response.status_code == 200')
    
    return assertions

def extract_var_name(js_code: str) -> str:
    """Extract variable name from JavaScript code."""
    # Look for pm.environment.set("VAR_NAME", ...) pattern
    match = re.search(r'pm\.environment\.set\("([^"]+)"', js_code)
    if match:
        return match.group(1)
    return "UNKNOWN_VAR"

def convert_if_statement(js_code: str) -> List[str]:
    """Convert JavaScript if statement to Python."""
    lines = []
    
    # Handle if (pm.response.code === 200) { ... }
    if 'if (pm.response.code === 200)' in js_code:
        lines.extend([
            'if response.status_code == 200:',
            '    response_data = response.json()',
            f'    dynamic_vars["{extract_var_name(js_code)}"] = response_data["Id"]'
        ])
    
    return lines

def convert_assertion(js_code: str) -> Optional[str]:
    """Convert JavaScript assertion to Python."""
    # Handle pm.expect(pm.response.code).to.equal(200)
    if 'pm.expect(pm.response.code).to.equal(200)' in js_code:
        return 'assert response.status_code == 200'
    
    # Handle pm.expect(response.json().Id).to.exist
    if 'pm.expect(response.json().Id).to.exist' in js_code:
        return 'assert "Id" in response.json()'
    
    return None

def convert_variable_assignment(js_code: str) -> Optional[str]:
    """Convert JavaScript variable assignment to Python."""
    # Handle pm.environment.set("VAR_NAME", response.json().Id)
    match = re.search(r'pm\.environment\.set\("([^"]+)",\s*response\.json\(\)\.Id\)', js_code)
    if match:
        var_name = match.group(1)
        return f'dynamic_vars["{var_name}"] = response.json()["Id"]'
    
    return None
