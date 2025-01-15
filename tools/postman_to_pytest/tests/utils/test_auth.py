"""Tests for authentication and environment configuration utilities."""

import os
import pytest
from unittest.mock import patch, mock_open, MagicMock
from src.utils.auth import AuthManager


@pytest.fixture
def mock_env():
    """Mock environment variables."""
    env_vars = {
        "TESTING": "true",  # Enable test mode
        "BASIC_AUTH_USERNAME": "test_user",
        "BASIC_AUTH_PASSWORD": "test_pass",
        "OAUTH_TOKEN_URL": "https://api.test.com/oauth/token",
        "OAUTH_SCOPE": "read write",
        "AUTH_HEADER": "Authorization",
        "AUTH_TOKEN_FILE": ".test_token",
        "HTTP_PROXY": "http://proxy.test:8080",
        "HTTPS_PROXY": "https://proxy.test:8080",
        "NO_PROXY": "localhost,127.0.0.1",
        "PROXY_USERNAME": "proxy_user",
        "PROXY_PASSWORD": "proxy_pass",
        "CERT_PATH": "/path/to/cert.pem",
        "TLS_VERIFY": "true",
        "ENV_URL": "https://api.test.com",
        "ENV_NAME": "test",
    }
    with patch.dict("os.environ", env_vars, clear=True):
        yield env_vars


def test_auth_manager_init(mock_env):
    """Test AuthManager initialization."""
    auth = AuthManager()

    assert auth.basic_auth_username == mock_env["BASIC_AUTH_USERNAME"]
    assert auth.basic_auth_password == mock_env["BASIC_AUTH_PASSWORD"]
    assert auth.oauth_token_url == mock_env["OAUTH_TOKEN_URL"]
    assert auth.oauth_scope == mock_env["OAUTH_SCOPE"].split()
    assert auth.auth_header == mock_env["AUTH_HEADER"]
    assert auth.auth_token_file == mock_env["AUTH_TOKEN_FILE"]
    assert auth.http_proxy == mock_env["HTTP_PROXY"]
    assert auth.https_proxy == mock_env["HTTPS_PROXY"]
    assert auth.no_proxy == mock_env["NO_PROXY"]
    assert auth.proxy_username == mock_env["PROXY_USERNAME"]
    assert auth.proxy_password == mock_env["PROXY_PASSWORD"]
    assert auth.cert_path == mock_env["CERT_PATH"]
    assert auth.tls_verify is True
    assert auth.env_url == mock_env["ENV_URL"]
    assert auth.env_name == mock_env["ENV_NAME"]


def test_get_proxy_dict(mock_env):
    """Test proxy dictionary generation."""
    # Temporarily remove TESTING flag to test proxy configuration
    env_without_testing = {k: v for k, v in mock_env.items() if k != "TESTING"}
    with patch.dict("os.environ", env_without_testing, clear=True):
        auth = AuthManager()
        proxies = auth._get_proxy_dict()

    expected_proxy = f"http://{mock_env['PROXY_USERNAME']}:{mock_env['PROXY_PASSWORD']}@proxy.test:8080"
    expected_https = f"https://{mock_env['PROXY_USERNAME']}:{mock_env['PROXY_PASSWORD']}@proxy.test:8080"

    assert proxies["http"] == expected_proxy
    assert proxies["https"] == expected_https


def test_get_verify(mock_env):
    """Test SSL verification configuration."""
    auth = AuthManager()
    assert auth._get_verify() == mock_env["CERT_PATH"]

    with patch.dict(os.environ, {"TLS_VERIFY": "false"}):
        auth = AuthManager()
        assert auth._get_verify() is False

    with patch.dict(os.environ, {"CERT_PATH": ""}):
        auth = AuthManager()
        assert auth._get_verify() is True


@pytest.mark.parametrize("token_exists", [True, False])
def test_token_file_operations(mock_env, token_exists):
    """Test token file save and load operations."""
    test_token = {"access_token": "test_token", "expires_in": 3600}
    mock_file = mock_open()

    with patch.dict("os.environ", {**mock_env, "TESTING": "true"}):
        with patch("builtins.open", mock_file):
            with patch("os.path.exists", return_value=token_exists):
                auth = AuthManager()

                # Test save token
                auth._save_token(test_token)
                mock_file().write.assert_called_once_with(
                    '{"access_token":"test_token","expires_in":3600}'
                )

                # Test load token
                mock_file.return_value.read.return_value = '{"access_token":"test_token","expires_in":3600}'
                loaded_token = auth._load_token()
                if token_exists:
                    assert loaded_token == test_token
                else:
                    assert loaded_token is None


@patch("src.utils.auth.OAuth2Session")
@patch("src.utils.auth.BackendApplicationClient")
def test_get_session(mock_client_class, mock_oauth, mock_env):
    """Test session creation and configuration."""
    mock_session = MagicMock()
    mock_session.token = {"access_token": "test_token"}
    mock_session.verify = mock_env["CERT_PATH"]
    mock_session.proxies = None
    mock_client = MagicMock()

    mock_client_class.return_value = mock_client
    mock_oauth.return_value = mock_session

    auth = AuthManager()
    session = auth.get_session()

    # Verify OAuth2Session was created with correct parameters
    mock_client_class.assert_called_once_with(client_id=mock_env["BASIC_AUTH_USERNAME"])
    mock_oauth.assert_called_once_with(client=mock_client)
    assert session == mock_session
    assert session.verify == mock_env["CERT_PATH"]
    assert session.proxies is None  # No proxies in test mode
    assert session.token == {"access_token": "test_token"}


def test_get_headers(mock_env):
    """Test authentication headers generation."""
    with patch("requests_oauthlib.OAuth2Session") as mock_oauth:
        mock_session = MagicMock()
        mock_oauth.return_value = mock_session
        mock_session.token = {"access_token": "test_token"}

        auth = AuthManager()
        headers = auth.get_headers()

        assert headers[mock_env["AUTH_HEADER"]] == "Bearer test_token"
