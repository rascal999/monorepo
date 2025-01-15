"""
Tests for CLI functionality.
"""

import pytest
from pathlib import Path
from click.testing import CliRunner
from src.cli import main


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_collection(tmp_path: Path) -> Path:
    """Create sample Postman collection file."""
    collection = {
        "info": {
            "name": "Sample API Collection",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [
            {
                "name": "Auth",
                "item": [
                    {
                        "name": "Login",
                        "request": {
                            "method": "POST",
                            "url": {
                                "raw": "http://api.example.com/auth/login",
                                "path": ["auth", "login"],
                            },
                            "header": [],
                            "body": {
                                "mode": "raw",
                                "raw": '{"username": "test", "password": "test"}',
                            },
                        },
                    }
                ],
            },
            {
                "name": "Users",
                "item": [
                    {
                        "name": "Get User",
                        "request": {
                            "method": "GET",
                            "url": {
                                "raw": "http://api.example.com/users/{{user_id}}",
                                "path": ["users", "{{user_id}}"],
                            },
                            "header": [
                                {"key": "Authorization", "value": "Bearer {{token}}"}
                            ],
                        },
                    },
                    {
                        "name": "Create User",
                        "request": {
                            "method": "POST",
                            "url": {
                                "raw": "http://api.example.com/users",
                                "path": ["users"],
                            },
                            "header": [
                                {"key": "Authorization", "value": "Bearer {{token}}"}
                            ],
                            "body": {"mode": "raw", "raw": '{"name": "test"}'},
                        },
                    },
                ],
            },
        ],
    }
    collection_file = tmp_path / "collection.json"
    import json

    collection_file.write_text(json.dumps(collection))
    return collection_file


@pytest.fixture
def sample_dependencies(tmp_path: Path) -> Path:
    """Create sample dependencies file."""
    dependencies = {
        "postman_collection_dependencies": {
            "endpoints": {
                "GET /users/{{user_id}}": {
                    "uses_variables": {
                        "token": {"type": "dynamic", "set_by": ["POST /auth/login"]},
                        "user_id": {"type": "dynamic", "set_by": ["POST /users"]},
                    }
                },
                "POST /auth/login": {"sets_variables": ["token"], "uses_variables": {}},
                "POST /users": {
                    "sets_variables": ["user_id"],
                    "uses_variables": {
                        "token": {"type": "dynamic", "set_by": ["POST /auth/login"]}
                    },
                },
            }
        }
    }
    dependencies_file = tmp_path / "dependencies.yml"
    import yaml

    dependencies_file.write_text(yaml.dump(dependencies))
    return dependencies_file


def test_cli_basic(
    runner: CliRunner,
    tmp_path: Path,
    sample_collection: Path,
    sample_dependencies: Path,
):
    """Test basic CLI functionality."""
    output_dir = tmp_path / "generated_tests"
    output_dir.mkdir(exist_ok=True)

    # Create a sample .env file
    env_content = """
    OAUTH_TOKEN_URL=https://auth.example.com/token
    BASIC_AUTH_USERNAME=test_client
    BASIC_AUTH_PASSWORD=test_secret
    """
    (output_dir / ".env").write_text(env_content.strip())

    result = runner.invoke(
        main,
        [
            "--collection",
            str(sample_collection),
            "--dependencies",
            str(sample_dependencies),
            "--output",
            str(output_dir),
        ],
    )

    print("\nCLI Output:", result.output)  # Debug output
    print("\nCLI Exception:", result.exception)  # Debug output
    assert result.exit_code == 0, f"CLI failed with output: {result.output}"
    assert "Successfully generated test files" in result.output
    assert output_dir.exists()


def test_cli_target_endpoint(
    runner: CliRunner,
    tmp_path: Path,
    sample_collection: Path,
    sample_dependencies: Path,
):
    """Test CLI with target endpoint."""
    output_dir = tmp_path / "generated_tests"
    output_dir.mkdir(exist_ok=True)

    # Create a sample .env file
    env_content = """
    OAUTH_TOKEN_URL=https://auth.example.com/token
    BASIC_AUTH_USERNAME=test_client
    BASIC_AUTH_PASSWORD=test_secret
    """
    (output_dir / ".env").write_text(env_content.strip())

    result = runner.invoke(
        main,
        [
            "--collection",
            str(sample_collection),
            "--dependencies",
            str(sample_dependencies),
            "--output",
            str(output_dir),
            "--target",
            "GET /users/{{user_id}}",
        ],
    )

    print("\nCLI Output:", result.output)  # Debug output
    print("\nCLI Exception:", result.exception)  # Debug output
    assert result.exit_code == 0, f"CLI failed with output: {result.output}"
    assert "Successfully generated test files" in result.output
    assert output_dir.exists()


def test_cli_target_name(
    runner: CliRunner,
    tmp_path: Path,
    sample_collection: Path,
    sample_dependencies: Path,
):
    """Test CLI with target name."""
    output_dir = tmp_path / "generated_tests"
    output_dir.mkdir(exist_ok=True)

    # Create a sample .env file
    env_content = """
    OAUTH_TOKEN_URL=https://auth.example.com/token
    BASIC_AUTH_USERNAME=test_client
    BASIC_AUTH_PASSWORD=test_secret
    """
    (output_dir / ".env").write_text(env_content.strip())

    result = runner.invoke(
        main,
        [
            "--collection",
            str(sample_collection),
            "--dependencies",
            str(sample_dependencies),
            "--output",
            str(output_dir),
            "--name",
            "Users/Get User",
        ],
    )

    assert result.exit_code == 0
    assert "Successfully generated test files" in result.output
    assert output_dir.exists()


def test_cli_folder_exclusions(
    runner: CliRunner,
    tmp_path: Path,
    sample_collection: Path,
    sample_dependencies: Path,
):
    """Test CLI with folder exclusions."""
    output_dir = tmp_path / "generated_tests"
    output_dir.mkdir(exist_ok=True)

    # Create a sample .env file
    env_content = """
    OAUTH_TOKEN_URL=https://auth.example.com/token
    BASIC_AUTH_USERNAME=test_client
    BASIC_AUTH_PASSWORD=test_secret
    """
    (output_dir / ".env").write_text(env_content.strip())

    result = runner.invoke(
        main,
        [
            "--collection",
            str(sample_collection),
            "--dependencies",
            str(sample_dependencies),
            "--output",
            str(output_dir),
            "--exclude-collection-folder",
            "Auth",
            "--exclude-dependency-folder",
            "Tutorials",
        ],
    )

    assert result.exit_code == 0
    assert "Successfully generated test files" in result.output
    assert output_dir.exists()


def test_cli_missing_files(runner: CliRunner, tmp_path: Path):
    """Test CLI with missing input files."""
    output_dir = tmp_path / "generated_tests"

    result = runner.invoke(
        main,
        [
            "--collection",
            "nonexistent.json",
            "--dependencies",
            "nonexistent.yml",
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Error" in result.output


def test_cli_invalid_target(
    runner: CliRunner,
    tmp_path: Path,
    sample_collection: Path,
    sample_dependencies: Path,
):
    """Test CLI with invalid target format."""
    output_dir = tmp_path / "generated_tests"

    result = runner.invoke(
        main,
        [
            "--collection",
            str(sample_collection),
            "--dependencies",
            str(sample_dependencies),
            "--output",
            str(output_dir),
            "--target",
            "INVALID FORMAT",
        ],
    )

    assert result.exit_code == 1
    assert "Error" in result.output


def test_cli_both_target_options(
    runner: CliRunner,
    tmp_path: Path,
    sample_collection: Path,
    sample_dependencies: Path,
):
    """Test CLI with both target options specified."""
    output_dir = tmp_path / "generated_tests"

    result = runner.invoke(
        main,
        [
            "--collection",
            str(sample_collection),
            "--dependencies",
            str(sample_dependencies),
            "--output",
            str(output_dir),
            "--target",
            "GET /users/{{user_id}}",
            "--name",
            "Users/Get User",
        ],
    )

    assert result.exit_code == 1
    assert "Error" in result.output
    assert "Cannot specify both" in result.output
