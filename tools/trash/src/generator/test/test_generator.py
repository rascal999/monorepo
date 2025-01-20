"""Test generation coordinator."""

import os
from typing import Dict, Any, List, Optional

from src.generator.handlers.fixtures import FixtureGenerator
from .test_file_generator import TestFileGenerator


class TestGenerator:
    """Coordinates test generation components."""

    def __init__(
        self,
        output_dir: str,
        base_dir: Optional[str] = None,
        auth_manager: Optional[Any] = None,
    ):
        """Initialize test generator.

        Args:
            output_dir: Output directory for generated tests
            base_dir: Base directory for finding .env files
            auth_manager: Optional auth manager for OAuth configuration
        """
        self.output_dir = output_dir
        self.base_dir = base_dir or os.getcwd()
        self.auth_manager = auth_manager

        # Create fixture generator
        self.fixture_generator = FixtureGenerator()

        # Create test file generator
        self.test_file_generator = TestFileGenerator(
            output_dir=output_dir,
            fixture_generator=self.fixture_generator,
            base_dir=base_dir,
            auth_manager=auth_manager,
        )

    def generate_tests(
        self,
        request_details: Dict[str, Any],
        dependencies: List[Dict[str, Any]],
        variables: Dict[str, List[str]],
    ) -> None:
        """Generate test files from request details.

        Args:
            request_details: Request details
            dependencies: List of dependent requests
            variables: Variable dependency mapping
        """
        self.test_file_generator.generate_test_file(
            request_details=request_details,
            dependencies=dependencies,
            variables=variables,
        )
