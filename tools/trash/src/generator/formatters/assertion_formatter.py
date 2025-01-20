"""
Test assertion formatting utilities.
"""

import re
from typing import Dict, Any, List, Optional


def extract_status_code(assertion: str) -> Optional[str]:
    """Extract status code from assertion string.

    Args:
        assertion: Assertion string from Postman test

    Returns:
        Status code if found, None otherwise
    """
    # Try exact match first with or without response. prefix
    if any(pattern in assertion for pattern in ["response.status_code === 204", "status_code === 204"]):
        return "204"
    elif any(pattern in assertion for pattern in ["response.status_code === 200", "status_code === 200"]):
        return "200"

    # Fall back to regex for other status codes
    match = re.search(r'(?:response\.)?status_code\s*={3}\s*(\d+)', assertion)
    if match:
        return match.group(1)

    return None


def format_assertions(request: Dict[str, Any], request_details: Optional[Dict[str, Any]] = None) -> List[str]:
    """Format test assertions as Python code lines.

    Args:
        request: Request details from Postman
        request_details: Parent request details containing test assertions

    Returns:
        List of assertion lines
    """
    lines = []
    assertions_added = False

    # Check for assertions in request or parent request_details
    test_assertions = None
    if "test" in request:
        test_assertions = request["test"]
    elif request_details and "test" in request_details:
        test_assertions = request_details["test"]

    if test_assertions:
        # First pass: Look for status code assertions
        for test in test_assertions:
            if "assertion" in test:
                assertion = test["assertion"]
                if "status_code" in assertion:
                    status_code = extract_status_code(assertion)
                    if status_code:
                        lines.append(f"    assert response.status_code == {status_code}")
                        assertions_added = True
                        break

        # Second pass: Add other assertions
        for test in test_assertions:
            if "assertion" in test:
                assertion = test["assertion"]
                if "!response.text" in assertion:
                    lines.append("    assert not response.text")
                    assertions_added = True
                elif "response.json()" in assertion:
                    # Handle JSON response assertions
                    # TODO: Add more complex JSON response assertions
                    pass

    # Add default assertion if no assertions were added
    if not assertions_added:
        lines.append("    assert response.status_code == 200")

    return lines
