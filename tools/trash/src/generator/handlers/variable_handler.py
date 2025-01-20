"""Variable handling utilities for test generation."""

from typing import Dict, List
from .fixtures import FixtureGenerator


def initialize_variables(variables: Dict[str, List[str]]) -> List[str]:
    """Generate variable initialization code.

    Args:
        variables: Variable dependency mapping

    Returns:
        List of lines initializing variables
    """
    lines = [
        "# Initialize variables"
    ]
    for var_name in variables:
        lines.append(f"_variable_store['{var_name}'] = None")
    lines.append("")
    return lines


def generate_variable_fixtures(
    variables: Dict[str, List[str]], fixture_generator: FixtureGenerator
) -> List[str]:
    """Generate fixtures for dynamic variables.

    Args:
        variables: Variable dependency mapping
        fixture_generator: Generator for test fixtures

    Returns:
        List of fixture definitions
    """
    fixture_lines = []
    for var_name in variables:
        # Get fixture scope from fixture_generator
        scope = fixture_generator.fixtures[var_name]["scope"] if var_name in fixture_generator.fixtures else "function"
        docstring = fixture_generator.fixtures[var_name]["docstring"] if var_name in fixture_generator.fixtures else f"Get {var_name} from variable store."
        
        fixture_lines.extend([
            f"@pytest.fixture(scope='{scope}')",
            f"def {var_name}():",
            f'    """{docstring}"""',
            f"    return _variable_store.get('{var_name}')",
            "",
        ])
    return fixture_lines


def handle_response_variables(request_details: Dict[str, any]) -> List[str]:
    """Generate code for handling response variables.

    Args:
        request_details: Request details containing variable information

    Returns:
        List of lines handling response variables
    """
    if "sets" not in request_details:
        return []

    return [
        "",
        "    # Extract response data",
        "    try:",
        "        response_data = response.json()",
        "        if 'Id' not in response_data:",
        "            raise ValueError(f'Could not find ID in response')",
        *[f"        _variable_store['{var}'] = response_data['Id']" for var in request_details["sets"]],
        "    except ValueError as e:",
        "        pytest.fail(f'Failed to parse response JSON: {str(e)}')",
        "    except KeyError as e:",
        "        pytest.fail(f'Required response field not found: {str(e)}')",
    ]
