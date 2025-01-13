"""Test dependency management utilities."""

from typing import Dict, List, Optional, Set, Tuple
from ..core.variable_types import Variable


def get_test_dependencies(variables: Dict[str, Variable], variable_registry: dict) -> Tuple[Set[str], Dict[str, str]]:
    """Get test dependencies and their response patterns.
    
    Args:
        variables: Dictionary of variables used in the test
        variable_registry: Variable registry containing dependency information
        
    Returns:
        Tuple of (set of dependent test names, dict mapping variable names to their regex patterns)
    """
    needed_deps = set()
    patterns = {}
    
    for var_name in variables:
        if var_name in variable_registry.get('variables', {}):
            var_data = variable_registry['variables'][var_name]
            if var_data.get('source') == 'fixture' and var_data.get('response_pattern'):
                response_pattern = var_data['response_pattern']
                if 'source_test' in response_pattern and response_pattern['source_test']:
                    needed_deps.add(response_pattern['source_test'])
                    patterns[var_name] = response_pattern['regex']
    
    return needed_deps, patterns


def get_fixture_parameters(deps: Set[str], patterns: Dict[str, str]) -> List[str]:
    """Get list of required fixture parameters.
    
    Args:
        deps: Set of test dependencies
        patterns: Dict mapping variable names to their regex patterns
        
    Returns:
        List of fixture parameter names needed for the test
    """
    params = ['base_url', 'resolve_variable', 'store_response_data']
    if deps:
        params.append('get_response_data')
    return params


def generate_response_extraction(test_name: str, patterns: Dict[str, str]) -> List[str]:
    """Generate code to store response data for dependent tests.
    
    Args:
        test_name: Name of the current test
        patterns: Dict mapping variable names to their regex patterns
        
    Returns:
        List of code lines for response data extraction and storage
    """
    if not patterns:
        return []
        
    lines = [
        "        # Store response data for dependent tests",
        "        try:",
        "            response_data = response.json()",
        "            store_response_data(test_name, response_data)",
        "        except Exception as e:",
        "            logger.error(f'Failed to store response data: {e}')",
        ""
    ]
    
    return lines
