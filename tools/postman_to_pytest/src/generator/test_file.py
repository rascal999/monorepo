"""
Generator for pytest test files from Postman requests and dependencies.
"""

import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from .fixtures import FixtureGenerator
from .test_content import TestContentGenerator
from ..utils.auth import AuthManager


class TestFileGenerator:
    def __init__(
        self,
        output_dir: str,
        fixture_generator: FixtureGenerator,
        auth_manager: Optional[AuthManager] = None,
        base_dir: Optional[str] = None,
    ):
        """Initialize test file generator.

        Args:
            output_dir: Directory to write test files to
            fixture_generator: FixtureGenerator instance for managing fixtures
            auth_manager: Optional auth manager for OAuth configuration
            base_dir: Optional base directory to look for .env files (defaults to current directory)
        """
        self.output_dir = Path(output_dir)
        self.fixture_generator = fixture_generator
        self.base_dir = Path(base_dir) if base_dir else Path('.')
        self.test_content_generator = TestContentGenerator(auth_manager)
        self._copy_env_file()
        self._generate_conftest()

    def _generate_conftest(self):
        """Generate conftest.py with environment variables and auth fixture."""
        conftest_content = [
            "import os",
            "import base64",
            "import pytest",
            "from dotenv import load_dotenv",
            "",
            "# Load environment variables",
            "load_dotenv()",
            "",
            "# Environment configuration",
            "ENV_URL = os.getenv('ENV_URL')",
            "TLS_VERIFY = os.getenv('TLS_VERIFY', 'true').lower() == 'true'",
            "",
            "# Auth configuration",
        ]
        
        if self.test_content_generator.auth_manager:
            conftest_content.extend([
                f'AUTH_TOKEN_URL = "{self.test_content_generator.auth_manager.oauth_token_url}"',
                f'BASIC_AUTH_USERNAME = "{self.test_content_generator.auth_manager.basic_auth_username}"',
                f'BASIC_AUTH_PASSWORD = "{self.test_content_generator.auth_manager.basic_auth_password}"',
            ])
        else:
            conftest_content.extend([
                "AUTH_TOKEN_URL = None",
                "BASIC_AUTH_USERNAME = None",
                "BASIC_AUTH_PASSWORD = None",
            ])

        conftest_content.extend([
            "",
            "@pytest.fixture(scope='session')",
            "def auth_session():",
            '    """Create authenticated session for requests."""',
            "    from requests_oauthlib import OAuth2Session",
            "    from oauthlib.oauth2 import BackendApplicationClient",
            "",
            "    # Allow insecure transport for testing",
            "    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'",
            "",
            "    # Create session with OAuth2",
            "    client = BackendApplicationClient(client_id=BASIC_AUTH_USERNAME)",
            "    session = OAuth2Session(client=client)",
            "",
            "    # Create Basic auth header for token request",
            "    auth_str = f'{BASIC_AUTH_USERNAME}:{BASIC_AUTH_PASSWORD}'",
            "    auth_bytes = auth_str.encode('ascii')",
            "    auth_header = base64.b64encode(auth_bytes).decode('ascii')",
            "",
            "    # Get token using client credentials grant",
            "    token = session.fetch_token(",
            "        token_url=AUTH_TOKEN_URL,",
            "        client_id=BASIC_AUTH_USERNAME,",
            "        client_secret=BASIC_AUTH_PASSWORD,",
            "        headers={'Authorization': f'Basic {auth_header}'},",
            "        verify=TLS_VERIFY",
            "    )",
            "",
            "    return session",
        ])

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write conftest.py
        conftest_path = self.output_dir / 'conftest.py'
        conftest_path.write_text('\n'.join(conftest_content))

    def _copy_env_file(self):
        """Copy .env file to output directory if it exists, or .env.sample if .env doesn't exist.
        Creates output directory if it doesn't exist."""
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Look for .env in project root first
        project_root = Path(__file__).parent.parent.parent
        src_env = project_root / '.env'
        src_env_sample = project_root / '.env.sample'
        
        # If not found in project root, try base_dir
        if not src_env.exists() and not src_env_sample.exists():
            src_env = self.base_dir / '.env'
            src_env_sample = self.base_dir / '.env.sample'
        
        dst_env = self.output_dir / '.env'

        if src_env.exists():
            shutil.copy2(src_env, dst_env)
        elif src_env_sample.exists():
            shutil.copy2(src_env_sample, dst_env)

    def generate_test_file(
        self,
        request_details: Dict[str, Any],
        dependencies: List[Dict[str, Any]],
        variables: Dict[str, List[str]],
    ) -> str:
        """Generate pytest file for request and its dependencies.

        Args:
            request_details: Dict with request information
            dependencies: List of dependency endpoint information
            variables: Dict mapping variables to setter endpoints

        Returns:
            Generated test file content
        """
        # Initialize uses list for request if not present
        if "uses" not in request_details:
            request_details["uses"] = []

        # Add only non-environment variables to request's uses list
        for var_name, setters in variables.items():
            # Check if variable is environment type in dependencies
            if var_name in request_details.get("uses_variables", {}) and \
               request_details["uses_variables"][var_name].get("type") != "environment":
                request_details["uses"].append((var_name, "dynamic"))

        # Initialize uses list for dependencies, excluding environment variables
        for dep in dependencies:
            if "uses" not in dep:
                dep["uses"] = []
            # Add only non-environment variables from uses_variables
            for var_name, var_info in dep.get("uses_variables", {}).items():
                if var_info.get("type") != "environment":
                    dep["uses"].append((var_name, "dynamic"))

        # Generate test content
        content = self.test_content_generator.generate_test_content(
            request_details,
            dependencies,
            variables,
            self.fixture_generator
        )

        # Create output directory structure matching request path
        test_name = self.test_content_generator.request_formatter._sanitize_name(request_details["name"])
        if request_details.get("path"):
            file_dir = self.output_dir.joinpath(*request_details["path"])
            file_dir.mkdir(parents=True, exist_ok=True)
            file_path = file_dir / f"test_{test_name}.py"
        else:
            file_path = self.output_dir / f"test_{test_name}.py"

        # Write test file
        file_path.write_text(content)

        return content
