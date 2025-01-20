"""Header formatting utilities."""

import logging
from typing import Dict, List, Union

logger = logging.getLogger(__name__)


def format_headers(headers: Dict[str, str]) -> str:
    """Format headers for use in test code.

    Args:
        headers: Dictionary of header key-value pairs

    Returns:
        Formatted headers string
    """
    logger.debug(f"Input headers: {headers}")
    header_items = []
    for key, value in headers.items():
        logger.debug(f"Processing header - key: {key}, value: {value}")
        if key == "Authorization" and value.startswith("Bearer {{") and value.endswith("}}"):
            # Extract just the variable name from Bearer token
            var_start = value.find("{{") + 2
            var_end = value.find("}}")
            token_var = value[var_start:var_end]
            logger.debug(f"Bearer token - extracted variable: '{token_var}'")
            token_var = token_var.strip()
            logger.debug(f"Bearer token - cleaned variable: '{token_var}'")
            # Format Bearer token with f-string - exactly as test expects
            formatted = f'"{key}": f"Bearer {{{token_var}}}"'
            logger.debug(f"Bearer token - final format: {formatted}")
            header_items.append(formatted)
        elif value == "application/json":
            header_items.append(f'"{key}": "application/json"')
        elif value.startswith("{{") and value.endswith("}}"):
            var_name = value[2:-2].strip()
            header_items.append(f'"{key}": {var_name}')
        else:
            header_items.append(f'"{key}": "{value}"')
    
    result = "{" + ", ".join(header_items) + "}"
    logger.debug(f"Final headers: {result}")
    return result


def extract_headers(request: Dict[str, Union[str, Dict]], dynamic_vars: set) -> Dict[str, str]:
    """Extract and format headers from request.

    Args:
        request: Request details from Postman
        dynamic_vars: Set of dynamic variable names

    Returns:
        Dictionary of formatted headers
    """
    logger.debug(f"Extracting headers from request: {request}")
    headers = {}

    if "header" in request or "headers" in request:
        header_list = request.get("header", []) or request.get("headers", [])
        logger.debug(f"Found header list: {header_list}")
        for h in header_list:
            key = h["key"]
            value = h["value"]
            logger.debug(f"Extracted header - key: {key}, value: {value}")
            headers[key] = value

    logger.debug(f"Extracted headers: {headers}")
    return headers
