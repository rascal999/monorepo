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
        "import pytest  # pytest-dependency plugin will be auto-loaded",
        "import requests",
        "from urllib.parse import urljoin",
        "from auth import AuthHandler",
    ]

def generate_test_function(item: 'PostmanItem', url_formatter, sanitize_func, variable_extractor, variable_registry: dict, auth_config=None, version: str = None, client_id: str = None) -> str:
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
        "logger.setLevel(logging.DEBUG)",
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

    # Add dependency markers
    test_lines.append("@pytest.mark.dependency()")  # Base marker for this test

    # Add dependencies for variables that come from responses
    needed_deps = set()
    for var_name in variables:
        if var_name in variable_registry.get('variables', {}):
            var_data = variable_registry['variables'][var_name]
            if var_data.get('source') == 'fixture' and var_data.get('response_pattern'):
                response_pattern = var_data['response_pattern']
                if 'source_test' in response_pattern:
                    needed_deps.add(response_pattern['source_test'])
    
    # Add dependency markers in sorted order
    for dep in sorted(needed_deps):
        # Extract module path from source_file in variable registry
        var_data = None
        for data in variable_registry.get('variables', {}).values():
            if data and isinstance(data, dict):
                response_pattern = data.get('response_pattern', {})
                if response_pattern and isinstance(response_pattern, dict):
                    if response_pattern.get('source_test') == dep:
                        var_data = data
                        break
        
        source_file = ''
        if var_data and isinstance(var_data, dict):
            response_pattern = var_data.get('response_pattern', {})
            if response_pattern and isinstance(response_pattern, dict):
                source_file = response_pattern.get('source_file', '')
        if source_file:
            # Convert path to module notation and prepend generated_tests
            module_path = f"generated_tests"
            if version:
                module_path += f".{version}"
            if client_id:
                module_path += f".{client_id}"
            module_path += f".{source_file.replace('/', '.').replace('.py', '')}"
            test_lines.append(f"@pytest.mark.dependency(depends=['{module_path}::{dep}'])")
        else:
            test_lines.append(f"@pytest.mark.dependency(depends=['{dep}'])")

    test_lines.extend([
        f"def test_{method}_{name}({', '.join(fixture_params)}):",
        f'    """Test {item.name}.',
        "",
        f"    {parse_markdown_link(item.request.description) if hasattr(item.request, 'description') and item.request.description else 'No description provided.'}",
        '    """',
        "    # Get request configuration",
        "    verify = os.getenv('TLS_VERIFY', 'true').lower() == 'true'",
        "    cert_path = os.getenv('CERT_PATH')",
        "    verify_arg = cert_path if cert_path else verify",
        "",
        "    # Get proxy settings",
        "    http_proxy = os.getenv('HTTP_PROXY')",
        "    https_proxy = os.getenv('HTTPS_PROXY')",
        "    proxies = {",
        "        'http': http_proxy,",
        "        'https': https_proxy",
        "    } if http_proxy or https_proxy else None",
        "    logger.debug(f'Using proxy settings: {proxies}')",
        "",
        "    # Create session with SSL verification and proxy",
        "    with requests.Session() as session:",
        "        session.verify = verify_arg",
        "        logger.debug(f'SSL verification setting: verify_arg={verify_arg}, cert_path={cert_path}')",
        "",
        "        if proxies:",
        "            session.proxies = proxies",
        "            logger.debug('Applied proxy settings to session')",
        "",
        "        # Construct request URL",
        f"        url = urljoin(base_url, f'{formatted_url}')",
    ])

    # Extract headers from Postman request
    headers = {}
    if hasattr(item.request, 'header') and item.request.header:
        for header in item.request.header:
            headers[header.key] = header.value

    # Add Content-Type for JSON if not present
    if item.request.body and item.request.body.raw:
        try:
            json.loads(item.request.body.raw)  # Test if body is valid JSON
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
        except json.JSONDecodeError:
            pass  # Not JSON data, don't add Content-Type

    # Generate headers dictionary string
    header_lines = []
    for key, value in headers.items():
        header_lines.append(f"            '{key}': '{value}',")
    if auth_config and auth_config.type == "oauth":
        header_lines.append("            'Authorization': f'Bearer {oauth_token}',")

    # Add headers initialization to test
    if header_lines:
        test_lines.extend([
            "        # Initialize request headers",
            "        headers = {",
            *header_lines,
            "        }",
            "",
        ])
    else:
        test_lines.extend([
            "        # Initialize request headers",
            "        headers = {}",
            "        if 'oauth_token' in locals():",
            "            headers['Authorization'] = f'Bearer {oauth_token}'",
            "",
        ])

    # Add request body preparation if present
    if item.request.body and item.request.body.raw:
        # Check request mode
        mode = item.request.body.mode if hasattr(item.request.body, 'mode') else 'raw'
        
        if mode == 'urlencoded':
            # Handle form data
            form_data = {}
            pairs = item.request.body.raw.split('&')
            for pair in pairs:
                key, value = pair.split('=', 1)
                if key in form_data:
                    if not isinstance(form_data[key], list):
                        form_data[key] = [form_data[key]]
                    form_data[key].append(value)
                else:
                    form_data[key] = value

            # Add form data preparation
            test_lines.extend([
                "        # Prepare form data",
                "        request_body = {",
                *[f"            '{k}': '{v}'," for k, v in form_data.items()],
                "        }",
                "",
            ])
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        else:
            # Handle raw/JSON data
            test_lines.extend([
                "        # Prepare request body",
                "        request_body = json.loads('''",
                f"{item.request.body.raw}",
                "''')",
                "",
            ])
            headers['Content-Type'] = 'application/json'

    test_lines.extend([
        f"        method = '{method}'  # Store HTTP method",
        "",
        "        logger.debug(f'Making {method.upper()} request to URL: {url}')",
        "        logger.debug(f'Request headers: {headers}')",
        "",
        "        # Make request",
        "        response = getattr(session, method)(",
        "            url=url,",
        "            headers=headers,",
    ])

    # Add body to request if present
    if item.request.body and item.request.body.raw:
        test_lines.append("            json=request_body," if "json=request_body" in "\n".join(test_lines) else "            data=request_body,")

    # Add response assertion and logging
    test_lines.extend([
        "        )",
        "        logger.debug(f'Response status code: {response.status_code}')",
        "        logger.debug(f'Response headers: {dict(response.headers)}')",
        "",
        "        assert response.status_code == 200  # TODO: Update expected status code",
        "",
        "        # Log response for variable extraction",
        "        try:",
        "            response_data = response.json()",
        "            logger.debug(f'Response data for variable extraction: {json.dumps(response_data, indent=2)}')",
        "            logger.debug(f'Response logged to {Path(__file__).resolve().parent.parent / \"test_responses.log\"}')",
        "        except json.JSONDecodeError as e:",
        "            logger.error(f'Failed to parse response as JSON: {e}')",
        "            logger.debug(f'Raw response content: {response.text}')",
        "        except Exception as e:",
        "            logger.error(f'Unexpected error processing response: {e}')",
        "",
    ])

    return "\n".join(test_lines)
