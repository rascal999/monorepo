"""Request-specific test generation utilities."""

from typing import Dict, List, Optional, Tuple
from .url_utils import sanitize_name
from .variable_handler import (
    Variable,
    VariableType,
    extract_variables,
    collect_variables_from_request
)

def generate_request_params(
    item: 'PostmanItem',
    url_formatter,
    sanitize_func,
    format_dict_func,
    variable_extractor=collect_variables_from_request
) -> Tuple[List[str], Dict[str, Variable], List[str]]:
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
    # Extract all variables from request
    variables = variable_extractor(item)
    fixture_params = ['session']
    fixture_names = set()
    params = []

    # Handle URL variables
    url = item.request.url.raw if isinstance(item.request.url, str) else item.request.url.raw
    url_vars = {name: var for name, var in variables.items() 
                if var.type in (VariableType.DOMAIN, VariableType.PATH)}
    
    # Format URL with proper domain/path handling
    formatted_url = url
    
    # Replace domain variables with base_url
    domain_vars = {name: var for name, var in url_vars.items() 
                  if var.type == VariableType.DOMAIN}
    if domain_vars:
        fixture_params.append('base_url')
        fixture_names.add('base_url')
        # Replace first domain variable with base_url
        first_domain = next(iter(domain_vars))
        formatted_url = formatted_url.replace(
            f"{{{{{first_domain}}}}}",
            "{base_url}"
        )
        # Remove other domain variables if any
        for var_name in list(domain_vars.keys())[1:]:
            formatted_url = formatted_url.replace(f"{{{{{var_name}}}}}", "")
    
    # Handle path variables
    path_vars = {name: var for name, var in url_vars.items() 
                if var.type == VariableType.PATH}
    for var_name in path_vars:
        fixture_name = sanitize_func(var_name.lower())
        if fixture_name not in fixture_names:
            fixture_params.append(fixture_name)
            fixture_names.add(fixture_name)
        formatted_url = formatted_url.replace(
            f"{{{{{var_name}}}}}",
            "{" + fixture_name + "}"
        )
    
    params.append(f'        url=urljoin(base_url, f"{formatted_url}"),')

    # Handle headers
    if item.request.header:
        headers = {h.key: h.value for h in item.request.header if not h.disabled}
        if headers:
            # Get header variables
            header_vars = {name: var for name, var in variables.items() 
                         if var.type == VariableType.HEADER}
            
            # Add header variables to fixtures
            for var_name in header_vars:
                fixture_name = sanitize_func(var_name.lower())
                if fixture_name not in fixture_names:
                    fixture_params.append(fixture_name)
                    fixture_names.add(fixture_name)
            
            # Format header values
            formatted_headers = {}
            for key, value in headers.items():
                formatted_value = value
                for var_name in header_vars:
                    formatted_value = formatted_value.replace(
                        f"{{{{{var_name}}}}}",
                        "{" + sanitize_func(var_name.lower()) + "}"
                    )
                formatted_headers[key] = f"f'{formatted_value}'"
            
            params.append(f"        headers={format_dict_func(formatted_headers, indent_level=3)},")

    return params, variables, fixture_params

def generate_request_body(
    item: 'PostmanItem',
    sanitize_func,
    format_dict_func,
    variable_extractor=collect_variables_from_request
) -> Tuple[Optional[str], Dict[str, Variable], List[str]]:
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
        return None, {}, []

    import json
    try:
        # Try to parse as JSON
        body_data = json.loads(item.request.body.raw)
        variables = variable_extractor(item)
        body_vars = {name: var for name, var in variables.items() 
                    if var.type == VariableType.BODY}
        fixture_params = []
        fixture_names = set()

        # Add body variables to fixtures
        for var_name in body_vars:
            fixture_name = sanitize_func(var_name.lower())
            if fixture_name not in fixture_names:
                fixture_params.append(fixture_name)
                fixture_names.add(fixture_name)

        # Format body data
        if isinstance(body_data, dict):
            formatted_data = {}
            for k, v in body_data.items():
                formatted_v = str(v)
                for var_name in body_vars:
                    formatted_v = formatted_v.replace(
                        f"{{{{{var_name}}}}}",
                        "{" + sanitize_func(var_name.lower()) + "}"
                    )
                formatted_data[k] = f"f'{formatted_v}'"
            return (
                f"        json={format_dict_func(formatted_data, indent_level=3)},",
                body_vars,
                fixture_params
            )
    except json.JSONDecodeError:
        # If not valid JSON, use raw string
        return f"        data={repr(item.request.body.raw)},", {}, []

    return None, {}, []
