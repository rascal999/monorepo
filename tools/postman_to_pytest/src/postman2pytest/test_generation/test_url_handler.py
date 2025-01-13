"""URL handling utilities for test generation."""

from pathlib import Path
from typing import Dict, Set, Tuple
from ..core.variable_types import Variable, VariableType


def process_url_variables(url: str, variables: Dict[str, Variable]) -> Set[str]:
    """Process URL variables and identify path variables."""
    path_variables = set()
    for var_name in variables:
        if '{{' + var_name + '}}' in url:
            if var_name != 'base_url':  # Skip base_url as it's handled by urljoin
                # Check if this is a path variable
                if '/{{' + var_name + '}}' in url:
                    path_variables.add(var_name)
                    variables[var_name].type = VariableType.PATH
    return path_variables


def generate_url_resolution_code() -> str:
    """Generate code for resolving URL path variables."""
    return '''
        # Resolve path variables first to avoid double slashes
        path_parts = []
        for part in formatted_url.split('/'):
            if part.startswith('{') and part.endswith('}'): 
                # This is a variable reference
                var_name = part[1:-1]  # Remove curly braces
                resolved = resolve_variable(var_name)
                if resolved:
                    path_parts.append(resolved)
                else:
                    raise ValueError(f'Failed to resolve path variable {var_name}')
            else:
                path_parts.append(part)

        # Join path parts with single slashes
        formatted_path = '/'.join(p for p in path_parts if p)

        # Construct request URL
        url = urljoin(base_url, formatted_path)
'''.strip()


def get_url_from_item(item: 'PostmanItem') -> str:
    """Extract URL from PostmanItem."""
    return item.request.url.raw if isinstance(item.request.url, str) else item.request.url.raw


def process_url(item: 'PostmanItem', variables: Dict[str, Variable], 
                url_formatter, sanitize_func) -> Tuple[str, Set[str]]:
    """Process URL and return formatted URL and path variables."""
    url = get_url_from_item(item)
    path_variables = process_url_variables(url, variables)
    formatted_url = url_formatter(url, variables, sanitize_func)
    return formatted_url, path_variables
