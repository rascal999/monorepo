"""
Utilities for converting Postman request bodies to pytest format.
"""
import re
import json
from typing import Dict, Any, List

def convert_request_body(body: Dict[str, Any]) -> str:
    """Convert Postman request body to Python dict string."""
    if not body or not body.get('raw'):
        return ''
    
    raw_body = body['raw']
    # Remove comments
    body_lines = [line for line in raw_body.split('\n') if not line.strip().startswith('//')]
    body_str = '\n'.join(body_lines)
    
    try:
        # Add missing commas between dictionary items
        body_str = re.sub(r'"\s*\n\s*"', '",\n"', body_str)
        body_str = re.sub(r'}\s*\n\s*"', '},\n"', body_str)
        body_str = re.sub(r'"\s*\n\s*{', '",\n{', body_str)
        body_str = re.sub(r'}\s*\n\s*{', '},\n{', body_str)
        body_str = re.sub(r'([^,{])\s*\n\s*}', r'\1\n}', body_str)
        
        body_dict = json.loads(body_str)
        
        # Convert to Python dict format with proper formatting
        lines = ['    body = {']
        lines.extend(_format_dict(body_dict))
        lines.append('    }')
        return '\n'.join(lines)
    except json.JSONDecodeError:
        # If JSON parsing fails, use raw body
        return f'    body = {body_str}'

def _format_dict(d: Dict[str, Any], indent: int = 8) -> List[str]:
    """Format a dictionary as Python code with proper indentation."""
    result = []
    items = list(d.items())
    for i, (key, value) in enumerate(items):
        is_last = i == len(items) - 1
        if isinstance(value, dict):
            result.append(' ' * indent + f'"{key}": {{')
            nested = _format_dict(value, indent + 4)
            result.extend(nested)
            result.append(' ' * indent + '}' + ('' if is_last else ','))
        else:
            if isinstance(value, bool):
                value = str(value)
            elif value is None:
                value = 'None'
            elif isinstance(value, str):
                # Handle Postman variables
                if value.startswith('{{') and value.endswith('}}'):
                    var_name = value[2:-2]  # Remove {{ and }}
                    if var_name.startswith('$'):
                        # It's a faker variable
                        value = f'faker_vars["{var_name}"]'
                    else:
                        # It's a dynamic variable
                        value = f'dynamic_vars["{var_name}"]'
                else:
                    value = f'"{value}"'
            result.append(' ' * indent + f'"{key}": {value}' + ('' if is_last else ','))
    return result
