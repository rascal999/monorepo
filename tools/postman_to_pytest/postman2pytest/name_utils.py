"""
Utilities for handling name sanitization and descriptions.
"""
import re

def normalize_name(name: str) -> str:
    """Normalize a name to a consistent format."""
    # Remove test_ prefix if present
    if name.startswith('test_'):
        name = name[5:]
    
    # Replace non-alphanumeric chars with underscore
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Remove "_a_" from names
    name = re.sub(r'_a_', '_', name)
    # Replace double underscores with single
    name = re.sub(r'__+', '_', name)
    # Remove trailing underscores
    name = name.rstrip('_')
    return name.lower()

def sanitize_name(name: str, is_filename: bool = False) -> str:
    """Convert a request name to a valid Python identifier."""
    # Extract the base name without any prefixes
    base_name = name
    if '/' in base_name:
        base_name = base_name.split('/')[-1]
    
    # Remove any HTTP method prefix
    base_name = re.sub(r'^(GET|POST|PUT|DELETE|PATCH)\s+', '', base_name)
    
    # Normalize the name
    normalized = normalize_name(base_name)
    
    if is_filename:
        # For filenames, we want test_name
        return f"test_{normalized}"
    else:
        # For function names and dependency names, we want just the normalized name
        return normalized

def get_request_description(request_name: str, description: str = None) -> str:
    """Get the description for a request."""
    if description:
        return description
    # Generate description from request name
    name = request_name.lower()
    # Remove HTTP method if present at start
    name = re.sub(r'^(get|post|put|delete|patch)\s+', '', name)
    return f"Test for {name}."
