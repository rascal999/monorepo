"""Authentication handling for pytest test generation."""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from requests_oauthlib import OAuth2Session


class AuthConfig(BaseModel):
    """Authentication configuration model."""
    type: str
    token: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    in_header: bool = True
    token_url: Optional[str] = None
    scope: Optional[List[str]] = None  # Changed to List[str] since OAuth scopes are a list
    expiry: Optional[int] = 3600

class TokenInfo(BaseModel):
    """OAuth token information."""
    access_token: str
    expires_at: float


class AuthHandler:
    """Handle authentication for test requests."""
    
    def __init__(self):
        """Initialize AuthHandler with environment variables."""
        load_dotenv()
        self.token_file = Path(os.getenv('AUTH_TOKEN_FILE', '.oauth_token'))

    def _get_cached_token(self) -> Optional[TokenInfo]:
        """Get cached OAuth token if valid."""
        if not self.token_file.exists():
            return None
        
        try:
            data = json.loads(self.token_file.read_text())
            token_info = TokenInfo(**data)
            
            # Check if token is expired (with 5 min buffer)
            if token_info.expires_at > datetime.now().timestamp() + 300:
                return token_info
        except Exception:
            return None
        return None

    def _save_token(self, token_info: TokenInfo):
        """Save OAuth token to cache file."""
        self.token_file.write_text(json.dumps({
            'access_token': token_info.access_token,
            'expires_at': token_info.expires_at
        }))

    def _get_oauth_token(self) -> Optional[str]:
        """Get OAuth token using basic auth credentials."""
        # Check cache first
        cached = self._get_cached_token()
        if cached:
            return cached.access_token

        # Get new token
        try:
            username = os.getenv('BASIC_AUTH_USERNAME')
            password = os.getenv('BASIC_AUTH_PASSWORD')
            token_url = os.getenv('OAUTH_TOKEN_URL')
            scope = os.getenv('OAUTH_SCOPE', '').split() if os.getenv('OAUTH_SCOPE') else []
            
            if not all([username, password, token_url]):
                return None

            # Get SSL verification setting
            verify = os.getenv('TLS_VERIFY', 'true').lower() == 'true'
            cert_path = os.getenv('CERT_PATH')
            verify_arg = cert_path if cert_path else verify

            # Use client credentials grant type
            response = requests.post(
                token_url,
                auth=(username, password),
                data={
                    'grant_type': 'client_credentials',
                    'scope': ' '.join(scope) if scope else ''
                },
                verify=verify_arg
            )
            response.raise_for_status()
            token = response.json()

            # Cache token
            expires_at = datetime.now().timestamp() + float(token.get('expires_in', 3600))
            token_info = TokenInfo(
                access_token=token['access_token'],
                expires_at=expires_at
            )
            self._save_token(token_info)
            
            return token['access_token']
        except Exception as e:
            logger.error(f"Failed to get OAuth token: {str(e)}")
            return None

    def create_session(self, auth_config: Optional[AuthConfig] = None) -> requests.Session:
        """Create a requests session with authentication."""
        session = requests.Session()
        
        if auth_config:
            if auth_config.type == "oauth":
                token = self._get_oauth_token()
                if token:
                    session.headers["Authorization"] = f"Bearer {token}"
            elif auth_config.type == "apiKey":
                if auth_config.in_header:
                    session.headers[auth_config.key] = auth_config.value
                else:
                    session.params[auth_config.key] = auth_config.value

        # Add proxy configuration if specified
        http_proxy = os.getenv('HTTP_PROXY')
        https_proxy = os.getenv('HTTPS_PROXY')
        if http_proxy or https_proxy:
            session.proxies = {
                'http': http_proxy,
                'https': https_proxy
            }
            
            # Add proxy authentication if specified
            proxy_username = os.getenv('PROXY_USERNAME')
            proxy_password = os.getenv('PROXY_PASSWORD')
            if proxy_username and proxy_password:
                session.proxy_auth = (proxy_username, proxy_password)

        return session

    def generate_auth_fixture(self, auth_config: AuthConfig) -> str:
        """Generate pytest fixture for authentication."""
        fixture_code = [
            "import os",
            "import logging",
            "import pytest",
            "import requests",
            "from dotenv import load_dotenv",
            "",
            "logger = logging.getLogger(__name__)",
            "",
            "@pytest.fixture(scope='session')",
            "def auth_handler():",
            '    """Create AuthHandler instance."""',
            "    load_dotenv()",
            "    handler = AuthHandler()",
            "    # Test OAuth token retrieval on startup",
            "    token = handler._get_oauth_token()",
            "    if not token:",
            '        logger.warning("Failed to obtain initial OAuth token")',
            "    return handler",
            "",
            "@pytest.fixture(scope='function')",
            "def oauth_token(auth_handler):",
            '    """Get OAuth token for request."""',
            "    token = auth_handler._get_oauth_token()",
            "    assert token, 'Failed to obtain OAuth token'",
            "    return token",
            "",
            "@pytest.fixture",
            "def session(base_url):",
            '    """Create a session with base URL."""',
            "    session = requests.Session()",
            "    session.base_url = base_url",
            "    return session",
        ]

        return "\n".join(fixture_code)

    def extract_auth_config(self, auth_data: Dict) -> Optional[AuthConfig]:
        """Extract authentication configuration from Postman auth data.

        Args:
            auth_data: Authentication data from Postman collection

        Returns:
            AuthConfig object if auth data is valid, None otherwise
        """
        if not auth_data:
            return None

        auth_type = auth_data.get("type", "").lower()
        
        # Always use OAuth for basic auth or bearer token
        if auth_type in ("basic", "bearer", "oauth2"):
            scope = os.getenv('OAUTH_SCOPE', '').split() if os.getenv('OAUTH_SCOPE') else None
            return AuthConfig(
                type="oauth",
                token_url=os.getenv('OAUTH_TOKEN_URL'),
                scope=scope
            )
        
        elif auth_type == "apikey":
            key = next(
                (item["value"] for item in auth_data.get("apikey", [])
                 if item["key"] == "key"),
                None
            )
            value = next(
                (item["value"] for item in auth_data.get("apikey", [])
                 if item["key"] == "value"),
                None
            )
            in_header = next(
                (item["value"] for item in auth_data.get("apikey", [])
                 if item["key"] == "in"),
                "header"
            ) == "header"
            
            if key and value:
                return AuthConfig(
                    type="apiKey",
                    key=key,
                    value=value,
                    in_header=in_header
                )

        return None
