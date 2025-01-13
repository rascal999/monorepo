"""Test generation coordination."""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

from .test_dependencies import get_test_dependencies
from .test_function_builder import build_test_function
from ..core.variable_types import Variable
from ..core.url_utils import sanitize_name
from ..core.variable_handler import collect_variables_from_request

logger = logging.getLogger(__name__)


def generate_test_function(item: 'PostmanItem', url_formatter, sanitize_func, 
                         variable_registry: dict, auth_config=None, version: str = None, 
                         client_id: str = None) -> str:
    """Generate a pytest test function from a Postman request.
    
    Args:
        item: PostmanItem containing the request
        url_formatter: Function to format URLs with variables
        sanitize_func: Function to sanitize names for Python
        variable_extractor: Function to extract variables from request
        variable_registry: Variable registry for dependencies
        auth_config: Optional authentication configuration
        version: Optional API version for module path
        client_id: Optional client ID for module path
        
    Returns:
        Generated test function as a string
    """
    # Extract basic information
    name = sanitize_func(item.name)
    method = item.request.method.lower()

    # Extract and process variables
    variables = collect_variables_from_request(item)
    logger.debug(f"Extracted variables: {[f'{k}: {v.type.value}' for k, v in variables.items()]}")
    
    # Build the test function
    return build_test_function(
        item=item,
        name=name,
        method=method,
        formatted_url=url_formatter(item.request.url.raw, variables, sanitize_func),
        variables=variables,
        variable_registry=variable_registry,
        auth_config=auth_config
    )
