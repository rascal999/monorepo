"""
Parser for Postman collection JSON files.
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class PostmanCollectionParser:
    """Parser for Postman collection JSON files."""

    def __init__(self, collection_path: str, exclude_folders: Optional[List[str]] = None):
        """Initialize collection parser.

        Args:
            collection_path: Path to collection JSON file
            exclude_folders: List of folders to exclude from parsing
        """
        self.file_path = collection_path
        self.exclude_folders = exclude_folders or []
        self.collection = self._load_collection()

    def _load_collection(self) -> Dict[str, Any]:
        """Load and validate collection file.

        Returns:
            Parsed collection data

        Raises:
            ValueError: If file is invalid or missing required data
        """
        try:
            with open(self.file_path) as f:
                data = json.load(f)

            # Validate basic structure
            if not isinstance(data, dict):
                raise ValueError("Invalid collection format")
            if "info" not in data or "item" not in data:
                raise ValueError("Missing required collection fields")

            return data

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except FileNotFoundError as e:
            raise ValueError(f"Collection file not found: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading collection: {str(e)}")

    def _normalize_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize request data to handle variations in field names.

        Args:
            request: Raw request data

        Returns:
            Normalized request data
        """
        normalized = request.copy()

        # Normalize headers field
        if "header" in request:
            normalized["headers"] = request["header"]
        elif "headers" in request:
            normalized["headers"] = request["headers"]
        else:
            normalized["headers"] = []

        return normalized

    def _should_exclude(self, path: List[str]) -> bool:
        """Check if path should be excluded.

        Args:
            path: Path components

        Returns:
            True if path should be excluded
        """
        return any(folder in path for folder in self.exclude_folders)

    def get_request_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find request by name.

        Args:
            name: Request name (with optional folder path)

        Returns:
            Request details or None if not found
        """
        # Split into folder path and request name
        parts = name.split("/")
        request_name = parts[-1]
        folder_path = parts[:-1]

        def search_items(
            items: List[Dict[str, Any]], current_path: List[str]
        ) -> Optional[Dict[str, Any]]:
            for item in items:
                # Skip excluded folders
                if "item" in item and self._should_exclude(current_path + [item["name"]]):
                    continue

                # Recurse into folders
                if "item" in item:
                    result = search_items(item["item"], current_path + [item["name"]])
                    if result:
                        return result

                # Check request
                if (
                    "request" in item
                    and item["name"] == request_name
                    and (not folder_path or current_path == folder_path)
                ):
                    return {
                        "name": item["name"],
                        "path": current_path,
                        "request": self._normalize_request(item["request"]),
                    }

            return None

        return search_items(self.collection["item"], [])

    def get_request_by_endpoint(
        self, method: str, path: str
    ) -> Optional[Dict[str, Any]]:
        """Find request by HTTP method and path.

        Args:
            method: HTTP method
            path: URL path

        Returns:
            Request details or None if not found
        """

        def search_items(
            items: List[Dict[str, Any]], current_path: List[str]
        ) -> Optional[Dict[str, Any]]:
            for item in items:
                # Skip excluded folders
                if "item" in item and self._should_exclude(current_path + [item["name"]]):
                    continue

                # Recurse into folders
                if "item" in item:
                    result = search_items(item["item"], current_path + [item["name"]])
                    if result:
                        return result

                # Check request
                if "request" in item:
                    request = item["request"]
                    if request["method"] == method and request["url"]["raw"].endswith(
                        path
                    ):
                        return {
                            "name": item["name"],
                            "path": current_path,
                            "request": self._normalize_request(request),
                        }

            return None

        return search_items(self.collection["item"], [])

    def get_all_requests(self) -> List[Dict[str, Any]]:
        """Get all requests in collection.

        Returns:
            List of all request details
        """
        requests = []

        def collect_requests(items: List[Dict[str, Any]], current_path: List[str]):
            for item in items:
                # Skip excluded folders
                if "item" in item and self._should_exclude(current_path + [item["name"]]):
                    continue

                # Recurse into folders
                if "item" in item:
                    collect_requests(item["item"], current_path + [item["name"]])

                # Add request
                if "request" in item:
                    requests.append(
                        {
                            "name": item["name"],
                            "path": current_path,
                            "request": self._normalize_request(item["request"]),
                        }
                    )

        collect_requests(self.collection["item"], [])
        return requests
