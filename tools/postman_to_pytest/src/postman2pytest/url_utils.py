"""URL and path handling utilities for test generation."""

import re
from pathlib import Path
from typing import List, Union
from urllib.parse import urlparse

def sanitize_name(name: str, preserve_case: bool = False) -> str:
    """Convert a name to a valid Python identifier.
    
    Args:
        name: Name to sanitize
        preserve_case: If True, preserve original case, otherwise convert to lowercase
    """
    # Replace non-alphanumeric chars with underscore
    name = re.sub(r'\W+', '_', name)
    # Ensure name starts with letter
    if name[0].isdigit():
        name = f"test_{name}"
    return name if preserve_case else name.lower()

def extract_api_path(url: Union[str, 'RequestUrl']) -> List[str]:
    """Extract API path components from URL."""
    if isinstance(url, str):
        # Parse URL string to get path components
        parsed = urlparse(url)
        # Remove leading/trailing slashes and split
        path = parsed.path.strip('/')
        return path.split('/') if path else []
    else:
        # For RequestUrl objects, path is already split
        return url.path if url.path else []

def create_test_file_path(output_dir: Path, item: 'PostmanItem') -> Path:
    """Create the appropriate test file path for a Postman request."""
    method = item.request.method.lower()
    
    # Extract API path components
    path_components = extract_api_path(item.request.url)
    
    # Create directory structure based on API path
    dir_path = output_dir
    if path_components:
        dir_path = dir_path.joinpath(*path_components)
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create file name from method and last path component or item name
    name = path_components[-1] if path_components else sanitize_name(item.name)
    file_path = dir_path / f"test_{method}_{name}.py"
    
    return file_path

def format_url(url: str, variables: set, sanitize_func=sanitize_name) -> str:
    """Format URL with proper scheme and variable substitution."""
    # Replace variables with format strings
    formatted_url = url
    for var in variables:
        formatted_url = formatted_url.replace(
            f"{{{{{var}}}}}",
            "{" + sanitize_func(var, preserve_case=True) + "}"
        )
    
    # Extract URL parts
    parsed = urlparse(formatted_url)
    
    # If no scheme or host, use urljoin with base_url
    if not (parsed.scheme and parsed.netloc):
        # Remove any leading/trailing slashes for proper joining
        path = formatted_url.strip('/')
        return f"urljoin(base_url, '{path}')"
    
    return f"f'{formatted_url}'"
