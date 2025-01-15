"""
Tests for request formatting functionality.
"""

import pytest
from src.generator.request_formatter import RequestFormatter


def test_sanitize_name():
    """Test sanitizing names for Python identifiers."""
    formatter = RequestFormatter()
    
    # Test basic conversion
    assert formatter._sanitize_name("Get User") == "test_get_user"

    # Test with special characters
    assert formatter._sanitize_name("Create User (v2)") == "test_create_user_v2"

    # Test with leading number
    assert formatter._sanitize_name("2FA Setup") == "test_2fa_setup"


@pytest.fixture(autouse=True)
def setup_env():
    """Setup test environment variables."""
    import os
    os.environ["ENV_URL"] = "http://api.example.com"
    os.environ["CLIENT_ID"] = "test_client"
    os.environ["USER_LEGAL_OWNER"] = "test_user"
    yield
    del os.environ["ENV_URL"]
    del os.environ["CLIENT_ID"]
    del os.environ["USER_LEGAL_OWNER"]


def test_format_request_details():
    """Test formatting request details as Python code."""
    formatter = RequestFormatter()
    request = {
        "method": "POST",
        "url": {"raw": "/users", "path": ["users"]},
        "header": [
            {"key": "Content-Type", "value": "application/json"},
            {"key": "Authorization", "value": "Bearer {{token}}"},
        ],
        "body": {"mode": "raw", "raw": '{"name": "test"}'},
    }

    lines = formatter.format_request_details(request)

    # Verify method
    assert any('method = "POST"' in line for line in lines)

    # Verify URL formatting with env_url
    assert any('url = f"{env_url}/users"' in line for line in lines)

    # Verify headers formatting
    headers_line = next(line for line in lines if "headers =" in line)
    assert '"Content-Type": "application/json"' in headers_line
    assert '"Authorization": "Bearer {{token}}"' in headers_line

    # Verify body formatting
    body_line = next(line for line in lines if "data =" in line)
    assert '{"name": "test"}' in body_line


def test_url_formatting_with_variables():
    """Test URL formatting with empty segments and variable placeholders."""
    formatter = RequestFormatter()
    
    # Test dictionary URL with empty segments and variables
    request_dict = {
        "method": "GET",
        "url": {
            "raw": "/v2.01//{{CLIENT_ID}}/users/{{USER_LEGAL_OWNER}}",
            "path": ["v2.01", "", "{{CLIENT_ID}}", "users", "{{USER_LEGAL_OWNER}}"]
        }
    }
    
    lines = formatter.format_request_details(request_dict)
    url_line = next(line for line in lines if "url =" in line)
    assert 'url = f"{env_url}/v2.01/{CLIENT_ID}/users/{USER_LEGAL_OWNER}"' in url_line

    # Test string URL with empty segments and variables
    request_str = {
        "method": "GET",
        "url": "/v2.01//{{CLIENT_ID}}//users/{{USER_LEGAL_OWNER}}"
    }
    
    lines = formatter.format_request_details(request_str)
    url_line = next(line for line in lines if "url =" in line)
    assert 'url = f"{env_url}/v2.01/{CLIENT_ID}/users/{USER_LEGAL_OWNER}"' in url_line

def test_url_formatting_with_env_url():
    """Test URL formatting with ENV_URL variable."""
    formatter = RequestFormatter()
    
    # Test with ENV_URL in the raw URL
    request = {
        "method": "GET",
        "url": {
            "raw": "{{ENV_URL}}/v2.01/{{CLIENT_ID}}/users",
        }
    }
    
    lines = formatter.format_request_details(request)
    url_line = next(line for line in lines if "url =" in line)
    assert 'url = f"{env_url}/v2.01/{CLIENT_ID}/users"' in url_line

def test_url_formatting_with_absolute_url():
    """Test URL formatting with absolute URLs."""
    formatter = RequestFormatter()
    
    # Test with absolute URL
    request = {
        "method": "GET",
        "url": {
            "raw": "https://api.example.com/v2.01/{{CLIENT_ID}}/users",
        }
    }
    
    lines = formatter.format_request_details(request)
    url_line = next(line for line in lines if "url =" in line)
    assert 'url = "https://api.example.com/v2.01/{{CLIENT_ID}}/users"' in url_line
