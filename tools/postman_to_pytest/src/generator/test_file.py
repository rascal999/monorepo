"""
Generator for pytest test files from Postman requests and dependencies.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from .fixtures import FixtureGenerator
from ..utils.auth import AuthManager


class TestFileGenerator:
    def __init__(
        self,
        output_dir: str,
        fixture_generator: FixtureGenerator,
        auth_manager: Optional[AuthManager] = None,
    ):
        """Initialize test file generator.

        Args:
            output_dir: Directory to write test files to
            fixture_generator: FixtureGenerator instance for managing fixtures
        """
        self.output_dir = Path(output_dir)
        self.fixture_generator = fixture_generator
        self.auth_manager = auth_manager

    def _sanitize_name(self, name: str) -> str:
        """Convert request name to valid Python identifier.

        Args:
            name: Original request name

        Returns:
            Sanitized name valid for Python
        """
        # Replace non-alphanumeric with underscore
        sanitized = "".join(c if c.isalnum() else "_" for c in name).lower()

        # Always prefix with test_
        if not sanitized.startswith("test_"):
            sanitized = "test_" + sanitized

        # Collapse multiple underscores
        while "__" in sanitized:
            sanitized = sanitized.replace("__", "_")

        # Remove trailing underscore
        sanitized = sanitized.rstrip("_")

        return sanitized

    def _format_request_details(
        self, request: Dict[str, Any], indent: str = "    "
    ) -> List[str]:
        """Format request details as Python code.

        Args:
            request: Request details dict
            indent: Indentation string

        Returns:
            List of code lines
        """
        lines = []

        # Add method
        lines.append(f'{indent}method = "{request.get("method", "GET")}"')

        # Format URL
        url = request.get("url", {})
        if isinstance(url, dict):
            lines.append(f'{indent}url = "{url.get("raw", "")}"')
        else:
            lines.append(f'{indent}url = "{url}"')

        # Format headers
        headers = {}
        for header in request.get("header", []):
            headers[header["key"]] = header["value"]
        lines.append(f"{indent}headers = {json.dumps(headers)}")

        # Format body
        body = request.get("body", {})
        if body and isinstance(body, dict):
            if body.get("mode") == "raw":
                raw_data = body.get("raw", "")
                if isinstance(raw_data, str):
                    try:
                        # Try to parse as JSON
                        data = json.loads(raw_data)
                        lines.append(f"{indent}data = {json.dumps(data)}")
                    except json.JSONDecodeError:
                        # Use raw string if not valid JSON
                        lines.append(f"{indent}data = {repr(raw_data)}")
            elif body.get("mode") == "urlencoded":
                data = {p["key"]: p["value"] for p in body.get("urlencoded", [])}
                lines.append(f"{indent}data = {json.dumps(data)}")
            elif body.get("mode") == "formdata":
                data = {p["key"]: p["value"] for p in body.get("formdata", [])}
                lines.append(f"{indent}data = {json.dumps(data)}")
            else:
                lines.append(f"{indent}data = None")
        else:
            lines.append(f"{indent}data = None")

        return lines

    def generate_test_file(
        self,
        request_details: Dict[str, Any],
        dependencies: List[Dict[str, Any]],
        variables: Dict[str, List[str]],
    ) -> str:
        """Generate pytest file for request and its dependencies.

        Args:
            request_details: Dict with request information
            dependencies: List of dependency endpoint information
            variables: Dict mapping variables to setter endpoints

        Returns:
            Generated test file content
        """
        # Initialize uses list for request if not present
        if "uses" not in request_details:
            request_details["uses"] = []

        # Add variables to request's uses list
        for var_name in variables.keys():
            request_details["uses"].append((var_name, "dynamic"))

        # Initialize uses list for dependencies
        for dep in dependencies:
            if "uses" not in dep:
                dep["uses"] = []
                # Add variables this dependency sets
                for var in dep.get("sets", []):
                    dep["uses"].append((var, "dynamic"))

        lines = [
            "import pytest",
            "import requests",
            "from typing import Dict, Any",
            "",
            "# Auth configuration",
            "AUTH_TOKEN_URL = None",
            "BASIC_AUTH_USERNAME = None",
            "BASIC_AUTH_PASSWORD = None",
            "",
            "@pytest.fixture(scope='session')",
            "def auth_session():",
            '    """Create authenticated session for requests."""',
            "    from requests_oauthlib import OAuth2Session",
            "    from oauthlib.oauth2 import BackendApplicationClient",
            "",
            "    # Create session with OAuth2",
            "    client = BackendApplicationClient(client_id=BASIC_AUTH_USERNAME)",
            "    session = OAuth2Session(client=client)",
            "",
            "    # Get token using client credentials grant",
            "    import base64",
            "    # Create basic auth header",
            "    auth_header = base64.b64encode(",
            "        f'{BASIC_AUTH_USERNAME}:{BASIC_AUTH_PASSWORD}'.encode()",
            "    ).decode('utf-8')",
            "",
            "    # Get token with basic auth",
            "    token = session.fetch_token(",
            "        token_url=AUTH_TOKEN_URL,",
            "        headers={'Authorization': f'Basic {auth_header}'},",
            "        auth=None,  # Disable default auth to use headers",
            "        client_id=None,  # Not needed with basic auth header",
            "        client_secret=None,  # Not needed with basic auth header",
            "    )",
            "",
            "    return session",
            "",
            "",
        ]

        # Generate test functions for dependencies first
        for dep in dependencies:
            dep_name = self._sanitize_name(dep["endpoint"])
            dep_vars = ["auth_session"] + [
                v[0] for v in dep.get("uses", [])
            ]  # Add auth_session

            lines.extend(
                [
                    f"@pytest.mark.dependency()",
                    f"def test_{dep_name}({', '.join(dep_vars)}):",
                    f'    """Test {dep["endpoint"]}"""',
                ]
            )

            # Add request details
            lines.extend(self._format_request_details(dep["request"]))

            # Add response handling and variable setting
            lines.extend(
                [
                    "    # Add auth header",
                    "    headers['Authorization'] = f'Bearer {auth_session.token[\"access_token\"]}'",
                    "",
                    "    # Make request using auth session",
                    "    response = auth_session.request(",
                    "        method=method,",
                    "        url=url,",
                    "        headers=headers,",
                    "        data=data",
                    "    )",
                    "    assert response.status_code == 200",
                ]
            )

            # Set variables for next tests
            for var in dep.get("sets", []):
                lines.append(
                    f"    {self.fixture_generator.get_fixture_setup(var, 'response.json()')}"
                )

            lines.extend(["", ""])

        # Generate main test function
        test_name = self._sanitize_name(request_details["name"])
        test_vars = ["auth_session"] + [
            v[0] for v in request_details.get("uses", [])
        ]  # Add auth_session

        # Add dependencies to test decorator
        dep_names = [f"test_{self._sanitize_name(d['endpoint'])}" for d in dependencies]
        if dep_names:
            dep_str = f"depends=[{', '.join(repr(d) for d in dep_names)}]"
            lines.append(f"@pytest.mark.dependency({dep_str})")
        else:
            lines.append("@pytest.mark.dependency()")

        lines.extend(
            [
                f"def test_{test_name}({', '.join(test_vars)}):",
                f'    """Test {request_details["name"]}"""',
            ]
        )

        # Add request details
        lines.extend(self._format_request_details(request_details["request"]))

        # Add response handling
        lines.extend(
            [
                "    # Add auth header",
                "    headers['Authorization'] = f'Bearer {auth_session.token[\"access_token\"]}'",
                "",
                "    # Make request using auth session",
                "    response = auth_session.request(",
                "        method=method,",
                "        url=url,",
                "        headers=headers,",
                "        data=data",
                "    )",
                "    assert response.status_code == 200",
            ]
        )

        # Update auth configuration if auth manager is present
        if self.auth_manager:
            auth_config = [
                f'AUTH_TOKEN_URL = "{self.auth_manager.oauth_token_url}"',
                f'BASIC_AUTH_USERNAME = "{self.auth_manager.basic_auth_username}"',
                f'BASIC_AUTH_PASSWORD = "{self.auth_manager.basic_auth_password}"',
            ]
            # Replace placeholder auth config with actual values
            content = "\n".join(lines).replace(
                "AUTH_TOKEN_URL = None\nBASIC_AUTH_USERNAME = None\nBASIC_AUTH_PASSWORD = None",
                "\n".join(auth_config),
            )
        else:
            content = "\n".join(lines)

        # Create output directory structure matching request path
        if request_details.get("path"):
            file_dir = self.output_dir.joinpath(*request_details["path"])
            file_dir.mkdir(parents=True, exist_ok=True)
            file_path = file_dir / f"test_{test_name}.py"
            file_path.write_text(content)
        else:
            file_path = self.output_dir / f"test_{test_name}.py"
            file_path.write_text(content)

        return content
