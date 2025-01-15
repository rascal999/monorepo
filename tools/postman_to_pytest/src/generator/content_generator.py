"""
Generator for pytest test content from Postman requests.
"""

import re
from typing import Dict, Any, List
from src.utils.auth import AuthManager
from src.generator.fixtures import FixtureGenerator


class ContentGenerator:
    """Generates pytest test content from Postman requests."""

    def __init__(self, auth_manager: AuthManager):
        """Initialize content generator.

        Args:
            auth_manager: Authentication manager for handling auth configuration
        """
        self.auth_manager = auth_manager

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
            "",
            "# Environment configuration",
            'ENV_URL = os.getenv("ENV_URL")',
            'CLIENT_ID = os.getenv("CLIENT_ID")',
            'USER_LEGAL_OWNER = os.getenv("USER_LEGAL_OWNER")',
            "",
            "from requests_oauthlib import OAuth2Session",
            "from oauthlib.oauth2 import BackendApplicationClient",
            "",
        ]

    def _generate_auth_config(self) -> List[str]:
        """Generate authentication configuration.

        Returns:
            List of auth configuration lines
        """
        return [
            "# Authentication configuration",
            f'BASIC_AUTH_USERNAME = "{self.auth_manager.basic_auth_username}"',
            f'BASIC_AUTH_PASSWORD = "{self.auth_manager.basic_auth_password}"',
            f'AUTH_TOKEN_URL = "{self.auth_manager.oauth_token_url}"',
            "",
        ]

    def _generate_auth_fixture(self) -> List[str]:
        """Generate authentication fixture.

        Returns:
            List of auth fixture lines
        """
        return [
            "@pytest.fixture(scope='session')",
            "def auth_session(tls_verify):",
            '    """Create authenticated session."""',
            "    client = BackendApplicationClient(client_id=BASIC_AUTH_USERNAME)",
            "    session = OAuth2Session(client=client)",
            "",
            "    # Get token",
            "    token = session.fetch_token(",
            "        token_url=AUTH_TOKEN_URL,",
            "        client_id=BASIC_AUTH_USERNAME,",
            "        client_secret=BASIC_AUTH_PASSWORD,",
            "        verify=tls_verify",
            "    )",
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
    ) -> List[str]:
        """Generate test function.

        Args:
            name: Test function name
            request_details: Request details
            dependencies: List of dependent test names
            variables: List of required variables

        Returns:
            List of test function lines
        """
        """Generate test function.

        Args:
            name: Test function name
            request_details: Request details
            dependencies: List of dependent test names
            variables: List of required variables

        Returns:
            List of test function lines
        """
        lines = []

        # Add dependency marker if needed
        if dependencies:
            deps = []
            for dep in dependencies:
                # Format endpoint name to match test function name
                dep_name = dep.lower().replace("/", "_").replace(" ", "_").strip("_")
                if dep_name.startswith("post_"):
                    dep_name = "post" + dep_name[5:]  # Remove extra underscore
                deps.append(f'test_test_{dep_name}')
            deps_str = '", "'.join(deps)
            lines.append(f'@pytest.mark.dependency(depends=["{deps_str}"])')

        # Function definition with fixtures
        fixtures = ["auth_session", "env_url", "tls_verify"] + variables
        fixtures_str = ", ".join(fixtures)
        lines.append(f"def {name}({fixtures_str}):")

        # Function docstring
        lines.append(f'    """{request_details.get("name", "Test request")}"""')

        # Request setup
        request = request_details["request"]
        lines.append(f'    method = "{request["method"]}"')

        # URL with variable substitution
        url = request["url"]["raw"]
        url = re.sub(r"\{\{([^}]+)\}\}", r"{\1}", url)
        lines.append(f'    url = f"{{env_url}}{url}"')

        # Headers with variable substitution
        if "header" in request:
            headers = {}
            for h in request["header"]:
                value = h["value"]
                # Replace {{var}} with {var} for f-string
                value = re.sub(r"\{\{([^}]+)\}\}", r"{\1}", value)
                headers[h["key"]] = value
            lines.append(f"    headers = {headers}")

        # Body
        if "body" in request and request["body"].get("mode") == "raw":
            lines.append(f'    data = {request["body"]["raw"]}')

        # Request call with explicit args
        request_args = ["method=method", "url=url"]
        if "header" in request:
            request_args.append("headers=headers")
        if "body" in request:
            request_args.append("data=data")
        request_args.append("verify=tls_verify")

        lines.extend(
            [
                "",
                "    # Make request",
                "    response = auth_session.request(",
                f"        {', '.join(request_args)}",
                "    )",
                "",
                "    # Verify response",
                "    assert response.status_code == 200",
                "",
            ]
        )

        return lines

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
        content = []

        # Add imports and configuration
        content.extend(self._generate_imports())
        content.extend(self._generate_auth_config())
        content.extend(self._generate_auth_fixture())

        # Process dependencies in order
        processed = []
        for dep in dependencies:
            endpoint = dep['endpoint']
            # Format endpoint name consistently
            dep_name = endpoint.lower().replace("/", "_").replace(" ", "_").strip("_")
            if dep_name.startswith("post_"):
                dep_name = "post" + dep_name[5:]  # Remove extra underscore
            test_name = f"test_test_{dep_name}"
            
            # Add test function
            content.extend(
                self._generate_test_function(
                    name=test_name,
                    request_details=dep,
                    dependencies=processed,  # Only depend on previously processed endpoints
                    variables=[v for v in variables if dep.get("sets", []) and v in dep["sets"]],
                )
            )
            processed.append(endpoint)

        # Add main test
        main_name = f"test_test_{request_details['name'].lower().replace(' ', '_').strip('_')}"
        dep_names = processed  # Use processed list to maintain order
        content.extend(
            self._generate_test_function(
                name=main_name,
                request_details=request_details,
                dependencies=dep_names,
                variables=list(variables.keys()),
            )
        )

        return "\n".join(content)
