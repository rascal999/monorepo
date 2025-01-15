"""
Formatter for Postman request details.
"""

import re
from typing import Dict, Any, List, Union


class RequestFormatter:
    """Formats Postman request details as Python code."""

    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for use as Python identifier.

        Args:
            name: Name to sanitize

        Returns:
            Sanitized name
        """
        # Convert to lowercase and replace spaces with underscores
        sanitized = name.lower().replace(" ", "_")
        # Remove any non-alphanumeric characters
        sanitized = re.sub(r"[^a-z0-9_]", "", sanitized)
        # Prefix with test_ if not already
        if not sanitized.startswith("test_"):
            sanitized = f"test_{sanitized}"
        return sanitized

    def _format_url(self, url: Union[str, Dict[str, Any]]) -> str:
        """Format URL for use in test code.

        Args:
            url: Raw URL from request (string or dictionary)

        Returns:
            Formatted URL string
        """
        # Extract raw URL from dictionary if needed
        if isinstance(url, dict):
            url = url["raw"]

        # Handle absolute URLs
        if url.startswith(("http://", "https://")):
            # Keep absolute URLs as-is
            return f'"{url}"'

        # Remove leading slash if present
        if url.startswith("/"):
            url = url[1:]

        # Remove any double slashes
        url = re.sub(r"//+", "/", url)

        # Replace {{ENV_URL}} with env_url if present
        url = re.sub(r"\{\{ENV_URL\}\}/", "", url)

        # Handle environment variables and other variables differently
        # Convert environment variables to direct references
        url = re.sub(r'\{\{(CLIENT_ID|USER_LEGAL_OWNER|ENV_URL)\}\}', r'{\1}', url)

        return f'f"{{env_url}}/{url}"'

    def format_request_details(self, request: Dict[str, Any]) -> List[str]:
        """Format request details as Python code lines.

        Args:
            request: Request details from Postman

        Returns:
            List of Python code lines
        """
        lines = []

        # Method
        lines.append(f'    method = "{request["method"]}"')

        # URL
        url = request["url"]
        lines.append(f"    url = {self._format_url(url)}")

        # Headers
        headers = {}
        has_auth_header = False
        if "header" in request or "headers" in request:
            header_list = request.get("header", []) or request.get("headers", [])
            for h in header_list:
                # Keep original value with {{var}} placeholders
                headers[h["key"]] = h["value"]
                if h["key"].lower() == "authorization":
                    has_auth_header = True
        
        # Add OAuth Authorization header only if no auth header exists
        if not has_auth_header:
            headers["Authorization"] = "Bearer {auth_session.token['access_token']}"
        
        if headers:
            # Format headers preserving variable placeholders
            header_str = "{"
            for key, value in headers.items():
                # Keep {{var}} placeholders intact
                header_str += f'"{key}": "{value}", '
            header_str = header_str.rstrip(", ") + "}"
            lines.append(f"    headers = {header_str}")

        # Body
        if "body" in request:
            body = request["body"]
            if body.get("mode") == "raw":
                lines.append(f'    data = {body["raw"]}')
            elif body.get("mode") == "formdata":
                form_data = {}
                for param in body["formdata"]:
                    form_data[param["key"]] = param["value"]
                lines.append(f"    data = {form_data}")
            elif body.get("mode") == "urlencoded":
                url_data = {}
                for param in body["urlencoded"]:
                    url_data[param["key"]] = param["value"]
                lines.append(f"    data = {url_data}")

        # Request call
        lines.extend([
            "",
            "    # Make request",
            "    response = auth_session.request(",
            "        method=method,",
            "        url=url,",
        ])

        if "header" in request or "headers" in request:
            lines.append("        headers=headers,")
        if "body" in request:
            lines.append("        data=data,")

        lines.extend([
            "        verify=tls_verify",
            "    )",
            "",
            "    # Verify response",
            "    assert response.status_code == 200",
        ])

        return lines
