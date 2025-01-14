"""
Generator for pytest test files from Postman requests and dependencies.
"""

import os
import json
import shutil
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
        base_dir: Optional[str] = None,
    ):
        """Initialize test file generator.

        Args:
            output_dir: Directory to write test files to
            fixture_generator: FixtureGenerator instance for managing fixtures
            auth_manager: Optional auth manager for OAuth configuration
            base_dir: Optional base directory to look for .env files (defaults to current directory)
        """
        self.output_dir = Path(output_dir)
        self.fixture_generator = fixture_generator
        self.auth_manager = auth_manager
        self.base_dir = Path(base_dir) if base_dir else Path('.')
        self._copy_env_file()

    def _copy_env_file(self):
        """Copy .env file to output directory if it exists, or .env.sample if .env doesn't exist."""
        src_env = self.base_dir / '.env'
        src_env_sample = self.base_dir / '.env.sample'
        dst_env = self.output_dir / '.env'

        if src_env.exists():
            shutil.copy2(src_env, dst_env)
        elif src_env_sample.exists():
            shutil.copy2(src_env_sample, dst_env)

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
            raw_url = url.get("raw", "")
            # Don't prepend ENV_URL for absolute URLs
            if raw_url.startswith(("http://", "https://")):
                lines.append(f'{indent}url = "{raw_url}"')
            else:
                # For relative URLs, check if ENV_URL is already in the URL
                if "{ENV_URL}" in raw_url or "{{ENV_URL}}" in raw_url:
                    # Convert Postman's double curly braces to Python f-string format
                    formatted_url = raw_url.replace("{{", "{").replace("}}", "}")
                    lines.append(f'{indent}url = f"{formatted_url}"')
                else:
                    # Handle URL segments while preserving variables
                    url_segments = raw_url.split('/')
                    # Filter out empty segments but keep variable placeholders
                    filtered_segments = [seg for seg in url_segments if seg or '{' in seg]
                    # Remove any leading/trailing empty segments
                    while filtered_segments and not filtered_segments[0]:
                        filtered_segments.pop(0)
                    while filtered_segments and not filtered_segments[-1]:
                        filtered_segments.pop()
                    raw_url = '/'.join(filtered_segments)
                    # Prepend ENV_URL since it's not in the URL
                    lines.append(f'{indent}url = f"{{ENV_URL}}/{raw_url}"')
        else:
            # Same logic for string URLs
            if str(url).startswith(("http://", "https://")):
                lines.append(f'{indent}url = "{url}"')
            else:
                # For relative URLs, check if ENV_URL is already in the URL
                url_str = str(url)
                if "{ENV_URL}" in url_str or "{{ENV_URL}}" in url_str:
                    # Convert Postman's double curly braces to Python f-string format
                    formatted_url = url_str.replace("{{", "{").replace("}}", "}")
                    lines.append(f'{indent}url = f"{formatted_url}"')
                else:
                    # Handle URL segments while preserving variables
                    url_segments = url_str.split('/')
                    # Filter out empty segments but keep variable placeholders
                    filtered_segments = [seg for seg in url_segments if seg or '{' in seg]
                    # Remove any leading/trailing empty segments
                    while filtered_segments and not filtered_segments[0]:
                        filtered_segments.pop(0)
                    while filtered_segments and not filtered_segments[-1]:
                        filtered_segments.pop()
                    url_str = '/'.join(filtered_segments)
                    # Prepend ENV_URL since it's not in the URL
                    lines.append(f'{indent}url = f"{{ENV_URL}}/{url_str}"')

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

        # Add only non-environment variables to request's uses list
        for var_name, setters in variables.items():
            # Check if variable is environment type in dependencies
            if var_name in request_details.get("uses_variables", {}) and \
               request_details["uses_variables"][var_name].get("type") != "environment":
                request_details["uses"].append((var_name, "dynamic"))

        # Initialize uses list for dependencies, excluding environment variables
        for dep in dependencies:
            if "uses" not in dep:
                dep["uses"] = []
                # Add only non-environment variables this dependency sets
                for var in dep.get("sets", []):
                    if var in dep.get("uses_variables", {}) and \
                       dep["uses_variables"][var].get("type") != "environment":
                        dep["uses"].append((var, "dynamic"))

        lines = [
            "import pytest",
            "import requests",
            "import base64",
            "import os",
            "from typing import Dict, Any",
            "from dotenv import load_dotenv",
            "",
            "# Load environment variables",
            "load_dotenv()",
            "",
            "# Environment configuration",
            "ENV_URL = os.getenv('ENV_URL')",
            "TLS_VERIFY = os.getenv('TLS_VERIFY', 'true').lower() == 'true'",
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
            "    # Allow insecure transport for testing",
            "    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'",
            "",
            "    # Create session with OAuth2",
            "    client = BackendApplicationClient(client_id=BASIC_AUTH_USERNAME)",
            "    session = OAuth2Session(client=client)",
            "",
            "    # Create Basic auth header for token request",
            "    auth_str = f'{BASIC_AUTH_USERNAME}:{BASIC_AUTH_PASSWORD}'",
            "    auth_bytes = auth_str.encode('ascii')",
            "    auth_header = base64.b64encode(auth_bytes).decode('ascii')",
            "",
            "    # Get token using client credentials grant",
            "    token = session.fetch_token(",
            "        token_url=AUTH_TOKEN_URL,",
            "        client_id=BASIC_AUTH_USERNAME,",
            "        client_secret=BASIC_AUTH_PASSWORD,",
            "        headers={'Authorization': f'Basic {auth_header}'},",
            "        verify=TLS_VERIFY",
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
                    "        data=data,",
                    "        verify=TLS_VERIFY",
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
                "        data=data,",
                "        verify=TLS_VERIFY",
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
