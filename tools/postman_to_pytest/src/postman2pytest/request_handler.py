"""Request-specific test generation utilities."""

from typing import Dict, List, Optional, Set
from .url_utils import sanitize_name
from .variable_handler import extract_variables

def generate_request_params(
    item: 'PostmanItem',
    url_formatter,
    sanitize_func,
    format_dict_func,
    variable_extractor=extract_variables
) -> tuple[List[str], Set[str], List[str]]:
    """Generate request parameters for a test function.
    
    Args:
        item: PostmanItem containing the request
        url_formatter: Function to format URLs with variables
        sanitize_func: Function to sanitize names
        format_dict_func: Function to format dictionaries
        variable_extractor: Function to extract variables from text
        
    Returns:
        Tuple of:
        - List of parameter strings
        - Set of variables found
        - List of fixture parameter names
    """
    url = item.request.url.raw if isinstance(item.request.url, str) else item.request.url.raw
    variables = variable_extractor(url)
    fixture_params = ['session', 'base_url']
    fixture_names = ['base_url']
    params = []

    # Format URL
    formatted_url = url_formatter(url, variables)
    # Don't wrap urljoin calls in f-string
    if formatted_url.startswith('urljoin'):
        params.append(f'        {formatted_url},')
    else:
        params.append(f'        f"{formatted_url}",')

    # Add fixture parameters for URL variables
    for var in variables:
        fixture_name = sanitize_func(var.lower())
        if fixture_name not in fixture_names:
            fixture_params.append(fixture_name)
            fixture_names.append(fixture_name)

    # Add headers if present
    if item.request.header:
        headers = {h.key: h.value for h in item.request.header if not h.disabled}
        if headers:
            header_vars = set()
            for value in headers.values():
                header_vars.update(variable_extractor(value))
            
            # Add header variables to fixtures
            for var in header_vars:
                fixture_name = sanitize_func(var.lower())
                if fixture_name not in fixture_names:
                    fixture_params.append(fixture_name)
                    fixture_names.append(fixture_name)
            
            # Format header values
            formatted_headers = {}
            for key, value in headers.items():
                for var in header_vars:
                    value = value.replace(
                        f"{{{{{var}}}}}",
                        "{" + sanitize_func(var.lower()) + "}"
                    )
                formatted_headers[key] = f"f'{value}'"
            
            params.append(f"        headers={format_dict_func(formatted_headers, indent_level=3)},")

    return params, variables, fixture_params

def generate_request_body(
    item: 'PostmanItem',
    sanitize_func,
    format_dict_func,
    variable_extractor=extract_variables
) -> tuple[Optional[str], Set[str], List[str]]:
    """Generate request body parameters.
    
    Args:
        item: PostmanItem containing the request
        sanitize_func: Function to sanitize names
        format_dict_func: Function to format dictionaries
        variable_extractor: Function to extract variables from text
        
    Returns:
        Tuple of:
        - Body parameter string or None
        - Set of variables found
        - List of fixture parameter names
    """
    if not (item.request.body and item.request.body.raw):
        return None, set(), []

    import json
    try:
        # Try to parse as JSON
        body_data = json.loads(item.request.body.raw)
        body_vars = variable_extractor(item.request.body.raw)
        fixture_params = []

        # Format body data
        if isinstance(body_data, dict):
            formatted_data = {}
            for k, v in body_data.items():
                formatted_v = str(v)
                for var in body_vars:
                    formatted_v = formatted_v.replace(
                        f"{{{{{var}}}}}",
                        "{" + sanitize_func(var.lower()) + "}"
                    )
                formatted_data[k] = f"f'{formatted_v}'"
            return (
                f"        json={format_dict_func(formatted_data, indent_level=3)},",
                body_vars,
                fixture_params
            )
    except json.JSONDecodeError:
        # If not valid JSON, use raw string
        return f"        data={repr(item.request.body.raw)},", set(), []

    return None, set(), []
