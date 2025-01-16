"""
Utilities for handling name sanitization and descriptions.
"""
import re

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

def get_request_description(request_name: str, description: str = None) -> str:
    """Get the description for a request."""
    if description:
        return description
    # Generate description from request name
    name = request_name.lower()
    # Remove HTTP method if present at start
    name = re.sub(r'^(get|post|put|delete|patch)\s+', '', name)
    return f"Test for {name}."
