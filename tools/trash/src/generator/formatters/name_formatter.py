"""Name formatting utilities for test generation."""

import re


def format_test_name(endpoint: str, method: str = None, include_method: bool = False) -> str:
    """Format endpoint as test function name.

    Args:
        endpoint: Endpoint path or name
        method: HTTP method (will be included in name if include_method is True)
        include_method: Whether to include the HTTP method in the name

    Returns:
        Formatted test function name
    """
    # Convert to lowercase first
    name = endpoint.lower()
    # Replace any special characters (including parentheses) with spaces
    name = re.sub(r'[^a-z0-9\s]', ' ', name)
    # Convert multiple spaces to single space and trim
    name = ' '.join(name.split())
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    
    # Add method prefix if provided and include_method is True
    if method and include_method:
        method_prefix = method.lower()
        return f"test_test_{method_prefix}_{name}"
    
    return f"test_test_{name}"
