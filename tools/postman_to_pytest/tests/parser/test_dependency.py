"""
Tests for dependency graph parser.
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from src.parser.dependency import DependencyGraphParser


def test_load_dependencies(dependencies_file: Path):
    """Test loading valid dependency file."""
    parser = DependencyGraphParser(str(dependencies_file))
    assert len(parser.dependencies) == 3
    assert "POST /auth/login" in parser.dependencies


def test_load_invalid_dependencies(temp_dir: Path):
    """Test loading invalid dependency file."""
    # Create invalid YAML file
    invalid_file = temp_dir / "invalid.yml"
    invalid_file.write_text("invalid: [yaml: content")

    with pytest.raises(ValueError):
        DependencyGraphParser(str(invalid_file))


def test_get_endpoint_dependencies(dependencies_file: Path):
    """Test getting dependencies for specific endpoint."""
    parser = DependencyGraphParser(str(dependencies_file))

    # Test endpoint with dependencies
    deps = parser.get_endpoint_dependencies("GET /users/{{user_id}}")
    assert len(deps) > 0
    dep = next(d for d in deps if d["endpoint"] == "POST /auth/login")
    assert "uses_variables" in dep
    assert "token" in dep["sets"]

    # Test endpoint without dependencies
    deps = parser.get_endpoint_dependencies("POST /auth/login")
    assert len(deps) == 0

    # Test non-existent endpoint
    deps = parser.get_endpoint_dependencies("GET /nonexistent")
    assert len(deps) == 0


def test_get_variable_dependencies(dependencies_file: Path):
    """Test getting variable dependencies for endpoint."""
    parser = DependencyGraphParser(str(dependencies_file))

    # Test endpoint using variables
    vars = parser.get_variable_dependencies("GET /users/{{user_id}}")
    assert "token" in vars
    assert "user_id" in vars
    assert vars["token"] == ["POST /auth/login"]
    assert vars["user_id"] == ["POST /users"]

    # Test endpoint not using variables
    vars = parser.get_variable_dependencies("POST /auth/login")
    assert not vars


def test_build_dependency_chain(dependencies_file: Path):
    """Test building complete dependency chain."""
    parser = DependencyGraphParser(str(dependencies_file))

    # Test chain for endpoint with multiple dependencies
    chain = parser.build_dependency_chain("GET /users/{{user_id}}")

    # Chain should include login (for token) and create user (for user_id)
    endpoints = [info["endpoint"] for info in chain]
    assert "POST /auth/login" in endpoints
    assert "POST /users" in endpoints
    assert "GET /users/{{user_id}}" in endpoints

    # Verify order (login before create user, both before get user)
    login_idx = endpoints.index("POST /auth/login")
    create_idx = endpoints.index("POST /users")
    get_idx = endpoints.index("GET /users/{{user_id}}")
    assert login_idx < get_idx
    assert create_idx < get_idx


def test_folder_exclusion(dependencies_file: Path):
    """Test excluding folders from dependency chain."""
    parser = DependencyGraphParser(str(dependencies_file), exclude_folders=["auth"])

    # Get chain for endpoint that depends on excluded auth endpoint
    chain = parser.build_dependency_chain("GET /users/{{user_id}}")

    # Chain should not include auth endpoints
    endpoints = [info["endpoint"] for info in chain]
    assert "POST /auth/login" not in endpoints


def test_get_all_endpoints(dependencies_file: Path):
    """Test getting all endpoints."""
    parser = DependencyGraphParser(str(dependencies_file))
    endpoints = parser.get_all_endpoints()

    # Should find all endpoints
    assert len(endpoints) == 3
    assert "POST /auth/login" in endpoints
    assert "GET /users/{{user_id}}" in endpoints
    assert "POST /users" in endpoints

    # Test with exclusions
    parser = DependencyGraphParser(str(dependencies_file), exclude_folders=["auth"])
    endpoints = parser.get_all_endpoints()
    assert "POST /auth/login" not in endpoints
