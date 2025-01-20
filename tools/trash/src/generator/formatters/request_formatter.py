"""
Formatter for Postman request details.
"""

import re
from typing import Dict, Any, List, Set, Optional

from .url_formatter import format_url
from .header_formatter import extract_headers, format_headers
from .body_formatter import format_body
from .request_builder import build_request_call
from .assertion_formatter import format_assertions


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

    def _get_dynamic_variables(self, request: Dict[str, Any]) -> Set[str]:
        """Get set of variables marked as dynamic in request.

        Args:
            request: Request details from Postman

        Returns:
            Set of dynamic variable names
        """
        dynamic_vars = set()
        if "uses_variables" in request:
            for var_name, var_info in request["uses_variables"].items():
                if var_info.get("type") == "dynamic":
                    dynamic_vars.add(var_name)
        return dynamic_vars

    def format_request_details(
        self,
        request: Dict[str, Any],
        dynamic_vars: Optional[Set[str]] = None,
        request_details: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Format request details as Python code lines.

        Args:
            request: Request details from Postman
            dynamic_vars: Set of variable names marked as dynamic
            request_details: Parent request details containing test assertions

        Returns:
            List of Python code lines
        """
        lines = []

        # Get dynamic variables from request and passed set
        request_dynamic_vars = set()
        if dynamic_vars:
            request_dynamic_vars.update(dynamic_vars)
        request_dynamic_vars.update(self._get_dynamic_variables(request))

        # Method
        lines.append(f'    method = "{request["method"]}"')

        # URL
        url = request["url"]
        lines.append(f"    url = {format_url(url, request_dynamic_vars)}")

        # Headers
        headers = extract_headers(request, request_dynamic_vars)
        if headers:
            lines.append(f"    headers = {format_headers(headers)}")
        else:
            # Add OAuth header if no other headers
            lines.append('    headers = {"Authorization": "Bearer {auth_session.token[\'access_token\']}"}')

        # Body
        if "body" in request:
            lines.extend(format_body(request["body"]))

        # Request call
        lines.extend(build_request_call(request))

        # Assertions
        lines.extend(format_assertions(request, request_details))

        return lines
