"""
Generator for pytest test file content.
"""

from typing import Dict, List, Any, Optional
import base64
from dotenv import load_dotenv
from .request_formatter import RequestFormatter


class TestContentGenerator:
    def __init__(self, auth_manager: Optional[Any] = None):
        """Initialize test content generator.

        Args:
            auth_manager: Optional auth manager for OAuth configuration
        """
        self.auth_manager = auth_manager
        self.request_formatter = RequestFormatter()

    def _generate_auth_fixture(self) -> List[str]:
        """Generate OAuth authentication fixture.

        Returns:
            List of auth fixture lines
        """
        return [
            "from requests_oauthlib import OAuth2Session",
            "from oauthlib.oauth2 import BackendApplicationClient",
            "",
            "# Import auth configuration",
            "BASIC_AUTH_USERNAME = os.getenv('BASIC_AUTH_USERNAME')",
            "BASIC_AUTH_PASSWORD = os.getenv('BASIC_AUTH_PASSWORD')",
            "AUTH_TOKEN_URL = os.getenv('OAUTH_TOKEN_URL')",
            "",
            "@pytest.fixture(scope='session')",
            "def auth_session(tls_verify):",
            "    \"\"\"Get OAuth authentication token.\"\"\"",
            "    client = BackendApplicationClient(client_id=BASIC_AUTH_USERNAME)",
            "    session = OAuth2Session(client=client)",
            "    token = session.fetch_token(",
            "        token_url=AUTH_TOKEN_URL,",
            "        client_id=BASIC_AUTH_USERNAME,",
            "        client_secret=BASIC_AUTH_PASSWORD,",
            "        verify=tls_verify",
            "    )",
            "    return session",
            "",
        ]

    def _generate_imports(self) -> List[str]:
        """Generate import statements.

        Returns:
            List of import lines
        """
        return [
            "import pytest",
            "import requests",
            "import base64",
            "import os",
            "from typing import Dict, Any",
            "",
            "# Import environment variables",
            "ENV_URL = os.getenv('ENV_URL')",
            "CLIENT_ID = os.getenv('CLIENT_ID')",
            "USER_LEGAL_OWNER = os.getenv('USER_LEGAL_OWNER')",
            "",
        ]

    def _generate_test_function(
        self,
        name: str,
        request_details: Dict[str, Any],
        dependencies: List[str],
        variables: List[str],
        fixture_generator: Any,
    ) -> List[str]:
        """Generate a test function.

        Args:
            name: Test function name
            request_details: Request details dict
            dependencies: List of dependency test names
            variables: List of required variables
            fixture_generator: Fixture generator instance

        Returns:
            List of test function lines
        """
        lines = []

        # Add dependencies to test decorator
        if dependencies:
            deps = [f'"{d}"' for d in dependencies]
            dep_str = f'depends=[{", ".join(deps)}]'
            lines.append(f"@pytest.mark.dependency({dep_str})")
        else:
            lines.append("@pytest.mark.dependency()")

        # Generate function definition with variables and fixtures
        test_vars = ["auth_session", "env_url", "tls_verify"] + variables
        lines.extend([
            f"def {name}({', '.join(test_vars)}):",
            f'    """Test {name}"""',
        ])

        # Add request details
        lines.extend(self.request_formatter.format_request_details(request_details))

        # Add response handling
        lines.extend([
            "    # Add auth header",
            "    headers['Authorization'] = f'Bearer {auth_session.token[\"access_token\"]}'",
            "",
            "    # Make request using auth session",
            "    response = auth_session.request(",
            "        method=method,",
            "        url=url,",
            "        headers=headers,",
            "        data=data,",
            "        verify=tls_verify",
            "    )",
            "    assert response.status_code == 200",
        ])

        # Set variables for next tests if this is a dependency
        for var in request_details.get("sets", []):
            lines.append(
                f"    {fixture_generator.get_fixture_setup(var, 'response.json()')}"
            )

        lines.extend(["", ""])
        return lines

    def generate_test_content(
        self,
        request_details: Dict[str, Any],
        dependencies: List[Dict[str, Any]],
        variables: Dict[str, List[str]],
        fixture_generator: Any,
    ) -> str:
        """Generate complete test file content.

        Args:
            request_details: Dict with request information
            dependencies: List of dependency endpoint information
            variables: Dict mapping variables to setter endpoints
            fixture_generator: Fixture generator instance

        Returns:
            Complete test file content
        """
        lines = []

        # Add imports and auth config
        lines.extend(self._generate_imports())
        if self.auth_manager:
            lines.extend(self._generate_auth_fixture())

        # Generate test functions for dependencies
        for dep in dependencies:
            dep_name = self.request_formatter._sanitize_name(dep["endpoint"])
            dep_vars = [v[0] for v in dep.get("uses", [])]
            lines.extend(
                self._generate_test_function(
                    f"test_{dep_name}",
                    dep["request"],
                    [],  # Dependencies are ordered, so each only depends on previous
                    dep_vars,
                    fixture_generator,
                )
            )

        # Generate main test function
        test_name = self.request_formatter._sanitize_name(request_details["name"])
        test_vars = [v[0] for v in request_details.get("uses", [])]
        dep_names = [f"test_{self.request_formatter._sanitize_name(d['endpoint'])}" for d in dependencies]
        
        lines.extend(
            self._generate_test_function(
                f"test_{test_name}",
                request_details["request"],
                dep_names,
                test_vars,
                fixture_generator,
            )
        )

        return "\n".join(lines)
