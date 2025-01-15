"""
Parser for dependency graph YAML files.
"""

import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path


class DependencyGraphParser:
    """Parser for dependency graph YAML files."""

    def __init__(self, dependency_file: str, exclude_folders: Optional[List[str]] = None):
        """Initialize dependency graph parser.

        Args:
            dependency_file: Path to dependency graph YAML file
            exclude_folders: List of folders to exclude from dependencies
        """
        self.file_path = dependency_file
        self.exclude_folders = exclude_folders or []
        self.dependencies = self._load_dependencies()

    def _load_dependencies(self) -> Dict[str, Any]:
        """Load and validate dependency graph file.

        Returns:
            Parsed dependency data

        Raises:
            ValueError: If file is invalid or missing required data
        """
        try:
            with open(self.file_path) as f:
                data = yaml.safe_load(f)

            # Validate basic structure
            if not isinstance(data, dict):
                raise ValueError("Invalid dependency file format")
            if "postman_collection_dependencies" not in data:
                raise ValueError("Missing postman_collection_dependencies section")
            if "endpoints" not in data["postman_collection_dependencies"]:
                raise ValueError("Missing endpoints section")

            return data["postman_collection_dependencies"]["endpoints"]

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading dependency file: {str(e)}")

    def get_endpoint_dependencies(self, endpoint: str) -> List[Dict[str, Any]]:
        """Get dependencies for specific endpoint.

        Args:
            endpoint: Endpoint to get dependencies for

        Returns:
            List of dependent endpoints with their details
        """
        if endpoint not in self.dependencies:
            return []

        deps = []
        endpoint_info = self.dependencies[endpoint]

        # Get dependencies from variable usage
        if "uses_variables" in endpoint_info:
            for var_name, var_info in endpoint_info["uses_variables"].items():
                if "set_by" in var_info:
                    for dep_endpoint in var_info["set_by"]:
                        if not self._is_excluded(dep_endpoint):
                            dep_info = self.dependencies.get(dep_endpoint, {})
                            deps.append({
                                "endpoint": dep_endpoint,
                                "request": dep_info.get("request", {}),
                                "sets": dep_info.get("sets_variables", []),
                                "uses_variables": dep_info.get("uses_variables", {}),
                            })

        return deps

    def get_variable_dependencies(self, endpoint: str) -> Dict[str, List[str]]:
        """Get variable dependencies for endpoint.

        Args:
            endpoint: Endpoint to get variable dependencies for

        Returns:
            Dictionary mapping variables to endpoints that set them
        """
        vars = {}
        if endpoint not in self.dependencies:
            return vars

        endpoint_info = self.dependencies[endpoint]
        if "uses_variables" not in endpoint_info:
            return vars

        # For each variable used by this endpoint
        for var_name, var_info in endpoint_info["uses_variables"].items():
            if "set_by" in var_info:
                vars[var_name] = [
                    dep for dep in var_info["set_by"]
                    if not self._is_excluded(dep)
                ]

        return vars

    def build_dependency_chain(self, endpoint: str) -> List[Dict[str, Any]]:
        """Build complete dependency chain for endpoint.

        Args:
            endpoint: Target endpoint to build chain for

        Returns:
            Ordered list of endpoints in dependency chain
        """
        chain = []
        visited = set()

        def add_dependencies(ep: str):
            if ep in visited or self._is_excluded(ep):
                return
            visited.add(ep)

            # Add dependencies first
            deps = self.get_endpoint_dependencies(ep)
            for dep in deps:
                add_dependencies(dep["endpoint"])

            # Add this endpoint
            chain.append({
                "endpoint": ep,
                "request": self.dependencies[ep].get("request", {}),
                "sets": self.dependencies[ep].get("sets_variables", []),
                "uses_variables": self.dependencies[ep].get("uses_variables", {}),
            })

        add_dependencies(endpoint)
        return chain

    def get_all_endpoints(self) -> List[str]:
        """Get all endpoints in dependency graph.

        Returns:
            List of all endpoint names
        """
        return [
            endpoint
            for endpoint in self.dependencies.keys()
            if not self._is_excluded(endpoint)
        ]

    def _is_excluded(self, endpoint: str) -> bool:
        """Check if endpoint is in excluded folder.

        Args:
            endpoint: Endpoint to check

        Returns:
            True if endpoint should be excluded
        """
        for folder in self.exclude_folders:
            if f"/{folder}/" in endpoint:
                return True
        return False
