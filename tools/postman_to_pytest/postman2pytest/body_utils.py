"""
Utilities for converting Postman request bodies to pytest format.
"""
import re
import json
import os
from typing import Dict, Any, List, Set

def _get_env_vars() -> Set[str]:
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

def convert_request_body(body: Dict[str, Any]) -> str:
    """Convert Postman request body to Python dict string."""
    if not body or not body.get('raw'):
        return ''
    
    raw_body = body.get('raw', '')
    
    # Get the body content
    if isinstance(raw_body, dict):
        # If raw_body is already a dict, use it directly
        body_dict = raw_body
    elif isinstance(raw_body, str):
        # If raw_body is a string, try to parse it
        try:
            # Remove comments and normalize line endings
            body_lines = [line for line in raw_body.split('\n') if not line.strip().startswith('//')]
            body_str = '\n'.join(body_lines)
            
            # Add missing commas between dictionary items
            body_str = re.sub(r'"\s*\n\s*"', '",\n"', body_str)
            body_str = re.sub(r'}\s*\n\s*"', '},\n"', body_str)
            body_str = re.sub(r'"\s*\n\s*{', '",\n{', body_str)
            body_str = re.sub(r'}\s*\n\s*{', '},\n{', body_str)
            body_str = re.sub(r'([^,{])\s*\n\s*}', r'\1\n}', body_str)
            
            try:
                # Parse the JSON string
                body_dict = json.loads(body_str)
            except json.JSONDecodeError:
                # If JSON parsing fails, use raw body
                return f'    body = {body_str}'
        except (AttributeError, TypeError):
            # If string operations fail, use raw body
            return f'    body = {raw_body}'
    else:
        # If raw_body is neither dict nor string, return empty body
        return ''
    
    # Convert to Python dict format with proper formatting
    lines = ['    body = {']
    lines.extend(_format_dict(body_dict))
    lines.append('    }')
    return '\n'.join(lines)

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
            if isinstance(value, list):
                # Handle lists
                list_items = []
                for item in value:
                    if isinstance(item, str):
                        # Handle Postman variables in list items
                        if item.startswith('{{') and item.endswith('}}'):
                            var_name = item[2:-2]  # Remove {{ and }}
                            if var_name.startswith('$'):
                                # It's a faker variable
                                list_items.append(f'faker_vars["{var_name}"]')
                            elif var_name in ENV_VARS:
                                # It's an environment variable
                                list_items.append(f'env_vars["{var_name}"]')
                            else:
                                # It's a dynamic variable
                                list_items.append(f'dynamic_vars["{var_name}"]')
                        else:
                            list_items.append(f'"{item}"')
                    elif isinstance(item, dict):
                        # Handle nested dictionaries in lists
                        nested_lines = _format_dict(item, indent + 4)
                        list_items.append('{\n' + '\n'.join(nested_lines) + '\n' + ' ' * (indent + 4) + '}')
                    else:
                        list_items.append(str(item))
                value = f'[{", ".join(list_items)}]'
                result.append(' ' * indent + f'"{key}": {value}' + ('' if is_last else ','))
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
                        elif var_name in ENV_VARS:
                            # It's an environment variable
                            value = f'env_vars["{var_name}"]'
                        else:
                            # It's a dynamic variable
                            value = f'dynamic_vars["{var_name}"]'
                    else:
                        value = f'"{value}"'
                result.append(' ' * indent + f'"{key}": {value}' + ('' if is_last else ','))
    return result
