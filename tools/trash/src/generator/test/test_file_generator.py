"""Test file generation utilities."""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.generator.handlers.fixtures import FixtureGenerator
from .content_generator import ContentGenerator
from .env_handler import EnvHandler
from .conftest_generator import ConftestGenerator
from .variable_initializer import VariableInitializer


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

        # Initialize components
        self.env_handler = EnvHandler(output_dir, base_dir)
        self.conftest_generator = ConftestGenerator(output_dir, auth_manager)
        self.variable_initializer = VariableInitializer(fixture_generator)

        # Set up initial files
        self.env_handler.copy_env_file()
        self.conftest_generator.generate()

    def generate_test_file(
        self,
        request_details: Dict[str, Any],
        dependencies: List[Dict[str, Any]],
        variables: Dict[str, List[str]],
        include_method_in_name: bool = False,
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
        self.variable_initializer.initialize_variables(request_details, dependencies)

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
        content_generator = ContentGenerator(auth_manager)
        content = content_generator.generate_test_content(
            request_details=request_details,
            dependencies=dependencies,
            variables=variables,
            fixture_generator=self.fixture_generator,
            include_method_in_name=include_method_in_name,
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
