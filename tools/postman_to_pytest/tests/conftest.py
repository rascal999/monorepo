"""
Shared test fixtures and configuration.
"""

import os
import json
import pytest
from pathlib import Path
from typing import Dict, Any


@pytest.fixture
def sample_collection() -> Dict[str, Any]:
    """Sample Postman collection data."""
    return {
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
                            "body": {
                                "mode": "raw",
                                "raw": '{"username": "test", "password": "password"}',
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
                            "body": {
                                "mode": "raw",
                                "raw": '{"name": "Test User", "email": "test@example.com"}',
                            },
                        },
                    },
                ],
            },
        ],
    }


@pytest.fixture
def sample_dependencies() -> Dict[str, Any]:
    """Sample dependency graph data."""
    return {
        "postman_collection_dependencies": {
            "endpoints": {
                "POST /auth/login": {"sets_variables": ["token"], "uses_variables": {}},
                "GET /users/{{user_id}}": {
                    "uses_variables": {
                        "token": {"type": "dynamic", "set_by": ["POST /auth/login"]},
                        "user_id": {"type": "dynamic", "set_by": ["POST /users"]},
                    }
                },
                "POST /users": {
                    "sets_variables": ["user_id"],
                    "uses_variables": {
                        "token": {"type": "dynamic", "set_by": ["POST /auth/login"]}
                    },
                },
            }
        }
    }


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Temporary directory for test files."""
    return tmp_path


@pytest.fixture
def collection_file(temp_dir: Path, sample_collection: Dict[str, Any]) -> Path:
    """Create temporary collection JSON file."""
    file_path = temp_dir / "collection.json"
    with open(file_path, "w") as f:
        json.dump(sample_collection, f, indent=2)
    return file_path


@pytest.fixture
def dependencies_file(temp_dir: Path, sample_dependencies: Dict[str, Any]) -> Path:
    """Create temporary dependencies YAML file."""
    file_path = temp_dir / "dependencies.yml"
    import yaml

    with open(file_path, "w") as f:
        yaml.dump(sample_dependencies, f)
    return file_path


@pytest.fixture
def output_dir(temp_dir: Path) -> Path:
    """Create temporary output directory."""
    output = temp_dir / "generated_tests"
    output.mkdir(exist_ok=True)
    return output
