"""postman2pytest package."""

__version__ = "0.1.0"

from .core import (
    # Types
    VariableSource,
    VariableType,
    Variable,
    RegistryVariable,
    
    # Variable Management
    is_domain_variable,
    classify_variable,
    extract_variables,
    extract_default_value,
    collect_variables_from_request,
    RANDOM_VAR_MAPPING,
    VariableRegistry,
    
    # File Operations
    generate_env_file,
    generate_variable_registry,
    copy_variable_registry
)

from .test_generation import (
    # Utils
    parse_markdown_link,
    format_dict,
    
    # Imports
    generate_imports,
    generate_oauth_fixture,
    generate_logging_setup,
    
    # Request Builder
    build_headers,
    prepare_request_body,
    generate_request_setup,
    generate_response_handling,
    generate_json_processor,
    
    # URL Handler
    process_url_variables,
    generate_url_resolution_code,
    get_url_from_item,
    process_url,
    
    # Dependencies
    get_test_dependencies,
    
    # Function Builder
    get_required_fixtures,
    generate_function_definition,
    generate_header_setup,
    generate_body_setup,
    generate_request_execution,
    build_test_function,
    
    # Generator
    generate_test_function
)

from .auth import AuthHandler
from .cli import main

__all__ = [
    # Version
    '__version__',
    
    # Core - Types
    'VariableSource',
    'VariableType',
    'Variable',
    'RegistryVariable',
    
    # Core - Variable Management
    'is_domain_variable',
    'classify_variable',
    'extract_variables',
    'extract_default_value',
    'collect_variables_from_request',
    'RANDOM_VAR_MAPPING',
    'VariableRegistry',
    
    # Core - File Operations
    'generate_env_file',
    'generate_variable_registry',
    'copy_variable_registry',
    
    # Test Generation - Utils
    'parse_markdown_link',
    'format_dict',
    
    # Test Generation - Imports
    'generate_imports',
    'generate_oauth_fixture',
    'generate_logging_setup',
    
    # Test Generation - Request Builder
    'build_headers',
    'prepare_request_body',
    'generate_request_setup',
    'generate_response_handling',
    'generate_json_processor',
    
    # Test Generation - URL Handler
    'process_url_variables',
    'generate_url_resolution_code',
    'get_url_from_item',
    'process_url',
    
    # Test Generation - Dependencies
    'get_test_dependencies',
    
    # Test Generation - Function Builder
    'get_required_fixtures',
    'generate_function_definition',
    'generate_header_setup',
    'generate_body_setup',
    'generate_request_execution',
    'build_test_function',
    
    # Test Generation - Generator
    'generate_test_function',
    
    # Auth
    'AuthHandler',
    
    # CLI
    'main'
]
