"""
Tests for Postman collection parser.
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from src.parser.collection import PostmanCollectionParser


def test_load_collection(collection_file: Path):
    """Test loading valid collection file."""
    parser = PostmanCollectionParser(str(collection_file))
    assert parser.collection["info"]["name"] == "Sample API Collection"
    assert len(parser.collection["item"]) == 2


def test_load_invalid_collection(temp_dir: Path):
    """Test loading invalid collection file."""
    # Create invalid JSON file
    invalid_file = temp_dir / "invalid.json"
    invalid_file.write_text("{invalid json")

    with pytest.raises(ValueError):
        PostmanCollectionParser(str(invalid_file))


def test_get_request_by_name(collection_file: Path):
    """Test finding request by name."""
    parser = PostmanCollectionParser(str(collection_file))

    # Test finding nested request
    request = parser.get_request_by_name("Users/Get User")
    assert request is not None
    assert request["name"] == "Get User"
    assert request["path"] == ["Users"]
    assert request["request"]["method"] == "GET"

    # Test non-existent request
    assert parser.get_request_by_name("NonExistent") is None


def test_get_request_by_endpoint(collection_file: Path):
    """Test finding request by endpoint."""
    parser = PostmanCollectionParser(str(collection_file))

    # Test finding request by method and path
    request = parser.get_request_by_endpoint("POST", "/auth/login")
    assert request is not None
    assert request["name"] == "Login"
    assert request["path"] == ["Auth"]

    # Test non-existent endpoint
    assert parser.get_request_by_endpoint("GET", "/nonexistent") is None


def test_get_all_requests(collection_file: Path):
    """Test getting all requests."""
    parser = PostmanCollectionParser(str(collection_file))
    requests = parser.get_all_requests()

    # Should find all 3 requests
    assert len(requests) == 3

    # Verify request details
    names = {r["name"] for r in requests}
    assert names == {"Login", "Get User", "Create User"}


def test_folder_exclusion(collection_file: Path):
    """Test excluding folders from parsing."""
    parser = PostmanCollectionParser(str(collection_file), exclude_folders=["Auth"])
    requests = parser.get_all_requests()

    # Should only find requests not in Auth folder
    assert len(requests) == 2
    names = {r["name"] for r in requests}
    assert "Login" not in names


def test_extract_request_details(collection_file: Path):
    """Test extracting request details."""
    parser = PostmanCollectionParser(str(collection_file))
    request = parser.get_request_by_name("Users/Get User")

    # Verify URL parsing
    assert request["request"]["url"]["raw"].endswith("/users/{{user_id}}")

    # Verify headers
    headers = request["request"]["headers"]
    assert any(
        h["key"] == "Authorization" and "{{token}}" in h["value"] for h in headers
    )


def test_request_body_parsing(collection_file: Path):
    """Test parsing different request body types."""
    parser = PostmanCollectionParser(str(collection_file))

    # Test raw JSON body
    login = parser.get_request_by_name("Auth/Login")
    assert login["request"]["body"]["mode"] == "raw"
    assert "username" in login["request"]["body"]["raw"]

    # Test request without body
    get_user = parser.get_request_by_name("Users/Get User")
    assert "body" not in get_user["request"]
