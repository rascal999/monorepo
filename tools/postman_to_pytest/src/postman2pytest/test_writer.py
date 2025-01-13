"""Test content generation utilities."""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from .variable_handler import Variable, VariableType

def parse_markdown_link(text: str) -> str:
    """Extract the text part from a Markdown link.
    
    Args:
        text: Text that may contain a Markdown link [text](url)
        
    Returns:
        The text part if it's a Markdown link, otherwise the original text
    """
    if not text:
        return "No description provided."
        
    # Match Markdown link pattern [text](url)
    match = re.match(r'\[(.*?)\]\((.*?)\)', text.strip())
    if match:
        return match.group(1)  # Return just the text part
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
        else:
            lines.append(f"{indent}'{key}': '{value}'{comma}")
    lines.append(' ' * ((indent_level - 1) * 4) + '}')
    return '\n'.join(lines)

def generate_imports() -> str:
    """Generate import statements for test files."""
    return "\n".join([
        "import os",
        "import json",
        "import logging",
        "from pathlib import Path",
        "import pytest",
        "import requests",
        "from urllib.parse import urljoin",
        "from auth import AuthHandler",  # Import from local auth.py",
        "",
        "# Configure logging",
        "logger = logging.getLogger(__name__)",
        "logger.setLevel(logging.INFO)",
        "",
        "",
    ])

def load_variable_registry() -> Dict[str, dict]:
    """Load variable registry from JSON file."""
    try:
        # First try the generated_tests directory
        registry_path = Path(__file__).parent.parent.parent / 'generated_tests' / 'variable_registry.json'
        if not registry_path.exists():
            # Fall back to project root
            registry_path = Path(__file__).parent.parent.parent / 'variable_registry.json'
        
        if registry_path.exists():
            registry = json.loads(registry_path.read_text())
            variables = registry.get('variables', {})
            # Convert keys to uppercase for consistent matching
            return {k.upper(): v for k, v in variables.items()}
    except Exception as e:
        print(f"Error loading variable registry: {e}")
    return {}

def generate_variable_fixtures(variables: Dict[str, Variable], used_vars: Set[str], sanitize_func) -> str:
    """Generate pytest fixtures for Postman variables."""
    fixtures = []
    
    # Only add registry fixture if we have variables that need it
    if used_vars:
        fixtures.extend([
            "@pytest.fixture",
            "def variable_registry():",
            '    """Load and provide variable registry."""',
            "    try:",
            "        # Find generated_tests directory by looking for conftest.py",
            "        current = Path(__file__).parent",
            "        while current.name != 'generated_tests' and current.parent != current:",
            "            current = current.parent",
            "        if current.name == 'generated_tests':",
            "            registry_path = current / 'variable_registry.json'",
            "        else:",
            "            registry_path = Path(__file__).parent / 'variable_registry.json'",
            "        if registry_path.exists():",
            "            return json.loads(registry_path.read_text()).get('variables', {})",
            "    except Exception:",
            "        pass",
            "    return {}",
            "",
            "",
        ])
    
    # Add fixtures only for variables used in the test
    for var_name in used_vars:
        var = variables.get(var_name)
        if not var:
            continue
            
        # Skip domain variables as they use base_url fixture
        if var.type == VariableType.DOMAIN:
            continue
            
        # Skip auth variables as they use auth fixtures
        if var.type == VariableType.AUTH:
            continue
            
        fixture_name = sanitize_func(var_name, preserve_case=True)  # Keep original case
        description = var.description or f"Get {var_name} from environment"
        
        fixtures.extend([
            f"@pytest.fixture",
            f"def {fixture_name}(variable_registry):",
            f'    """{description}"""',
            f"    # Try both original case and uppercase",
            f"    var_info = next((v for k, v in variable_registry.items() if k.upper() == '{var_name.upper()}'), {{}})",
            f"    source = var_info.get('source')",
            f"    if source == 'value':",
            f"        return os.getenv('{var_name}', var_info.get('value', 'test-{var_name}'))",
            f"    elif source == 'collection':",
            f"        return os.getenv('{var_name}', var_info.get('value', 'test-{var_name}'))",
            f"    else:  # fixture or response",
            f"        fixture_name = var_info.get('fixture', 'test-{var_name}')",
            f"        return os.getenv('{var_name}', fixture_name)",
            "",
            "",
        ])
    return "\n".join(fixtures)

from .request_handler import generate_request_params, generate_request_body

def construct_url(url: str, variables: Dict[str, Variable], sanitize_func) -> Tuple[str, List[str]]:
    """Construct URL with proper handling of domain and path variables."""
    fixture_params = []
    result_url = url
    
    # Remove any base_url prefix if present
    if result_url.startswith('{base_url}'):
        result_url = result_url[len('{base_url}'):]
    
    # Replace domain variables with base_url
    domain_vars = {name: var for name, var in variables.items() 
                  if var.type == VariableType.DOMAIN}
    if domain_vars:
        # Use base_url fixture
        fixture_params.append('base_url')
        # Replace first domain variable with base_url
        first_domain = next(iter(domain_vars))
        result_url = result_url.replace(
            f"{{{{{first_domain}}}}}",
            ""  # Remove domain var since we'll use base_url
        )
        # Remove other domain variables if any
        for var_name in list(domain_vars.keys())[1:]:
            result_url = result_url.replace(f"{{{{{var_name}}}}}", "")
            
    # Handle path variables
    path_vars = {name: var for name, var in variables.items() 
                if var.type == VariableType.PATH}
    for var_name, var in path_vars.items():
        # Use fixture name from registry if available
        fixture_name = var.fixture if hasattr(var, 'fixture') else sanitize_func(var_name, preserve_case=True)  # Keep original case
        fixture_params.append(fixture_name)
        result_url = result_url.replace(
            f"{{{{{var_name}}}}}",
            "{" + fixture_name + "}"
        )
        
    return result_url, fixture_params

def generate_test_function(item: 'PostmanItem', url_formatter, sanitize_func, variable_extractor, auth_config=None) -> str:
    """Generate a pytest test function from a Postman request."""
    name = sanitize_func(item.name)  # Don't preserve case for test function names
    method = item.request.method.lower()

    # Extract and classify variables
    variables = variable_extractor(item)
    
    # Track which variables are actually used
    used_vars = set()
    
    # Generate request parameters (URL and headers)
    url = item.request.url.raw if isinstance(item.request.url, str) else item.request.url.raw
    formatted_url, url_fixtures = construct_url(url, variables, sanitize_func)
    
    # Add variables used in URL
    for fixture in url_fixtures:
        # Keep original case from variables dict
        var_name = next((name for name in variables if name.upper() == fixture.upper()), fixture)
        if var_name in variables:
            used_vars.add(var_name)
    
    params = [f"        url=urljoin(base_url, f'{formatted_url}'),"]
    fixture_params = url_fixtures

    # Generate request body if present
    body_param, body_vars, body_fixtures = generate_request_body(
        item,
        sanitize_func,
        format_dict,
        variable_extractor
    )
    
    if body_param:
        params.append(body_param)
        # Add variables used in body
        for fixture in body_fixtures:
            # Keep original case from variables dict
            var_name = next((name for name in variables if name.upper() == fixture.upper()), fixture)
            if var_name in variables:
                used_vars.add(var_name)

    # Add auth-related fixtures if auth_config is present
    auth_fixtures = []
    if auth_config and auth_config.type == "oauth":
        auth_fixtures.extend([
            "@pytest.fixture(scope='function')",
            "def oauth_token(auth_handler):",
            '    """Get OAuth token for request."""',
            "    token = auth_handler._get_oauth_token()",
            "    assert token, 'Failed to obtain OAuth token'",
            "    return token",
            "",
            ""
        ])
        # Add Authorization header to request
        params.append("        headers={'Authorization': f'Bearer {oauth_token}'},")

    # Add auth to fixture params
    fixture_params.extend(body_fixtures)
    if auth_config and auth_config.type == "oauth":
        if 'oauth_token' not in fixture_params:
            fixture_params.append('oauth_token')

    # Join parameters with newlines and proper indentation
    request_params = "\n".join(params)

    # Generate fixtures only for used variables
    var_fixtures = generate_variable_fixtures(variables, used_vars, sanitize_func)

    # Generate the test function
    test_lines = [
        var_fixtures,
        "\n".join(auth_fixtures) if auth_fixtures else "",
        f"def test_{method}_{name}({', '.join(fixture_params)}):",
        f'    """Test {item.name}.',
        f"",
        f"    {parse_markdown_link(item.request.description) if hasattr(item.request, 'description') and item.request.description else 'No description provided.'}",
        f'    """',
        f"    # Get SSL verification setting",
        f"    verify = os.getenv('TLS_VERIFY', 'true').lower() == 'true'",
        f"    cert_path = os.getenv('CERT_PATH')",
        f"    verify_arg = cert_path if cert_path else verify",
        f"",
        f"    # Create session with SSL verification",
        f"    with requests.Session() as session:",
        f"        session.verify = verify_arg",
        f"",
        f"        response = session.{method}(",
        request_params.rstrip(','),  # Remove trailing comma from last parameter
        "        )",
        "        assert response.status_code == 200  # TODO: Update expected status code",
        ""
    ]

    return "\n".join(test_lines)
