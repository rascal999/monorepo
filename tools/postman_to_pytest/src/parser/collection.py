"""
Parser for Postman collection JSON files.
Extracts request details, folder structure, and test information.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from ..utils.auth import AuthManager


class PostmanCollectionParser:
    def __init__(
        self,
        collection_path: str,
        exclude_folders: Optional[List[str]] = None,
        auth_manager: Optional[AuthManager] = None,
    ):
        """Initialize parser with collection file path and options.

        Args:
            collection_path: Path to Postman collection JSON file
            exclude_folders: Optional list of folder names to exclude
        """
        self.collection_path = collection_path
        self.exclude_folders = exclude_folders or []
        self.auth_manager = auth_manager
        self.collection = self._load_collection()

    def _load_collection(self) -> Dict[str, Any]:
        """Load and validate Postman collection JSON file.

        Returns:
            Dict containing the parsed collection data

        Raises:
            FileNotFoundError: If collection file doesn't exist
            ValueError: If collection format is invalid
        """
        if not Path(self.collection_path).exists():
            raise FileNotFoundError(
                f"Collection file not found: {self.collection_path}"
            )

        with open(self.collection_path) as f:
            collection = json.load(f)

        # Validate basic collection structure
        if "info" not in collection or "item" not in collection:
            raise ValueError("Invalid Postman collection format")

        return collection

    def _should_exclude(self, folder_path: List[str]) -> bool:
        """Check if folder path should be excluded.

        Args:
            folder_path: List of folder names forming path

        Returns:
            True if path contains excluded folder, False otherwise
        """
        return any(folder in folder_path for folder in self.exclude_folders)

    def _extract_request_details(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant details from request object.

        Args:
            request: Request object from collection

        Returns:
            Dict containing extracted request details
        """
        if not isinstance(request, dict):
            return {}

        details = {
            "method": request.get("method", ""),
            "url": request.get("url", {}),
            "headers": self._merge_headers(request.get("header", [])),
            "auth": self._get_auth_config(request.get("auth", {})),
        }

        # Extract URL components if present
        if isinstance(details["url"], dict):
            details["url"] = {
                "raw": details["url"].get("raw", ""),
                "path": details["url"].get("path", []),
                "query": details["url"].get("query", []),
                "variable": details["url"].get("variable", []),
            }

        # Handle request body if present
        if "body" in request:
            details["body"] = request["body"]

        return details

    def _merge_headers(self, headers: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Merge request headers with auth headers.

        Args:
            headers: List of header dictionaries from request

        Returns:
            List of merged headers including auth headers
        """
        if not self.auth_manager:
            return headers

        # Convert auth headers to Postman format
        auth_headers = [
            {"key": k, "value": v} for k, v in self.auth_manager.get_headers().items()
        ]

        # Remove any existing auth headers with same keys
        filtered_headers = [
            h for h in headers if h.get("key") not in self.auth_manager.get_headers()
        ]

        return filtered_headers + auth_headers

    def _get_auth_config(self, auth_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get authentication configuration.

        Args:
            auth_config: Authentication config from request

        Returns:
            Updated auth configuration with OAuth details
        """
        if not self.auth_manager:
            return auth_config

        # Add OAuth configuration
        return {
            "type": "oauth2",
            "oauth2": {
                "tokenUrl": self.auth_manager.oauth_token_url,
                "scope": " ".join(self.auth_manager.oauth_scope),
                "clientId": self.auth_manager.basic_auth_username,
                "clientSecret": self.auth_manager.basic_auth_password,
            },
        }

    def get_request_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find request by its Postman name (folder path + name).

        Args:
            name: Full request name (e.g. "User Management/Get User Details")

        Returns:
            Dict with request details if found, None otherwise
        """

        def search_items(
            items: List[Dict[str, Any]], current_path: List[str]
        ) -> Optional[Dict[str, Any]]:
            for item in items:
                # Skip if in excluded folder
                if self._should_exclude(current_path):
                    continue

                if "item" in item:
                    # This is a folder
                    result = search_items(
                        item["item"], current_path + [item.get("name", "")]
                    )
                    if result:
                        return result
                else:
                    # This is a request
                    full_name = "/".join(current_path + [item.get("name", "")])
                    if full_name == name:
                        return {
                            "name": item.get("name", ""),
                            "path": current_path,
                            "request": self._extract_request_details(
                                item.get("request", {})
                            ),
                        }
            return None

        return search_items(self.collection["item"], [])

    def get_request_by_endpoint(
        self, method: str, path: str
    ) -> Optional[Dict[str, Any]]:
        """Find request by HTTP method and path.

        Args:
            method: HTTP method (e.g. "GET", "POST")
            path: Request path (e.g. "/api/users")

        Returns:
            Dict with request details if found, None otherwise
        """

        def search_items(
            items: List[Dict[str, Any]], current_path: List[str]
        ) -> Optional[Dict[str, Any]]:
            for item in items:
                # Skip if in excluded folder
                if self._should_exclude(current_path):
                    continue

                if "item" in item:
                    # This is a folder
                    result = search_items(
                        item["item"], current_path + [item.get("name", "")]
                    )
                    if result:
                        return result
                else:
                    # This is a request
                    request = item.get("request", {})
                    if request.get(
                        "method", ""
                    ).upper() == method.upper() and request.get("url", {}).get(
                        "raw", ""
                    ).endswith(
                        path
                    ):
                        return {
                            "name": item.get("name", ""),
                            "path": current_path,
                            "request": self._extract_request_details(request),
                        }
            return None

        return search_items(self.collection["item"], [])

    def get_all_requests(self) -> List[Dict[str, Any]]:
        """Get all requests in collection (respecting exclusions).

        Returns:
            List of dicts containing request details
        """
        requests = []

        def collect_items(items: List[Dict[str, Any]], current_path: List[str]):
            for item in items:
                # Skip if in excluded folder
                if self._should_exclude(current_path):
                    continue

                if "item" in item:
                    # This is a folder
                    collect_items(item["item"], current_path + [item.get("name", "")])
                else:
                    # This is a request
                    requests.append(
                        {
                            "name": item.get("name", ""),
                            "path": current_path,
                            "request": self._extract_request_details(
                                item.get("request", {})
                            ),
                        }
                    )

        collect_items(self.collection["item"], [])
        return requests
