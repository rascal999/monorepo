"""Test content generation utilities."""

from typing import Dict, Any, List
from src.generator.handlers.fixtures import FixtureGenerator
from .test_function_generator import TestFunctionGenerator
from ..formatters.name_formatter import format_test_name


class ContentGenerator:
    """Generates test content from Postman requests."""

    def __init__(self, auth_manager: Any):
        """Initialize content generator.

        Args:
            auth_manager: Auth manager for OAuth configuration
        """
        self.auth_manager = auth_manager
        self.test_function_generator = TestFunctionGenerator()

    def _generate_auth_fixture(self) -> List[str]:
        """Generate auth session fixture.

        Returns:
            List of code lines for auth fixture
        """
        lines = [
            "@pytest.fixture(scope='session')",
            'def auth_session(tls_verify):',
            '    """Session with auth token."""',
            '    client = BackendApplicationClient(client_id=BASIC_AUTH_USERNAME)',
            '    session = OAuth2Session(client=client)',
            '',
            '    # Fetch token with error handling',
            '    try:',
            '        token = session.fetch_token(',
            '            token_url=AUTH_TOKEN_URL,',
            '            client_id=BASIC_AUTH_USERNAME,',
            '            client_secret=BASIC_AUTH_PASSWORD,',
            '            verify=tls_verify',
            '        )',
            '    except Exception as e:',
            '        pytest.skip(f"Failed to fetch OAuth token: {str(e)}")',
            '',
            '    return session',
            '',
        ]
        return lines

    def _generate_imports(self) -> List[str]:
        """Generate import statements.

        Returns:
            List of import lines
        """
        lines = [
            "import pytest",
            "import requests",
            "import os",
            "import base64",
            "import json",
            "from typing import Dict, Any",
            "from requests_oauthlib import OAuth2Session",
            "from oauthlib.oauth2 import BackendApplicationClient",
            "",
            "# Environment variables",
            'ENV_URL = os.getenv("ENV_URL")',
            'CLIENT_ID = os.getenv("CLIENT_ID")',
            'BASIC_AUTH_USERNAME = "test_client"',
            'BASIC_AUTH_PASSWORD = "test_secret"',
            f'AUTH_TOKEN_URL = "{self.auth_manager.oauth_token_url}"',
            "",
            "# Initialize variable store",
            "_variable_store: Dict[str, Any] = {}",
            "",
        ]
        return lines

    def _generate_test_function(
        self,
        name: str,
        request_details: Dict[str, Any],
        dependencies: List[str],
        variables: List[str],
        fixture_generator: FixtureGenerator,
    ) -> List[str]:
        """Generate a test function.

        Args:
            name: Test function name
            request_details: Request details from Postman
            dependencies: List of dependent test names
            variables: List of required variables
            fixture_generator: Generator for test fixtures

        Returns:
            List of code lines for test function
        """
        return self.test_function_generator.generate_test_function(
            name=name,
            request_details=request_details,
            dependencies=dependencies,
            variables=variables,
            fixture_generator=fixture_generator,
        )

    def generate_test_content(
        self,
        request_details: Dict[str, Any],
        dependencies: List[Dict[str, Any]],
        variables: Dict[str, List[str]],
        fixture_generator: FixtureGenerator,
        include_method_in_name: bool = False,
    ) -> str:
        """Generate test content for request.

        Args:
            request_details: Request details
            dependencies: List of dependent requests
            variables: Variable dependency mapping
            fixture_generator: Generator for test fixtures
            include_method_in_name: Whether to include HTTP method in test names

        Returns:
            Generated test content
        """
        lines = self._generate_imports()

        # Initialize variables for circular dependencies
        for name in variables.keys():
            lines.append(f"_variable_store['{name}'] = None")
        lines.append("")

        # Add auth session fixture first
        lines.extend(self._generate_auth_fixture())

        # Track which fixtures have been added
        added_fixtures = {"auth_session"}

        # Add fixtures from fixture generator
        for name, fixture in fixture_generator.fixtures.items():
            added_fixtures.add(name)
            # Add fixture decorator with scope from generator
            # Use double quotes for module scope, single quotes for function scope
            scope_str = f'scope="{fixture["scope"]}"' if fixture["scope"] == "module" else f"scope='{fixture['scope']}'"
            lines.append(f"@pytest.fixture({scope_str})")
            # Add fixture function with dependencies
            if fixture["dependencies"]:
                deps = ", ".join(fixture["dependencies"])
                lines.append(f"def {name}({deps}):")
            else:
                lines.append(f"def {name}():")
            # Add docstring
            lines.append(f'    """{fixture["docstring"]}"""')
            # Add dynamic variable handling
            if fixture["type"] == "dynamic":
                lines.extend([
                    "    # Get value from store",
                    f"    value = _variable_store.get('{name}')",
                    "    if value is None:",
                    "        pytest.skip('Required variable not set')",
                    "    yield value",
                    "    # Cleanup",
                    f"    if '{name}' in _variable_store:",
                    f"        del _variable_store['{name}']",
                ])
            else:  # static
                lines.extend([
                    "    # Return static value",
                    f"    return _variable_store.get('{name}')",
                ])
            lines.append("")

        # Order tests based on dependencies
        # Create a wrapper for format_test_name that controls method inclusion
        def format_name_with_method(name, method=None, **kwargs):
            return format_test_name(name, method=method, include_method=include_method_in_name)
        
        ordered_tests = self.test_function_generator.order_tests(
            request_details=request_details,
            dependencies=dependencies,
            variables=variables,
            format_test_name_fn=format_name_with_method,
        )

        # Generate test functions
        for test in ordered_tests:
            lines.extend(
                self.test_function_generator.generate_test_function(
                    name=test["name"],
                    request_details=test["details"],
                    dependencies=test["dependencies"],
                    variables=test["variables"],
                    fixture_generator=fixture_generator,
                )
            )

        # Add fixtures for remaining variables
        for var_name in variables.keys():
            if var_name not in added_fixtures:
                # Add fixture decorator
                lines.append(f"@pytest.fixture(scope='function')")  # Always use single quotes for function scope
                # Add fixture function
                lines.append(f"def {var_name}():")
                # Add docstring
                lines.append(f'    """Variable {var_name}"""')
                # Add variable handling
                lines.extend([
                    "    # Get value from store",
                    f"    value = _variable_store.get('{var_name}')",
                    "    if value is None:",
                    f"        pytest.skip('Required variable {var_name} not set')",
                    "    yield value",
                    "    # Cleanup",
                    f"    if '{var_name}' in _variable_store:",
                    f"        del _variable_store['{var_name}']",
                ])
                lines.append("")

        return "\n".join(lines)
