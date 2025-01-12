"""Variable extraction and management utilities."""

import re
from typing import Set

def extract_variables(text: str) -> Set[str]:
    """Extract Postman variables from text.
    
    Args:
        text: Text containing Postman variables in {{variable}} format
        
    Returns:
        Set of variable names without the curly braces
    """
    pattern = r'\{\{([^}]+)\}\}'
    return set(re.findall(pattern, text))

def replace_variables(text: str, variables: Set[str], sanitize_func) -> str:
    """Replace Postman variables with Python format strings.
    
    Args:
        text: Text containing Postman variables
        variables: Set of variable names to replace
        sanitize_func: Function to sanitize variable names
        
    Returns:
        Text with variables replaced with Python format strings
    """
    result = text
    for var in variables:
        result = result.replace(
            f"{{{{{var}}}}}",
            "{" + sanitize_func(var.lower()) + "}"
        )
    return result

def collect_variables_from_request(item: 'PostmanItem') -> Set[str]:
    """Extract all variables from a Postman request.
    
    Checks URL, headers, and body for variables.
    
    Args:
        item: PostmanItem containing the request
        
    Returns:
        Set of all unique variable names found
    """
    variables = set()
    
    # Check URL
    url = item.request.url.raw if isinstance(item.request.url, str) else item.request.url.raw
    variables.update(extract_variables(url))
    
    # Check headers
    if item.request.header:
        for header in item.request.header:
            if not header.disabled:
                variables.update(extract_variables(header.value))
    
    # Check body
    if item.request.body and item.request.body.raw:
        variables.update(extract_variables(item.request.body.raw))
    
    return variables
