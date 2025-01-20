"""
Input validation utilities.
"""

import re
from pathlib import Path
from typing import Optional, List


def validate_inputs(
    collection_path: str,
    dependencies_path: str,
    output_dir: str,
    target: Optional[str] = None,
    name: Optional[str] = None,
    exclude_collection_folders: Optional[List[str]] = None,
    exclude_dependency_folders: Optional[List[str]] = None,
) -> None:
    """Validate all input parameters.

    Args:
        collection_path: Path to Postman collection JSON
        dependencies_path: Path to dependency graph YAML
        output_dir: Output directory path
        target: Optional target endpoint
        name: Optional target name
        exclude_collection_folders: Collection folders to exclude
        exclude_dependency_folders: Dependency folders to exclude

    Raises:
        ValueError: If any validation fails
        FileNotFoundError: If required files don't exist
    """
    # Check input files exist
    if not Path(collection_path).exists():
        raise FileNotFoundError(f"Collection file not found: {collection_path}")
    if not Path(dependencies_path).exists():
        raise FileNotFoundError(f"Dependencies file not found: {dependencies_path}")

    # Check file extensions
    if not collection_path.lower().endswith(".json"):
        raise ValueError("Collection file must be JSON")
    if not dependencies_path.lower().endswith((".yml", ".yaml")):
        raise ValueError("Dependencies file must be YAML")

    # Validate target specification
    if target and name:
        raise ValueError("Cannot specify both --target and --name")

    if target:
        validate_endpoint_format(target)

    # Validate folder exclusions
    if exclude_collection_folders:
        for folder in exclude_collection_folders:
            if not folder.strip():
                raise ValueError("Empty collection folder name in exclusions")

    if exclude_dependency_folders:
        for folder in exclude_dependency_folders:
            if not folder.strip():
                raise ValueError("Empty dependency folder name in exclusions")


def validate_endpoint_format(endpoint: str) -> None:
    """Validate endpoint format (METHOD PATH).

    Args:
        endpoint: Endpoint string to validate

    Raises:
        ValueError: If format is invalid
    """
    # Check basic format
    if " " not in endpoint:
        raise ValueError(
            'Invalid endpoint format. Must be "METHOD PATH" (e.g. "GET /api/users")'
        )

    # Split and validate parts
    method, path = endpoint.split(" ", 1)

    # Validate HTTP method
    valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
    if method.upper() not in valid_methods:
        raise ValueError(
            f"Invalid HTTP method: {method}. Must be one of: {', '.join(valid_methods)}"
        )

    # Validate path format
    if not path.startswith("/"):
        raise ValueError("Path must start with /")

    # Basic path validation (alphanumeric, -, _, /, and common special chars)
    if not re.match(r"^[a-zA-Z0-9\-_/{}?&=.]+$", path):
        raise ValueError(
            "Invalid characters in path. Must contain only alphanumeric, -, _, /, {}, ?, &, =, ."
        )
