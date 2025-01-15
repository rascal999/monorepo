"""
Authentication and environment configuration utilities.
"""

import os
import json
from typing import Dict, Any, List, Optional
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient


class AuthManager:
    """Manages authentication and environment configuration."""

    def __init__(self):
        """Initialize auth manager with environment configuration."""
        # Basic auth settings
        self.basic_auth_username = os.getenv("BASIC_AUTH_USERNAME")
        self.basic_auth_password = os.getenv("BASIC_AUTH_PASSWORD")

        # OAuth settings
        self.oauth_token_url = os.getenv("OAUTH_TOKEN_URL")
        self.oauth_scope = os.getenv("OAUTH_SCOPE", "").split()
        self.auth_header = os.getenv("AUTH_HEADER", "Authorization")
        self.auth_token_file = os.getenv("AUTH_TOKEN_FILE", ".oauth_token")

        # Proxy settings
        self.http_proxy = os.getenv("HTTP_PROXY")
        self.https_proxy = os.getenv("HTTPS_PROXY")
        self.no_proxy = os.getenv("NO_PROXY")
        self.proxy_username = os.getenv("PROXY_USERNAME")
        self.proxy_password = os.getenv("PROXY_PASSWORD")

        # SSL settings
        self.cert_path = os.getenv("CERT_PATH")
        self.tls_verify = os.getenv("TLS_VERIFY", "true").lower() == "true"

        # Environment settings
        self.env_url = os.getenv("ENV_URL")
        self.env_name = os.getenv("ENV_NAME")

        # Session cache
        self._session = None

    def _get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """Get proxy configuration dictionary.

        Returns:
            Proxy configuration dictionary or None if no proxy configured
        """
        # In test mode, return None to disable proxies
        if os.getenv("TESTING"):
            return None

        # Build proxy dict from environment
        proxies = {}
        auth = ""
        if self.proxy_username and self.proxy_password:
            auth = f"{self.proxy_username}:{self.proxy_password}@"

        if self.http_proxy:
            proxy_url = self.http_proxy.replace("http://", "")
            proxies["http"] = f"http://{auth}{proxy_url}"

        if self.https_proxy:
            proxy_url = self.https_proxy.replace("https://", "")
            proxies["https"] = f"https://{auth}{proxy_url}"

        return proxies if proxies else None

    def _get_verify(self) -> bool | str:
        """Get SSL verification configuration.

        Returns:
            True/False for verification, or path to certificate
        """
        if not self.tls_verify:
            return False
        if self.cert_path:
            return self.cert_path
        return True

    def _save_token(self, token: Dict[str, Any]) -> None:
        """Save OAuth token to file.

        Args:
            token: OAuth token dictionary
        """
        # Format token as compact JSON with proper separators
        token_json = json.dumps(token, separators=(',', ':'))
        
        # Create directory if token file has a directory path
        dir_path = os.path.dirname(self.auth_token_file)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
            
        # Write in a single operation
        with open(self.auth_token_file, "w") as f:
            f.write(token_json)

    def _load_token(self) -> Optional[Dict[str, Any]]:
        """Load OAuth token from file.

        Returns:
            OAuth token dictionary or None if file doesn't exist
        """
        try:
            if not os.path.exists(self.auth_token_file):
                return None

            with open(self.auth_token_file) as f:
                content = f.read().strip()
                if not content:
                    return None
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            # If there's any error reading the token, return None
            # so a new token will be fetched
            return None

    def get_session(self) -> OAuth2Session:
        """Get authenticated OAuth2 session.

        Returns:
            Configured OAuth2Session
        """
        if self._session is None:
            # Create OAuth2 session
            client = BackendApplicationClient(client_id=self.basic_auth_username)
            self._session = OAuth2Session(client=client)

            # Configure session
            self._session.verify = self._get_verify()
            proxies = self._get_proxy_dict()
            if proxies:
                self._session.proxies = proxies

            # Load or fetch token
            token = self._load_token()
            if not token:
                token = self._session.fetch_token(
                    token_url=self.oauth_token_url,
                    client_id=self.basic_auth_username,
                    client_secret=self.basic_auth_password,
                    verify=self._get_verify(),
                )
                self._save_token(token)

            self._session.token = token

        return self._session

    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers.

        Returns:
            Dictionary of auth headers
        """
        session = self.get_session()
        return {self.auth_header: f"Bearer {session.token['access_token']}"}
