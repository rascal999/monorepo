"""
Generator for authentication-related pytest code.
"""

import pytest
from typing import List
from src.utils.auth import AuthManager
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient


class AuthGenerator:
    """Generates authentication-related pytest code."""

    def __init__(self, auth_manager: AuthManager):
        """Initialize auth generator.

        Args:
            auth_manager: Authentication manager for handling auth configuration
        """
        self.auth_manager = auth_manager

    def generate_auth_config(self) -> List[str]:
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
            "# Validate required auth configuration",
            "if not all([BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD, AUTH_TOKEN_URL]):",
            '    pytest.skip("Missing required environment variables for authentication")',
            "",
        ]

    def generate_auth_fixture(self) -> List[str]:
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
