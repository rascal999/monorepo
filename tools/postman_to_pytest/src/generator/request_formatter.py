"""
Formatter for Postman request details into Python code.
"""

import json
from typing import Dict, Any, List


class RequestFormatter:
    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Convert request name to valid Python identifier.

        Args:
            name: Original request name

        Returns:
            Sanitized name valid for Python
        """
        # Replace non-alphanumeric with underscore
        sanitized = "".join(c if c.isalnum() else "_" for c in name).lower()

        # Always prefix with test_
        if not sanitized.startswith("test_"):
            sanitized = "test_" + sanitized

        # Collapse multiple underscores
        while "__" in sanitized:
            sanitized = sanitized.replace("__", "_")

        # Remove trailing underscore
        sanitized = sanitized.rstrip("_")

        return sanitized

    @staticmethod
    def format_request_details(request: Dict[str, Any], indent: str = "    ") -> List[str]:
        """Format request details as Python code.

        Args:
            request: Request details dict
            indent: Indentation string

        Returns:
            List of code lines
        """
        lines = []

        # Add method
        lines.append(f'{indent}method = "{request.get("method", "GET")}"')

        # Format URL
        url = request.get("url", {})
        if isinstance(url, dict):
            raw_url = url.get("raw", "")
            # Don't prepend ENV_URL for absolute URLs
            if raw_url.startswith(("http://", "https://")):
                lines.append(f'{indent}url = "{raw_url}"')
            else:
                # For relative URLs, check if ENV_URL is already in the URL
                if "{ENV_URL}" in raw_url or "{{ENV_URL}}" in raw_url:
                    # Convert Postman's double curly braces to Python f-string format
                    formatted_url = raw_url.replace("{{", "{").replace("}}", "}")
                    # Replace Postman variables with Python variables
                    formatted_url = formatted_url.replace("{ENV_URL}", "{env_url}")
                    formatted_url = formatted_url.replace("{CLIENT_ID}", "{CLIENT_ID}")
                    formatted_url = formatted_url.replace("{USER_LEGAL_OWNER}", "{USER_LEGAL_OWNER}")
                    lines.append(f'{indent}url = f"{formatted_url}"')
                else:
                    # Handle URL segments while preserving variables
                    url_segments = raw_url.split('/')
                    # Filter out empty segments but keep variable placeholders
                    filtered_segments = [seg for seg in url_segments if seg or '{' in seg]
                    # Remove any leading/trailing empty segments
                    while filtered_segments and not filtered_segments[0]:
                        filtered_segments.pop(0)
                    while filtered_segments and not filtered_segments[-1]:
                        filtered_segments.pop()
                    raw_url = '/'.join(filtered_segments)
                    # Replace Postman variables with Python variables
                    raw_url = raw_url.replace("{{CLIENT_ID}}", "{CLIENT_ID}")
                    raw_url = raw_url.replace("{{USER_LEGAL_OWNER}}", "{USER_LEGAL_OWNER}")
                    # Prepend ENV_URL since it's not in the URL
                    lines.append(f'{indent}url = f"{{env_url}}/{raw_url}"')
        else:
            # Same logic for string URLs
            if str(url).startswith(("http://", "https://")):
                lines.append(f'{indent}url = "{url}"')
            else:
                # For relative URLs, check if ENV_URL is already in the URL
                url_str = str(url)
                if "{ENV_URL}" in url_str or "{{ENV_URL}}" in url_str:
                    # Convert Postman's double curly braces to Python f-string format
                    formatted_url = url_str.replace("{{", "{").replace("}}", "}")
                    # Replace Postman variables with Python variables
                    formatted_url = formatted_url.replace("{ENV_URL}", "{env_url}")
                    formatted_url = formatted_url.replace("{CLIENT_ID}", "{CLIENT_ID}")
                    formatted_url = formatted_url.replace("{USER_LEGAL_OWNER}", "{USER_LEGAL_OWNER}")
                    lines.append(f'{indent}url = f"{formatted_url}"')
                else:
                    # Handle URL segments while preserving variables
                    url_segments = url_str.split('/')
                    # Filter out empty segments but keep variable placeholders
                    filtered_segments = [seg for seg in url_segments if seg or '{' in seg]
                    # Remove any leading/trailing empty segments
                    while filtered_segments and not filtered_segments[0]:
                        filtered_segments.pop(0)
                    while filtered_segments and not filtered_segments[-1]:
                        filtered_segments.pop()
                    url_str = '/'.join(filtered_segments)
                    # Replace Postman variables with Python variables
                    url_str = url_str.replace("{{CLIENT_ID}}", "{CLIENT_ID}")
                    url_str = url_str.replace("{{USER_LEGAL_OWNER}}", "{USER_LEGAL_OWNER}")
                    # Prepend ENV_URL since it's not in the URL
                    lines.append(f'{indent}url = f"{{env_url}}/{url_str}"')

        # Format headers
        headers = {}
        for header in request.get("header", []):
            headers[header["key"]] = header["value"]
        lines.append(f"{indent}headers = {json.dumps(headers)}")

        # Format body
        body = request.get("body", {})
        if body and isinstance(body, dict):
            if body.get("mode") == "raw":
                raw_data = body.get("raw", "")
                if isinstance(raw_data, str):
                    try:
                        # Try to parse as JSON
                        data = json.loads(raw_data)
                        lines.append(f"{indent}data = {json.dumps(data)}")
                    except json.JSONDecodeError:
                        # Use raw string if not valid JSON
                        lines.append(f"{indent}data = {repr(raw_data)}")
            elif body.get("mode") == "urlencoded":
                data = {p["key"]: p["value"] for p in body.get("urlencoded", [])}
                lines.append(f"{indent}data = {json.dumps(data)}")
            elif body.get("mode") == "formdata":
                data = {p["key"]: p["value"] for p in body.get("formdata", [])}
                lines.append(f"{indent}data = {json.dumps(data)}")
            else:
                lines.append(f"{indent}data = None")
        else:
            lines.append(f"{indent}data = None")

        return lines
