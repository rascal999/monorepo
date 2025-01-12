"""Authentication handling for pytest test generation."""

from pathlib import Path
from typing import Dict, Optional

import requests
from pydantic import BaseModel


class AuthConfig(BaseModel):
    """Authentication configuration model."""
    type: str
    token: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    in_header: bool = True


class AuthHandler:
    """Handle authentication for test requests."""

    @staticmethod
    def create_session(auth_config: Optional[AuthConfig] = None) -> requests.Session:
        """Create a requests session with authentication.

        Args:
            auth_config: Authentication configuration

        Returns:
            Configured requests.Session object
        """
        session = requests.Session()
        
        if auth_config:
            if auth_config.type == "bearer":
                session.headers["Authorization"] = f"Bearer {auth_config.token}"
            elif auth_config.type == "apiKey":
                if auth_config.in_header:
                    session.headers[auth_config.key] = auth_config.value
                else:
                    # For query parameter API keys
                    session.params[auth_config.key] = auth_config.value

        return session

    @staticmethod
    def generate_auth_fixture(auth_config: AuthConfig) -> str:
        """Generate pytest fixture for authentication.

        Args:
            auth_config: Authentication configuration

        Returns:
            String containing the fixture code
        """
        fixture_code = [
            "@pytest.fixture",
            "def session():",
            '    """Create an authenticated session."""',
            "    session = requests.Session()",
        ]

        if auth_config.type == "bearer":
            fixture_code.extend([
                f'    session.headers["Authorization"] = "Bearer {auth_config.token}"'
            ])
        elif auth_config.type == "apiKey":
            if auth_config.in_header:
                fixture_code.extend([
                    f'    session.headers["{auth_config.key}"] = "{auth_config.value}"'
                ])
            else:
                fixture_code.extend([
                    f'    session.params["{auth_config.key}"] = "{auth_config.value}"'
                ])

        fixture_code.extend([
            "    return session",
            ""
        ])

        return "\n    ".join(fixture_code)

    @staticmethod
    def extract_auth_config(auth_data: Dict) -> Optional[AuthConfig]:
        """Extract authentication configuration from Postman auth data.

        Args:
            auth_data: Authentication data from Postman collection

        Returns:
            AuthConfig object if auth data is valid, None otherwise
        """
        if not auth_data:
            return None

        auth_type = auth_data.get("type", "").lower()
        
        if auth_type == "bearer":
            token = next(
                (item["value"] for item in auth_data.get("bearer", [])
                 if item["key"] == "token"),
                None
            )
            if token:
                return AuthConfig(type="bearer", token=token)
        
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
