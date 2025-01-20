"""
Tests for input validation utilities.
"""

import pytest
from pathlib import Path
from src.utils.validation import validate_inputs, validate_endpoint_format


def test_validate_inputs_valid(temp_dir: Path):
    """Test validation with valid inputs."""
    # Create test files
    collection = temp_dir / "collection.json"
    collection.write_text("{}")

    dependencies = temp_dir / "deps.yml"
    dependencies.write_text("postman_collection_dependencies: {}")

    # Should not raise any exceptions
    validate_inputs(
        collection_path=str(collection),
        dependencies_path=str(dependencies),
        output_dir=str(temp_dir),
        target="GET /api/users",
        exclude_collection_folders=["auth"],
        exclude_dependency_folders=["examples"],
    )


def test_validate_inputs_missing_files(temp_dir: Path):
    """Test validation with missing files."""
    with pytest.raises(FileNotFoundError, match="Collection file not found"):
        validate_inputs(
            collection_path=str(temp_dir / "missing.json"),
            dependencies_path=str(temp_dir / "deps.yml"),
            output_dir=str(temp_dir),
        )


def test_validate_inputs_wrong_extensions(temp_dir: Path):
    """Test validation with wrong file extensions."""
    # Create files with wrong extensions
    collection = temp_dir / "collection.txt"
    collection.write_text("{}")

    dependencies = temp_dir / "deps.txt"
    dependencies.write_text("content")

    with pytest.raises(ValueError, match="Collection file must be JSON"):
        validate_inputs(
            collection_path=str(collection),
            dependencies_path=str(dependencies),
            output_dir=str(temp_dir),
        )

    # Create JSON file and test YAML validation
    collection = temp_dir / "collection.json"
    collection.write_text("{}")

    with pytest.raises(ValueError, match="Dependencies file must be YAML"):
        validate_inputs(
            collection_path=str(collection),
            dependencies_path=str(dependencies),
            output_dir=str(temp_dir),
        )


def test_validate_inputs_target_conflict(temp_dir: Path):
    """Test validation with conflicting target specifications."""
    # Create required files
    collection = temp_dir / "collection.json"
    collection.write_text("{}")

    dependencies = temp_dir / "deps.yml"
    dependencies.write_text("content")

    with pytest.raises(ValueError, match="Cannot specify both --target and --name"):
        validate_inputs(
            collection_path=str(collection),
            dependencies_path=str(dependencies),
            output_dir=str(temp_dir),
            target="GET /api/users",
            name="Get User",
        )


def test_validate_inputs_empty_exclusions(temp_dir: Path):
    """Test validation with empty folder exclusions."""
    # Create required files
    collection = temp_dir / "collection.json"
    collection.write_text("{}")

    dependencies = temp_dir / "deps.yml"
    dependencies.write_text("content")

    with pytest.raises(ValueError, match="Empty collection folder name"):
        validate_inputs(
            collection_path=str(collection),
            dependencies_path=str(dependencies),
            output_dir=str(temp_dir),
            exclude_collection_folders=["auth", ""],
        )

    with pytest.raises(ValueError, match="Empty dependency folder name"):
        validate_inputs(
            collection_path=str(collection),
            dependencies_path=str(dependencies),
            output_dir=str(temp_dir),
            exclude_dependency_folders=["", "examples"],
        )


def test_validate_endpoint_format_valid():
    """Test endpoint format validation with valid inputs."""
    # Test various valid formats
    validate_endpoint_format("GET /api/users")
    validate_endpoint_format("POST /auth/login")
    validate_endpoint_format("PUT /users/{id}")
    validate_endpoint_format("DELETE /items/123?force=true")


def test_validate_endpoint_format_invalid():
    """Test endpoint format validation with invalid inputs."""
    # Test missing space
    with pytest.raises(ValueError, match="Invalid endpoint format"):
        validate_endpoint_format("GET/api/users")

    # Test invalid method
    with pytest.raises(ValueError, match="Invalid HTTP method"):
        validate_endpoint_format("INVALID /api/users")

    # Test missing leading slash
    with pytest.raises(ValueError, match="Path must start with /"):
        validate_endpoint_format("GET api/users")

    # Test invalid characters
    with pytest.raises(ValueError, match="Invalid characters in path"):
        validate_endpoint_format("GET /api/users<script>")


def test_validate_endpoint_format_methods():
    """Test endpoint format validation with different HTTP methods."""
    valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

    for method in valid_methods:
        # Should not raise any exceptions
        validate_endpoint_format(f"{method} /api/test")

        # Should work with lowercase too
        validate_endpoint_format(f"{method.lower()} /api/test")

    # Test invalid method
    with pytest.raises(ValueError, match="Invalid HTTP method"):
        validate_endpoint_format("CUSTOM /api/test")


def test_validate_endpoint_format_paths():
    """Test endpoint format validation with different path formats."""
    # Test nested paths
    validate_endpoint_format("GET /api/v1/users/active")

    # Test path parameters
    validate_endpoint_format("GET /users/{id}/posts/{post_id}")

    # Test query parameters
    validate_endpoint_format("GET /search?q=test&page=1")

    # Test with allowed special characters
    validate_endpoint_format("GET /api/users-and-groups")
    validate_endpoint_format("GET /api/user_profiles")

    # Test invalid paths
    with pytest.raises(ValueError, match="Invalid characters in path"):
        validate_endpoint_format("GET /api/users\\posts")  # backslash

    with pytest.raises(ValueError, match="Invalid characters in path"):
        validate_endpoint_format('GET /api/users"')  # quote
