"""
Generator for pytest test content from Postman requests.
"""

import re
from typing import Dict, Any, List, Optional
from src.utils.auth import AuthManager
from src.generator.fixtures import FixtureGenerator
from src.generator.request_formatter import RequestFormatter


class TestContentGenerator:
    """Generates pytest test content from Postman requests."""

    def __init__(self, auth_manager: AuthManager):
        """Initialize test content generator.

        Args:
            auth_manager: Authentication manager for handling auth configuration
        """
        self.auth_manager = auth_manager
        self.request_formatter = RequestFormatter()

    def _format_test_name(self, endpoint: str, method: str = None) -> str:
        """Format endpoint as test function name.

        Args:
            endpoint: Endpoint path or name
            method: HTTP method (optional)

        Returns:
            Formatted test function name
        """
        # Remove leading/trailing slashes and spaces
        name = endpoint.strip("/ ")
        # Replace slashes and spaces with underscores
        name = name.replace("/", "_").replace(" ", "_").lower()
        # Remove any {{var}} placeholders
        name = re.sub(r"\{\{.*?\}\}", "", name)
        # Clean up any double underscores
        name = re.sub(r"_+", "_", name)
        # Add method prefix if provided
        if method:
            name = f"{method.lower()}_{name}"
            # Remove any double method prefixes
            name = re.sub(r'(get|post|put|delete)_\1', r'\1', name)
        return f"test_test_{name}"

    def _generate_imports(self) -> List[str]:
        """Generate required import statements.

        Returns:
            List of import statements
        """
        return [
            "import pytest",
            "import requests",
            "import base64",
            "import os",
            "from typing import Dict, Any",
            "from requests_oauthlib import OAuth2Session",
            "from oauthlib.oauth2 import BackendApplicationClient",
            "",
            "# Environment configuration",
            "ENV_URL = os.getenv('ENV_URL')",
            "CLIENT_ID = os.getenv('CLIENT_ID')",
            "USER_LEGAL_OWNER = os.getenv('USER_LEGAL_OWNER')",
            "",
            "# Authentication configuration",
            'BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME")',
            'BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD")',
            'AUTH_TOKEN_URL = os.getenv("OAUTH_TOKEN_URL")',
            "",
            "# Validate required auth configuration",
            "if not all([BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD, AUTH_TOKEN_URL]):",
            '    pytest.skip("Missing required environment variables for authentication")',
            "",
        ]

    def _generate_auth_fixture(self) -> List[str]:
        """Generate auth fixture configuration.

        Returns:
            List of lines for auth fixture
        """
        return [
            "@pytest.fixture(scope='session')",
            "def auth_session(tls_verify):",
            '    """Create authenticated session."""',
            "    client = BackendApplicationClient(client_id=BASIC_AUTH_USERNAME)",
            "    session = OAuth2Session(client=client)",
            "",
            "    try:",
            "        # Get token",
            "        token = session.fetch_token(",
            "            token_url=AUTH_TOKEN_URL,",
            "            client_id=BASIC_AUTH_USERNAME,",
            "            client_secret=BASIC_AUTH_PASSWORD,",
            "            verify=tls_verify",
            "        )",
            "    except Exception as e:",
            '        pytest.skip(f"Failed to fetch OAuth token: {str(e)}")',
            "",
            "    return session",
            "",
        ]

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
            List of lines for test function
        """
        function_lines = []

        # Add dependency marker if needed
        if dependencies:
            deps_str = '", "'.join(dependencies)
            function_lines.append(f'@pytest.mark.dependency(depends=["{deps_str}"])')
        else:
            function_lines.append('@pytest.mark.dependency()')

        # Function definition with fixtures
        fixtures = ["auth_session", "env_url", "tls_verify"] + variables
        fixtures_str = ", ".join(fixtures)
        function_lines.append(f"def {name}({fixtures_str}):")

        # Function docstring
        function_lines.append(
            f'    """{request_details.get("name", "Test request")}."""'
        )

        # Format request details
        request = request_details.get("request", request_details)
        function_lines.extend(self.request_formatter.format_request_details(request))

        # Handle response variables if needed
        if "sets" in request_details:
            function_lines.extend([
                "",
                "    # Extract response data",
                "    response_data = response.json()",
                "    return response_data",
            ])

        function_lines.append("")
        return function_lines

    def generate_test_content(
        self,
        request_details: Dict[str, Any],
        dependencies: List[Dict[str, Any]],
        variables: Dict[str, List[str]],
        fixture_generator: FixtureGenerator,
    ) -> str:
        """Generate complete test file content.

        Args:
            request_details: Main request details
            dependencies: List of dependent requests
            variables: Variable dependency mapping
            fixture_generator: Generator for test fixtures

        Returns:
            Complete test file content
        """
        content_lines = []

        # Add imports
        content_lines.extend(self._generate_imports())
        content_lines.extend(self._generate_auth_fixture())

        # Add dependent tests in order
        processed_deps = []
        for dep in dependencies:
            method = dep.get("request", {}).get("method", "GET")
            dep_name = self._format_test_name(dep["endpoint"], method)
            dep_deps = [d for d in processed_deps]
            content_lines.extend(
                self._generate_test_function(
                    name=dep_name,
                    request_details=dep,
                    dependencies=dep_deps,
                    variables=[v for v in variables if dep.get("sets", []) and v in dep["sets"]],
                    fixture_generator=fixture_generator,
                )
            )
            processed_deps.append(dep_name)

        # Add main test
        method = request_details.get("request", {}).get("method", "GET")
        main_name = self._format_test_name(request_details["name"], method)
        dep_names = [
            self._format_test_name(dep["endpoint"], dep.get("request", {}).get("method", "GET"))
            for dep in dependencies
        ]
        content_lines.extend(
            self._generate_test_function(
                name=main_name,
                request_details=request_details,
                dependencies=dep_names,
                variables=list(variables.keys()),
                fixture_generator=fixture_generator,
            )
        )

        return "\n".join(content_lines)
