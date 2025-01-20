"""
Body formatting utilities.
"""

import re
from typing import Dict, Any, List


def format_raw_body(raw_body: str) -> str:
    """Format raw request body.

    Args:
        raw_body: Raw body content

    Returns:
        Formatted body string
    """
    # If body contains variables, format them properly
    if "{{" in raw_body and "}}" in raw_body:
        # Replace {{variable}} with variable name for Python dict
        formatted_body = re.sub(r'"\{\{(.+?)\}\}"', r"\1", raw_body)
        return formatted_body
    # Use raw body as is
    return raw_body


def format_form_data(form_data_params: List[Dict[str, Any]]) -> tuple[Dict[str, str], Dict[str, str]]:
    """Format form data parameters.

    Args:
        form_data_params: List of form data parameters

    Returns:
        Tuple of (form_data, files_data) dictionaries
    """
    form_data = {}
    files_data = {}

    for param in form_data_params:
        if param.get("type") == "file":
            # Handle file upload
            src = param["src"]
            if src.startswith("{{") and src.endswith("}}"):
                # Variable contains file path
                var_name = src[2:-2]  # Remove {{ }}
                files_data[param["key"]] = f"open({var_name}, 'rb')"
            else:
                # Static file path
                files_data[param["key"]] = f"open('{src}', 'rb')"
        else:
            # Handle regular form fields
            value = param["value"]
            if value.startswith("{{") and value.endswith("}}"):
                # Variable substitution
                var_name = value[2:-2]  # Remove {{ }}
                form_data[param["key"]] = var_name
            else:
                form_data[param["key"]] = f"'{value}'"

    return form_data, files_data


def format_urlencoded(urlencoded_params: List[Dict[str, str]]) -> Dict[str, str]:
    """Format URL-encoded parameters.

    Args:
        urlencoded_params: List of URL-encoded parameters

    Returns:
        Dictionary of formatted parameters
    """
    url_data = {}
    for param in urlencoded_params:
        value = param["value"]
        if value.startswith("{{") and value.endswith("}}"):
            # Variable substitution
            var_name = value[2:-2]  # Remove {{ }}
            url_data[param["key"]] = var_name
        else:
            url_data[param["key"]] = f"'{value}'"
    return url_data


def format_body(body: Dict[str, Any]) -> List[str]:
    """Format request body as Python code lines.

    Args:
        body: Request body details

    Returns:
        List of code lines
    """
    lines = []
    
    if body.get("mode") == "raw":
        # Handle raw JSON body
        formatted_body = format_raw_body(body["raw"])
        lines.append(f"    data = {formatted_body}")
    
    elif body.get("mode") == "formdata":
        form_data, files_data = format_form_data(body["formdata"])
        
        if files_data:
            file_items = [f"'{k}': {v}" for k, v in files_data.items()]
            lines.append(f"    files = {{{', '.join(file_items)}}}")
        if form_data:
            form_items = [f"'{k}': {v}" for k, v in form_data.items()]
            lines.append(f"    data = {{{', '.join(form_items)}}}")
    
    elif body.get("mode") == "urlencoded":
        url_data = format_urlencoded(body["urlencoded"])
        url_items = [f"'{k}': {v}" for k, v in url_data.items()]
        lines.append(f"    data = {{{', '.join(url_items)}}}")

    return lines
