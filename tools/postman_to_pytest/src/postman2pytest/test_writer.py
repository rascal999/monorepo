"""Test content generation utilities."""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Configure logging
logger = logging.getLogger(__name__)
from .variable_handler import Variable, VariableType

def parse_markdown_link(text: str) -> str:
    """Extract the text part from a Markdown link."""
    if not text:
        return "No description provided."
    match = re.match(r'\[(.*?)\]\((.*?)\)', text.strip())
    if match:
        return match.group(1)
    return text

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
        elif isinstance(value, str):
            if '{' in value and '}' in value:
                lines.append(f"{indent}'{key}': f'{value}'{comma}")
            else:
                lines.append(f"{indent}'{key}': '{value}'{comma}")
        else:
            lines.append(f"{indent}'{key}': '{value}'{comma}")
    lines.append(' ' * ((indent_level - 1) * 4) + '}')
    return '\n'.join(lines)

def generate_imports() -> List[str]:
    """Generate import statements for test files."""
    return [
        "import os",
        "import json",
        "import logging",
        "from pathlib import Path",
        "import pytest",
        "import requests",
        "from urllib.parse import urljoin",
        "from auth import AuthHandler",
    ]

def generate_test_function(item: 'PostmanItem', url_formatter, sanitize_func, variable_extractor, auth_config=None) -> str:
    """Generate a pytest test function from a Postman request."""
    name = sanitize_func(item.name)
    method = item.request.method.lower()

    # Extract variables
    variables = variable_extractor(item)
    logger.debug(f"Extracted variables: {[f'{k}: {v.type.value}' for k, v in variables.items()]}")
    
    # Generate request parameters
    url = item.request.url.raw if isinstance(item.request.url, str) else item.request.url.raw
    
    # Process URL variables
    formatted_url = url
    for var_name in variables:
        if '{{' + var_name + '}}' in formatted_url:
            if var_name != 'base_url':  # Skip base_url as it's handled by urljoin
                formatted_url = formatted_url.replace(
                    '{{' + var_name + '}}',
                    "{resolve_variable('" + var_name + "')}"
                )
    
    # Remove base_url prefix if present
    formatted_url = formatted_url.replace('{base_url}', '').replace('{{base_url}}', '')
    
    # Add required fixtures
    fixture_params = ['base_url', 'resolve_variable']
    
    # Add auth token if needed
    if auth_config and auth_config.type == "oauth":
        fixture_params.append('oauth_token')

    # Generate test function
    test_lines = [
        "\n".join(generate_imports()),
        "",
        "# Configure logging",
        "logger = logging.getLogger(__name__)",
        "logger.setLevel(logging.INFO)",
        "",
    ]

    # Add auth fixture if needed
    if auth_config and auth_config.type == "oauth":
        test_lines.extend([
            "@pytest.fixture(scope='function')",
            "def oauth_token(auth_handler):",
            '    """Get OAuth token for request."""',
            "    token = auth_handler._get_oauth_token()",
            "    assert token, 'Failed to obtain OAuth token'",
            "    return token",
            "",
            "",
        ])

    # Generate test function
    test_lines.extend([
        f"def test_{method}_{name}({', '.join(fixture_params)}):",
        f'    """Test {item.name}.',
        "",
        f"    {parse_markdown_link(item.request.description) if hasattr(item.request, 'description') and item.request.description else 'No description provided.'}",
        '    """',
        "    # Get SSL verification setting",
        "    verify = os.getenv('TLS_VERIFY', 'true').lower() == 'true'",
        "    cert_path = os.getenv('CERT_PATH')",
        "    verify_arg = cert_path if cert_path else verify",
        "",
        "    # Create session with SSL verification",
        "    with requests.Session() as session:",
        "        session.verify = verify_arg",
        "",
        "        response = session.post(",
        f"            url=urljoin(base_url, f'{formatted_url}'),",
    ])

    # Add request body if present
    if item.request.body and item.request.body.raw:
        try:
            body_data = json.loads(item.request.body.raw)
            test_lines.append("            json={")
            for key, value in body_data.items():
                if isinstance(value, dict):
                    test_lines.append(f"                '{key}': {{")
                    for k, v in value.items():
                        if isinstance(v, str) and ('{{' in v or '$random' in v):
                            var_name = v.strip('{}')
                            test_lines.append(f"                    '{k}': resolve_variable('{var_name}'),")
                        else:
                            test_lines.append(f"                    '{k}': '{v}',")
                    test_lines.append("                },")
                elif isinstance(value, str) and ('{{' in value or '$random' in value):
                    var_name = value.strip('{}')
                    test_lines.append(f"                '{key}': resolve_variable('{var_name}'),")
                else:
                    test_lines.append(f"                '{key}': '{value}',")
            test_lines.append("            },")
        except json.JSONDecodeError:
            test_lines.append(f"            data='{item.request.body.raw}',")

    # Add auth header if needed
    if auth_config and auth_config.type == "oauth":
        test_lines.append("            headers={'Authorization': f'Bearer {oauth_token}'},")

    # Add response assertion
    test_lines.extend([
        "        )",
        "        assert response.status_code == 200  # TODO: Update expected status code",
        "",
    ])

    return "\n".join(test_lines)
