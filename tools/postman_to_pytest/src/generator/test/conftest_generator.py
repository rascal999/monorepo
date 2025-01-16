"""Conftest file generation utilities."""

from pathlib import Path
from typing import Any, Optional


class ConftestGenerator:
    """Generates conftest.py with environment and auth configuration."""

    def __init__(self, output_dir: str, auth_manager: Optional[Any] = None):
        """Initialize conftest generator.

        Args:
            output_dir: Output directory for generated tests
            auth_manager: Optional auth manager for OAuth configuration
        """
        self.output_dir = output_dir
        self.auth_manager = auth_manager

    def generate(self) -> None:
        """Generate conftest.py with environment and auth configuration."""
        lines = [
            "import os",
            "import base64",
            "import pytest",
            "from dotenv import load_dotenv",
            "from requests_oauthlib import OAuth2Session",
            "from oauthlib.oauth2 import BackendApplicationClient",
            "",
            "# Load environment variables",
            "load_dotenv()",
            "",
            "# Environment configuration",
            "ENV_URL = os.getenv('ENV_URL')",
            "TLS_VERIFY = os.getenv('TLS_VERIFY', 'true').lower() == 'true'",
            "",
            "# Authentication configuration",
        ]

        # Add auth configuration based on auth manager
        if self.auth_manager:
            if hasattr(self.auth_manager, 'oauth_token_url'):
                # Use hardcoded values from auth manager
                lines.extend([
                    f'AUTH_TOKEN_URL = "{self.auth_manager.oauth_token_url}"',
                    f'BASIC_AUTH_USERNAME = "{self.auth_manager.basic_auth_username}"',
                    f'BASIC_AUTH_PASSWORD = "{self.auth_manager.basic_auth_password}"',
                ])
            else:
                # Fall back to environment variables
                lines.extend([
                    'AUTH_TOKEN_URL = os.getenv("OAUTH_TOKEN_URL")',
                    'BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME")',
                    'BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD")',
                ])
            lines.extend([
                "",
                "# Validate required auth configuration",
                "if not all([BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD, AUTH_TOKEN_URL]):",
                '    pytest.skip("Missing required environment variables for authentication")',
            ])
        else:
            # No auth manager, use None values
            lines.extend([
                'AUTH_TOKEN_URL = None',
                'BASIC_AUTH_USERNAME = None',
                'BASIC_AUTH_PASSWORD = None',
            ])

        # Add auth session fixture
        lines.extend([
            "",
            "@pytest.fixture(scope='session')",
            "def auth_session():",
            '    """Create authenticated session."""',
            "",
            "    # Create OAuth2 session",
            "    client = BackendApplicationClient(client_id=BASIC_AUTH_USERNAME)",
            "    session = OAuth2Session(client=client)",
            "",
            "    try:",
            "        # Get token",
            "        token = session.fetch_token(",
            "            token_url=AUTH_TOKEN_URL,",
            "            client_id=BASIC_AUTH_USERNAME,",
            "            client_secret=BASIC_AUTH_PASSWORD,",
            "            verify=TLS_VERIFY",
            "        )",
            "    except Exception as e:",
            '        pytest.skip(f"Failed to fetch OAuth token: {str(e)}")',
            "",
            "    return session",
            "",
        ])

        # Write conftest.py
        conftest_path = Path(self.output_dir) / "conftest.py"
        conftest_path.write_text("\n".join(lines))
