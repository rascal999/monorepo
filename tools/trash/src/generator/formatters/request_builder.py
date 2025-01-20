"""
Request call building utilities.
"""

import pytest
import requests
from typing import Dict, Any, List


def build_request_call(request: Dict[str, Any]) -> List[str]:
    """Build request call code lines.

    Args:
        request: Request details from Postman

    Returns:
        List of code lines
    """
    lines = [
        "",
        "    # Make request",
        "    try:",
        "        response = auth_session.request(",
        "            method=method,",
        "            url=url,",
    ]

    # Add headers if present
    if "header" in request or "headers" in request:
        lines.append("            headers=headers,")

    # Add body parameters if present
    if "body" in request:
        body = request["body"]
        if body.get("mode") == "formdata" and any(p.get("type") == "file" for p in body["formdata"]):
            lines.append("            files=files,")
            if any(p.get("type") != "file" for p in body["formdata"]):
                lines.append("            data=data,")
        else:
            lines.append("            data=data,")

    # Add verify parameter
    lines.extend([
        "            verify=tls_verify",
        "        )",
        "    except requests.exceptions.RequestException as e:",
        '        pytest.fail(f"Request failed: {str(e)}")',
        "",
        "    # Verify response",
    ])

    return lines
