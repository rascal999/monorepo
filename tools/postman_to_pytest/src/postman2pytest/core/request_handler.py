"""Request-specific test generation utilities."""

import logging
from typing import Dict, List, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)
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
    logger.debug(f"Generating request parameters for: {item.name}")
    
    # Extract all variables from request
    variables = variable_extractor(item)
    logger.debug(f"Extracted variables: {[f'{k}: {v.type.value}' for k, v in variables.items()]}")
    
    # Only need base_url and resolve_variable fixtures
    fixture_params = ['base_url', 'resolve_variable']
    params = []

    # Handle URL variables
    url = item.request.url.raw if isinstance(item.request.url, str) else item.request.url.raw
    logger.debug(f"Processing URL: {url}")
    
    # Format URL with proper domain/path handling
    formatted_url = url
    
    # Replace domain variables with base_url
    if '{base_url}' in formatted_url or '{{base_url}}' in formatted_url:
        formatted_url = formatted_url.replace('{base_url}', '').replace('{{base_url}}', '')
    
    # Handle other URL variables
    for var_name in variables:
        if '{{' + var_name + '}}' in formatted_url and var_name != 'base_url':
            formatted_url = formatted_url.replace(
                '{{' + var_name + '}}',
                "{resolve_variable('" + var_name + "')}"
            )
    
    params.append(f'        url=urljoin(base_url, f"{formatted_url}"),')

    # Handle headers
    if item.request.header:
        logger.debug("Processing request headers")
        headers = {h.key: h.value for h in item.request.header if not h.disabled}
        if headers:
            # Format header values
            formatted_headers = {}
            for key, value in headers.items():
                formatted_value = value
                for var_name in variables:
                    if '{{' + var_name + '}}' in formatted_value:
                        formatted_value = formatted_value.replace(
                            '{{' + var_name + '}}',
                            "{resolve_variable('" + var_name + "')}"
                        )
                formatted_headers[key] = f"{formatted_value}"
            
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
    logger.debug(f"Generating request body for: {item.name}")
    
    if not (item.request.body and item.request.body.raw):
        logger.debug("No request body found")
        return None, {}, []

    import json

    # Check if content is explicitly marked as JSON
    is_json = False
    if (hasattr(item.request.body, 'mode') and item.request.body.mode == 'raw' and
        hasattr(item.request.body, 'options') and 
        getattr(item.request.body.options, 'raw', {}).get('language') == 'json'):
        is_json = True
        logger.debug("Request body explicitly marked as JSON")

    # If not explicitly JSON, try to parse as JSON
    if not is_json:
        try:
            json.loads(item.request.body.raw)
            is_json = True
            logger.debug("Successfully parsed request body as JSON")
        except json.JSONDecodeError:
            logger.debug("Request body is not valid JSON")

    if is_json:
        try:
            body_data = json.loads(item.request.body.raw)
            variables = variable_extractor(item)

            def format_value(value):
                """Recursively format values, handling nested structures."""
                if isinstance(value, dict):
                    return {k: format_value(v) for k, v in value.items()}
                elif isinstance(value, list):
                    return [format_value(v) for v in value]
                else:
                    formatted_v = str(value)
                    # Handle variables in {{...}} format
                    if '{{' in formatted_v and '}}' in formatted_v:
                        # Extract variable name from {{...}}
                        var_name = formatted_v.split('{{')[1].split('}}')[0]
                        # For both $random and regular variables, use resolve_variable
                        formatted_v = f"{{resolve_variable('{var_name}')}}"
                    return formatted_v

            # Format body data
            if isinstance(body_data, dict):
                formatted_data = format_value(body_data)
                return (
                    f"        json={format_dict_func(formatted_data, indent_level=3)},",
                    variables,
                    []  # No fixture params needed since we use resolve_variable
                )
            return None, {}, []
        except json.JSONDecodeError:
            # If not valid JSON, use raw string
            logger.debug("Request body is not valid JSON, using raw string")
            return f"        data={repr(item.request.body.raw)},", {}, []

    return None, {}, []
