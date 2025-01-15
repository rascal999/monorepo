#!/usr/bin/env python3
"""
Postman to Pytest Generator
Generates pytest files from Postman collections using dependency information.
"""

import sys
import click
import yaml
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from .parser.collection import PostmanCollectionParser
from .parser.dependency import DependencyGraphParser
from .generator.fixtures import FixtureGenerator
from .generator.test_file import TestFileGenerator
from .utils.validation import validate_inputs, validate_endpoint_format
from .utils.auth import AuthManager


class PostmanToPytestGenerator:
    def __init__(
        self,
        collection_path: str,
        dependencies_path: str,
        output_dir: str,
        target: Optional[str] = None,
        name: Optional[str] = None,
        exclude_collection_folders: Optional[List[str]] = None,
        exclude_dependency_folders: Optional[List[str]] = None,
    ) -> None:
        """Initialize the generator with input files and options.

        Args:
            collection_path: Path to Postman collection JSON file
            dependencies_path: Path to dependency graph YAML file
            output_dir: Directory to write generated tests to
            target: Optional target endpoint in format "HTTP_METHOD PATH"
            name: Optional target using Postman folder/test name
            exclude_collection_folders: Collection folders to exclude
            exclude_dependency_folders: Dependency folders to exclude
        """
        self.collection_path = collection_path
        self.dependencies_path = dependencies_path
        self.output_dir = output_dir
        self.target = target
        self.name = name
        self.exclude_collection_folders = exclude_collection_folders or []
        self.exclude_dependency_folders = exclude_dependency_folders or []

        # Validate inputs
        validate_inputs(
            collection_path=collection_path,
            dependencies_path=dependencies_path,
            output_dir=output_dir,
            target=target,
            name=name,
            exclude_collection_folders=self.exclude_collection_folders,
            exclude_dependency_folders=self.exclude_dependency_folders,
        )

        # Initialize auth manager
        self.auth_manager = AuthManager()

        # Initialize parsers
        self.collection_parser = PostmanCollectionParser(
            collection_path=collection_path,
            exclude_folders=self.exclude_collection_folders
        )
        self.dependency_parser = DependencyGraphParser(
            dependency_file=self.dependencies_path,
            exclude_folders=self.exclude_dependency_folders,
        )

    def _resolve_target(self) -> Optional[Dict[str, Any]]:
        """Resolve target endpoint from options.

        Returns:
            Request details if target specified, None otherwise
        """
        if self.target:
            # Validate target format
            validate_endpoint_format(self.target)
            # Split target into method and path
            method, path = self.target.split(" ", 1)
            # Get request by endpoint
            return self.collection_parser.get_request_by_endpoint(method, path)
        elif self.name:
            # Get request by name
            return self.collection_parser.get_request_by_name(self.name)
        else:
            # No target specified, return None to process all endpoints
            return None

    def generate(self) -> None:
        """Generate pytest files from Postman collection."""
        # Resolve target endpoint
        target = self._resolve_target()

        # Get requests to process
        if target:
            requests = [target]
        else:
            requests = self.collection_parser.get_all_requests()

        # Create fixture generator
        fixture_generator = FixtureGenerator()

        # Create test file generator
        test_generator = TestFileGenerator(
            output_dir=self.output_dir,
            fixture_generator=fixture_generator,
            auth_manager=self.auth_manager,
        )

        # Process each request
        for request in requests:
            # Get dependencies for this request
            # Extract endpoint from request
            method = request["request"]["method"]
            url = request["request"]["url"]["raw"]
            endpoint = f"{method} {url}"
            dependencies = self.dependency_parser.get_endpoint_dependencies(endpoint)

            # Get variable dependencies
            variables = self.dependency_parser.get_variable_dependencies(endpoint)

            # Generate test file
            test_generator.generate_test_file(
                request_details=request,
                dependencies=dependencies,
                variables=variables,
            )

        click.echo(f"Successfully generated test files in {self.output_dir}")


@click.command()
@click.option(
    "--collection", required=True, help="Path to Postman collection JSON file"
)
@click.option(
    "--dependencies", required=True, help="Path to dependency graph YAML file"
)
@click.option(
    "--output", default="generated_tests", help="Output directory for generated tests"
)
@click.option("--target", help='Target endpoint in format "HTTP_METHOD PATH"')
@click.option("--name", help="Target using Postman folder/test name")
@click.option(
    "--exclude-collection-folder", multiple=True, help="Collection folders to exclude"
)
@click.option(
    "--exclude-dependency-folder", multiple=True, help="Dependency folders to exclude"
)
def main(
    collection: str,
    dependencies: str,
    output: str,
    target: Optional[str],
    name: Optional[str],
    exclude_collection_folder: tuple,
    exclude_dependency_folder: tuple,
) -> None:
    """Generate pytest files from Postman collection using dependency information."""
    try:
        generator = PostmanToPytestGenerator(
            collection_path=collection,
            dependencies_path=dependencies,
            output_dir=output,
            target=target,
            name=name,
            exclude_collection_folders=list(exclude_collection_folder),
            exclude_dependency_folders=list(exclude_dependency_folder),
        )
        generator.generate()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
