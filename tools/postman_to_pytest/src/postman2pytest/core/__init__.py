"""Core functionality for postman2pytest."""

from .parser import (
    PostmanUrl,
    PostmanRequest,
    PostmanItem,
    PostmanItemGroup,
    PostmanInfo,
    PostmanCollection,
    parse_collection
)

from .url_utils import (
    sanitize_name,
    format_url,
    create_test_file_path
)

from .variable_types import (
    VariableSource,
    VariableType,
    Variable,
    RegistryVariable
)

from .variable_handler import (
    is_domain_variable,
    classify_variable,
    extract_variables,
    extract_default_value,
    collect_variables_from_request,
    generate_env_file,
    generate_variable_registry,
    copy_variable_registry,
    RANDOM_VAR_MAPPING
)

from .variable_registry import VariableRegistry
from .generator import TestGenerator, create_test_generator
from .conftest_generator import create_conftest
from .file_manager import FileManager
from .variable_processor import VariableProcessor
from .test_file_generator import TestFileGenerator

__all__ = [
    # Parser
    'PostmanUrl',
    'PostmanRequest',
    'PostmanItem',
    'PostmanItemGroup',
    'PostmanInfo',
    'PostmanCollection',
    'parse_collection',
    
    # URL Utils
    'sanitize_name',
    'format_url',
    'create_test_file_path',
    
    # Variable Types
    'VariableSource',
    'VariableType',
    'Variable',
    'RegistryVariable',
    
    # Variable Handler
    'is_domain_variable',
    'classify_variable',
    'extract_variables',
    'extract_default_value',
    'collect_variables_from_request',
    'generate_env_file',
    'generate_variable_registry',
    'copy_variable_registry',
    'RANDOM_VAR_MAPPING',
    
    # Variable Registry
    'VariableRegistry',
    
    # Generator Components
    'TestGenerator',
    'create_test_generator',
    'create_conftest',
    'FileManager',
    'VariableProcessor',
    'TestFileGenerator'
]
