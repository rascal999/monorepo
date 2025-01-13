"""Test function building utilities."""

import json
import logging
import re
from typing import Dict, List, Optional, Set
from pathlib import Path

from .test_imports import (
    generate_imports,
    generate_oauth_fixture,
    generate_logging_setup
)
from .test_request_builder import (
    build_headers,
    prepare_request_body,
    generate_request_setup,
    generate_response_handling,
    generate_json_processor
)
from .test_url_handler import generate_url_resolution_code
from ..core.variable_types import Variable

logger = logging.getLogger(__name__)


def get_required_fixtures(auth_config: Optional[dict], deps: Optional[Set[str]], 
                         has_patterns: bool = False) -> List[str]:
    """Get list of required fixture parameters.
    
    Args:
        auth_config: Optional authentication configuration
        deps: Optional set of test dependencies
        has_patterns: Whether the test has response patterns to extract
        
    Returns:
        List of required fixture parameter names
    """
    fixture_params = ['base_url', 'resolve_variable']
    if auth_config and auth_config.type == "oauth":
        fixture_params.append('oauth_token')
    if has_patterns:
        fixture_params.append('store_response_data')
    if deps:
        fixture_params.append('get_response_data')
    return fixture_params


def generate_function_definition(name: str, method: str, fixture_params: List[str], 
                               description: Optional[str] = None) -> List[str]:
    """Generate test function definition."""
    return [
        f"def test_{method}_{name}({', '.join(fixture_params)}):",
        f'    """Test {name}.',
        "",
        f"    {description if description else 'No description provided.'}",
        '    """',
    ]


def generate_header_setup(item: 'PostmanItem', auth_config: Optional[dict] = None) -> List[str]:
    """Generate header setup code."""
    headers = build_headers(item, auth_config)
    if headers:
        header_lines = []
        for key, value in headers.items():
            header_lines.append(f"            '{key}': '{value}',")
        if auth_config and auth_config.type == "oauth":
            header_lines.append("            'Authorization': f'Bearer {oauth_token}',")

        return [
            "        # Initialize request headers",
            "        headers = {",
            *header_lines,
            "        }",
            "",
        ]
    else:
        return [
            "        # Initialize request headers",
            "        headers = {}",
            "        if 'oauth_token' in locals():",
            "            headers['Authorization'] = f'Bearer {oauth_token}'",
            "",
        ]


def generate_body_setup(item: 'PostmanItem') -> List[str]:
    """Generate request body setup code."""
    if not (item.request.body and isinstance(item.request.body, dict) and 'raw' in item.request.body):
        return []

    content_type, body_data = prepare_request_body(item)
    if content_type == 'application/json':
        # Fix common JSON formatting issues
        raw_json = item.request.body['raw']
        # Replace single quotes with double quotes
        raw_json = raw_json.replace("'", '"')
        # Add quotes around unquoted property names
        raw_json = re.sub(r'(\s*)(\w+)(\s*):([^:])', r'\1"\2"\3:\4', raw_json)
        
        return [
            "        # Load raw JSON body",
            "        raw_body = json.loads('''",
            f"{raw_json}",
            "''')",
            "",
            generate_json_processor(),
            "",
            "        # Prepare request body with resolved variables",
            "        request_body = process_json_value(raw_body)",
            "",
        ]
    elif content_type == 'application/x-www-form-urlencoded':
        return [
            "        # Prepare form data",
            "        request_body = {",
            *[f"            '{k}': '{v}'," for k, v in body_data.items()],
            "        }",
            "",
        ]
    return []


def generate_request_execution(method: str, headers: Dict[str, str], has_body: bool) -> List[str]:
    """Generate request execution code."""
    lines = [
        f"        method = '{method}'  # Store HTTP method",
        "",
        "        logger.debug(f'Making {method.upper()} request to URL: {url}')",
        "        logger.debug(f'Request headers: {headers}')",
        "",
        "        # Make request",
        "        response = getattr(session, method)(",
        "            url=url,",
        "            headers=headers,",
    ]

    if has_body:
        # Use json parameter if Content-Type is application/json
        if headers.get('Content-Type') == 'application/json':
            lines.append("            json=request_body,")
        else:
            lines.append("            data=request_body,")

    lines.extend([
        "        )",
        "        logger.debug(f'Response status code: {response.status_code}')",
        "        logger.debug(f'Response headers: {dict(response.headers)}')",
        "",
        "        assert response.status_code == 200  # TODO: Update expected status code",
        "",
    ])

    return lines


def build_test_function(item: 'PostmanItem', name: str, method: str, formatted_url: str,
                       variables: Dict[str, Variable], variable_registry: dict,
                       auth_config: Optional[dict] = None) -> str:
    """Build complete test function."""
    from .test_dependencies import get_test_dependencies, generate_response_extraction
    
    test_lines = []
    
    # Add imports and logging setup
    test_lines.extend(generate_imports())
    test_lines.append("")
    test_lines.extend(generate_logging_setup())
    
    # Add auth fixture if needed
    if auth_config and auth_config.type == "oauth":
        test_lines.extend(generate_oauth_fixture())

    # Get dependencies and patterns
    deps, patterns = get_test_dependencies(variables, variable_registry)

    # Generate function definition
    fixture_params = get_required_fixtures(auth_config, deps, bool(patterns))
    description = item.request.description if hasattr(item.request, 'description') else None
    test_lines.extend(generate_function_definition(name, method, fixture_params, description))

    # Add request setup
    test_lines.append(generate_request_setup())
    
    # Add URL setup
    test_lines.extend([
        f"        formatted_url = '{formatted_url}'  # Store formatted URL",
        ""
    ])
    test_lines.append(generate_url_resolution_code())

    # Add headers setup
    test_lines.extend(generate_header_setup(item, auth_config))

    # Add body setup if present
    test_lines.extend(generate_body_setup(item))

    # Add request execution
    headers = build_headers(item, auth_config)
    has_body = bool(item.request.body and isinstance(item.request.body, dict) and 'raw' in item.request.body)
    test_lines.extend(generate_request_execution(method, headers, has_body))

    # Add response handling
    test_lines.append(generate_response_handling())

    # Add response data storage for dependent tests
    test_lines.extend(generate_response_extraction(name, patterns))

    return "\n".join(test_lines)
