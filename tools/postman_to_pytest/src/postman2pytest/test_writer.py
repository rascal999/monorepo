"""Test content generation utilities."""

import json
from typing import Dict, List, Set

def format_dict(d: dict, indent_level: int = 2) -> str:
    """Format a dictionary as a Python literal with proper indentation."""
    lines = []
    indent = ' ' * (indent_level * 4)
    lines.append('{')
    for i, (key, value) in enumerate(d.items()):
        comma = ',' if i < len(d) - 1 else ''
        if isinstance(value, dict):
            value_str = format_dict(value, indent_level + 1)
            lines.append(f"{indent}'{key}': {value_str}{comma}")
        else:
            lines.append(f"{indent}'{key}': '{value}'{comma}")
    lines.append(' ' * ((indent_level - 1) * 4) + '}')
    return '\n'.join(lines)

def generate_imports() -> str:
    """Generate import statements for test files."""
    return "\n".join([
        "import os",
        "import pytest",
        "import requests",
        "from urllib.parse import urljoin",
        "",
        "",
        "@pytest.fixture",
        "def base_url():",
        '    """Get base URL from environment."""',
        "    url = os.getenv('ENV_URL', 'https://api.example.com')",
        "    # Ensure URL has scheme",
        "    if not url.startswith(('http://', 'https://')):",
        "        url = 'https://' + url",
        "    return url.rstrip('/')",  # Remove trailing slash for proper joining",
        "",
        "@pytest.fixture",
        "def session(base_url):",
        '    """Create a requests session with authentication."""',
        "    session = requests.Session()",
        "    # Add base URL to session for reference",
        "    session.base_url = base_url",
        "    # TODO: Add authentication setup",
        "    return session",
        "",
        "",
    ])

def generate_variable_fixtures(variables: Set[str], sanitize_func) -> str:
    """Generate pytest fixtures for Postman variables."""
    fixtures = []
    for var in variables:
        fixture_name = sanitize_func(var.lower())
        fixtures.extend([
            f"@pytest.fixture",
            f"def {fixture_name}():",
            f'    """Get {var} from environment."""',
            f"    return os.getenv('{var}', 'test-{var.lower()}')",
            "",
            "",
        ])
    return "\n".join(fixtures)

from .request_handler import generate_request_params, generate_request_body

def generate_test_function(item: 'PostmanItem', url_formatter, sanitize_func, variable_extractor) -> str:
    """Generate a pytest test function from a Postman request."""
    name = sanitize_func(item.name)
    method = item.request.method.lower()

    # Generate request parameters (URL and headers)
    params, url_vars, fixture_params = generate_request_params(
        item,
        url_formatter,
        sanitize_func,
        format_dict,
        variable_extractor
    )

    # Generate request body if present
    body_param, body_vars, body_fixtures = generate_request_body(
        item,
        sanitize_func,
        format_dict,
        variable_extractor
    )
    
    if body_param:
        params.append(body_param)

    # Combine all variables and fixtures
    all_vars = url_vars | body_vars
    fixture_params.extend(body_fixtures)

    # Join parameters with newlines and proper indentation
    request_params = "\n".join(params)

    # Generate fixtures for variables
    fixtures = generate_variable_fixtures(all_vars, sanitize_func)

    # Generate the test function
    test_lines = [
        fixtures,
        f"def test_{method}_{name}({', '.join(fixture_params)}):",
        f'    """Test {item.name}."""',
        f"    response = session.{method}(",
        request_params.rstrip(','),  # Remove trailing comma from last parameter
        "    )",
        "    assert response.status_code == 200  # TODO: Update expected status code",
        ""
    ]

    return "\n".join(test_lines)
