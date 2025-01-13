"""URL handling utilities."""

import re
from pathlib import Path
from typing import Dict
from .variable_types import Variable


def sanitize_name(name: str) -> str:
    """Convert a name to a valid Python identifier.
    
    Args:
        name: Name to sanitize
        
    Returns:
        Sanitized name that is a valid Python identifier
    """
    # Replace non-alphanumeric chars with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # Ensure it starts with a letter or underscore
    if sanitized and sanitized[0].isdigit():
        sanitized = f"_{sanitized}"
        
    # Convert to lowercase for consistency
    return sanitized.lower()


def format_url(url: str, variables: Dict[str, Variable], sanitize_func) -> str:
    """Format a URL template with variable placeholders.
    
    Args:
        url: URL template with {{variable}} placeholders
        variables: Dictionary of variables
        sanitize_func: Function to sanitize variable names
        
    Returns:
        URL with Python format string placeholders
    """
    result = url
    
    # Replace Postman variable syntax with Python format string syntax
    for var_name in variables:
        if var_name.startswith('$random'):  # Postman dynamic variable
            result = result.replace(
                var_name,  # Direct replacement without {{...}}
                "{" + var_name[1:] + "}"  # Remove $ prefix for Python identifiers
            )
        else:  # Regular Postman variable
            result = result.replace(
                f"{{{{{var_name}}}}}",  # Use original case from collection
                "{" + var_name + "}"  # Keep original case without sanitizing
            )
    
    return result


def create_test_file_path(output_dir: Path, item: 'PostmanItem') -> Path:
    """Create a test file path from a Postman request.
    
    Args:
        output_dir: Base output directory
        item: PostmanItem containing the request
        
    Returns:
        Path object for the test file
    """
    # Get URL path components
    url = item.request.url.raw if isinstance(item.request.url, str) else item.request.url.raw
    
    # Extract path after domain
    path_match = re.search(r'https?://[^/]+(/.*)?', url)
    if path_match and path_match.group(1):
        path = path_match.group(1).rstrip('/')
    else:
        path = ''
    
    # Convert path to directory structure
    parts = [p for p in path.split('/') if p]
    if not parts:
        parts = ['root']
    
    # Create test file name from last path component and request method
    method = item.request.method.lower()
    name = sanitize_name(parts[-1])
    filename = f"test_{method}_{name}.py"
    
    # Construct full path
    file_path = output_dir
    for part in parts[:-1]:  # Create intermediate directories
        file_path = file_path / sanitize_name(part)
    file_path = file_path / filename
    
    return file_path
