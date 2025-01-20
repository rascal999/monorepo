"""URL formatting utilities."""

import re
from typing import Dict, Any, Union, Set


def format_url(url: Union[str, Dict[str, Any]], dynamic_vars: Set[str]) -> str:
    """Format URL for use in test code.

    Args:
        url: Raw URL from request (string or dictionary)
        dynamic_vars: Set of variables marked as dynamic

    Returns:
        Formatted URL string
    """
    # Extract URL components from dictionary if needed
    if isinstance(url, dict):
        base_url = url["raw"]
        # Handle query parameters if present
        if "query" in url:
            query_parts = []
            for param in url["query"]:
                key = param["key"]
                value = param["value"]
                # Replace {{var}} with {var} for dynamic variables
                if value.startswith("{{") and value.endswith("}}"):
                    var_name = value[2:-2]  # Keep original case
                    if var_name in dynamic_vars:
                        value = "{" + var_name + "}"
                    else:
                        value = "{" + var_name + "}"  # Always use variable reference
                query_parts.append(f"{key}={value}")
            if query_parts:
                base_url = base_url.split("?")[0]  # Remove existing query string
                base_url = f"{base_url}?{'&'.join(query_parts)}"
    else:
        base_url = url

    # Handle absolute URLs
    if base_url.startswith(("http://", "https://")):
        # Keep absolute URLs as-is
        return f'"{base_url}"'

    # Remove leading slash if present
    if base_url.startswith("/"):
        base_url = base_url[1:]

    # Remove any double slashes
    base_url = re.sub(r"//+", "/", base_url)

    # Replace {{ENV_URL}} with env_url if present
    base_url = re.sub(r"\{\{ENV_URL\}\}/", "", base_url)

    # Replace all {{var}} with {var} in URL
    base_url = re.sub(r'\{\{([^}]+)\}\}', lambda m: '{' + m.group(1) + '}', base_url)

    return f'f"{{env_url}}/{base_url}"'
