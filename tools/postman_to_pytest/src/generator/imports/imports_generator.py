"""
Generator for pytest import statements and environment configuration.
"""

from typing import Dict, List, Any


class ImportsGenerator:
    """Generates import statements and environment configuration."""

    def generate_imports(self, request_details: Dict[str, Any] = None) -> List[str]:
        """Generate required import statements.

        Args:
            request_details: Request details containing variable information (optional)

        Returns:
            List of import statements
        """
        # Get dynamic variables if request_details provided
        dynamic_vars = set()
        if request_details and "uses_variables" in request_details:
            for var_name, var_info in request_details["uses_variables"].items():
                if isinstance(var_info, dict) and var_info.get("type") == "dynamic":
                    dynamic_vars.add(var_name)

        lines = [
            "import pytest",
            "import requests",
            "import base64",
            "import os",
            "from typing import Dict, Any",
            "from requests_oauthlib import OAuth2Session",
            "from oauthlib.oauth2 import BackendApplicationClient",
            "",
            "# Environment configuration",
            'ENV_URL = os.getenv("ENV_URL")',
            'CLIENT_ID = os.getenv("CLIENT_ID")',
        ]

        # Only add USER_LEGAL_OWNER as env var if not marked as dynamic
        if "user_legal_owner" not in dynamic_vars:
            lines.append('USER_LEGAL_OWNER = os.getenv("USER_LEGAL_OWNER")')

        lines.extend([
            "",
            "# Variable storage for dynamic variables",
            "_variable_store: Dict[str, Any] = {}",
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
        ])

        return lines

    def generate_variable_fixtures(self, variables: Dict[str, List[str]]) -> List[str]:
        """Generate fixtures for variables.

        Args:
            variables: Variable dependency mapping

        Returns:
            List of fixture lines
        """
        lines = []
        for var_name in variables.keys():
            lines.extend([
                f"@pytest.fixture(scope='function')",
                f"def {var_name}():",
                f'    """Variable set by dependency."""',
                f"    return _variable_store.get('{var_name}')",
                "",
            ])
        return lines

    def generate_variable_storage(self, var_name: str) -> List[str]:
        """Generate variable storage code.

        Args:
            var_name: Name of variable to store

        Returns:
            List of variable storage lines
        """
        return [
            "",
            "    # Store variables for later use",
            "    response_data = response.json()",
            f"    if 'Id' in response_data:",
            f"        _variable_store['{var_name}'] = response_data['Id']",
            f"    elif 'id' in response_data:",
            f"        _variable_store['{var_name}'] = response_data['id']",
            f"    else:",
            f"        raise ValueError(f'Could not find ID in response: {{response_data}}')",
            "",
        ]
