"""
Generator for pytest test files from Postman requests.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from src.generator.fixtures import FixtureGenerator
from src.generator.test_content import TestContentGenerator


class TestFileGenerator:
    """Generates pytest test files from Postman requests."""

    def __init__(
        self,
        output_dir: str,
        fixture_generator: FixtureGenerator,
        base_dir: Optional[str] = None,
        auth_manager: Optional[Any] = None,
    ):
        """Initialize test file generator.

        Args:
            output_dir: Output directory for generated tests
            fixture_generator: Generator for test fixtures
            base_dir: Base directory for finding .env files
            auth_manager: Optional auth manager for OAuth configuration
        """
        self.output_dir = output_dir
        self.fixture_generator = fixture_generator
        self.base_dir = base_dir or os.getcwd()
        self.auth_manager = auth_manager

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Copy environment file
        self._copy_env_file()

        # Generate conftest.py
        self._generate_conftest()

    def _copy_env_file(self) -> None:
        """Copy environment file to output directory.
        
        Looks for .env file in the following order:
        1. Project root directory
        2. Current/base directory
        3. .env.sample from project root
        """
        output_path = Path(self.output_dir) / ".env"
        
        # Try project root .env
        project_root = Path(self.base_dir).parent
        print(f"Project root: {project_root}")
        root_env = project_root / ".env"
        print(f"Root .env exists: {root_env.exists()}")
        if root_env.exists():
            content = root_env.read_text()
            print(f"Root env content: {content}")
            output_path.write_text(content)
            print(f"Output env content after write: {output_path.read_text()}")
            return

        # Try current/base directory .env
        base_env = Path(self.base_dir) / ".env"
        print(f"Base .env exists: {base_env.exists()}")
        if base_env.exists():
            content = base_env.read_text()
            print(f"Base env content: {content}")
            output_path.write_text(content)
            print(f"Output env content after write: {output_path.read_text()}")
            return

        # Try .env.sample from project root
        sample_env = project_root / ".env.sample"
        print(f"Sample .env exists: {sample_env.exists()}")
        if sample_env.exists():
            print(f"Reading sample content from: {sample_env}")
            sample_content = sample_env.read_text()
            print(f"Sample content: {sample_content}")
            print(f"Writing to output path: {output_path}")
            output_path.write_text(sample_content)
            print(f"Verifying content...")
            written_content = output_path.read_text()
            print(f"Written content: {written_content}")
            print(f"Output env content after write: {output_path.read_text()}")
            assert written_content == sample_content, f"Content mismatch. Expected: {sample_content}, Got: {written_content}"
            return

        print("No env files found, not creating default template")

    def _generate_conftest(self) -> None:
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

        # Add auth configuration
        lines.extend([
            'AUTH_TOKEN_URL = os.getenv("OAUTH_TOKEN_URL")',
            'BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME")',
            'BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD")',
            "",
            "# Validate required auth configuration",
            "if not all([BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD, AUTH_TOKEN_URL]):",
            '    pytest.skip("Missing required environment variables for authentication")',
        ])

        # Add auth session fixture
        lines.extend([
            "",
            "@pytest.fixture(scope='session')",
            "def auth_session(tls_verify):",
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
            "            verify=tls_verify",
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

    def _initialize_variables(
        self,
        request: Dict[str, Any],
        dependencies: List[Dict[str, Any]],
    ) -> None:
        """Initialize variable lists for request and dependencies.

        Args:
            request: Request details
            dependencies: List of dependent requests
        """
        # Initialize uses list if not present
        if "uses" not in request:
            request["uses"] = []

        # Add dynamic variables to request uses
        if "uses_variables" in request:
            for var_name, var_info in request["uses_variables"].items():
                if isinstance(var_info, dict) and var_info.get("type") == "dynamic":
                    request["uses"].append((var_name, "dynamic"))

        # Initialize dependency uses lists
        for dep in dependencies:
            if "uses" not in dep:
                dep["uses"] = []
            if "uses_variables" in dep:
                for var_name, var_info in dep["uses_variables"].items():
                    if isinstance(var_info, dict) and var_info.get("type") == "dynamic":
                        dep["uses"].append((var_name, "dynamic"))

    def generate_test_file(
        self,
        request_details: Dict[str, Any],
        dependencies: List[Dict[str, Any]],
        variables: Dict[str, List[str]],
    ) -> str:
        """Generate test file for request.

        Args:
            request_details: Request details
            dependencies: List of dependent requests
            variables: Variable dependency mapping

        Returns:
            Generated test file content
        """
        # Initialize variables
        self._initialize_variables(request_details, dependencies)

        # Create test directory structure
        if "path" in request_details:
            test_dir = Path(self.output_dir)
            for part in request_details["path"]:
                test_dir = test_dir / part
            test_dir.mkdir(parents=True, exist_ok=True)

        # Generate test content
        # Create default auth manager if none provided
        auth_manager = self.auth_manager or type(
            "DefaultAuthManager",
            (),
            {
                "oauth_token_url": "https://api.example.com/oauth/token",
                "basic_auth_username": "test_client",
                "basic_auth_password": "test_secret",
            },
        )()
        content_generator = TestContentGenerator(auth_manager)
        content = content_generator.generate_test_content(
            request_details=request_details,
            dependencies=dependencies,
            variables=variables,
            fixture_generator=self.fixture_generator,
        )

        # Create test file path
        if "path" in request_details:
            test_dir = Path(self.output_dir)
            for part in request_details["path"]:
                test_dir = test_dir / part
            test_file = test_dir / f"test_{request_details['name'].lower().replace(' ', '_')}.py"
        else:
            # Default to test_api.py if no path specified
            test_file = Path(self.output_dir) / "test_api.py"
            
        # Write test content to file
        test_file.write_text(content)
        return content
