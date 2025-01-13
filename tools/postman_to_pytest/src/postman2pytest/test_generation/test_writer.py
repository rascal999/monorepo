"""Test writing interface."""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

from .test_generator import generate_test_function
from .test_dependencies import (
    get_test_dependencies,
    get_fixture_parameters,
    generate_response_extraction
)
from .test_function_builder import build_test_function
from .test_request_builder import (
    build_headers,
    prepare_request_body,
    generate_request_setup,
    generate_response_handling,
    generate_json_processor
)
from .test_url_handler import (
    process_url_variables,
    generate_url_resolution_code,
    get_url_from_item,
    process_url
)
from .test_imports import (
    generate_imports,
    generate_oauth_fixture,
    generate_logging_setup
)
from .test_utils import (
    parse_markdown_link,
    format_dict
)
from ..core.variable_types import Variable
from ..core.url_utils import sanitize_name, format_url
from ..core.variable_handler import extract_variables

logger = logging.getLogger(__name__)


def write_test_file(item: 'PostmanItem', file_path: Path, variable_registry: dict,
                   auth_config: Optional[dict] = None, version: Optional[str] = None,
                   client_id: Optional[str] = None) -> None:
    """Write a test file for a Postman request.
    
    Args:
        item: PostmanItem containing the request
        file_path: Path where the test file should be written
        variable_registry: Variable registry for dependencies
        auth_config: Optional authentication configuration
        version: Optional API version for module path
        client_id: Optional client ID for module path
    """
    logger.debug(f"Writing test file for: {item.name}")
    
    test_content = generate_test_function(
        item=item,
        url_formatter=format_url,
        sanitize_func=sanitize_name,
        variable_extractor=extract_variables,
        variable_registry=variable_registry,
        auth_config=auth_config,
        version=version,
        client_id=client_id
    )
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(test_content)
    logger.debug(f"Successfully wrote test file: {file_path}")


__all__ = [
    # Main interface
    'write_test_file',
    'generate_test_function',
    
    # Dependencies
    'get_test_dependencies',
    'get_fixture_parameters',
    'generate_response_extraction',
    
    # Function building
    'build_test_function',
    
    # Request handling
    'build_headers',
    'prepare_request_body',
    'generate_request_setup',
    'generate_response_handling',
    'generate_json_processor',
    
    # URL handling
    'process_url_variables',
    'generate_url_resolution_code',
    'get_url_from_item',
    'process_url',
    
    # Imports and setup
    'generate_imports',
    'generate_oauth_fixture',
    'generate_logging_setup',
    
    # Utilities
    'parse_markdown_link',
    'format_dict'
]
