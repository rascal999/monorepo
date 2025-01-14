"""
Parser for dependency graph YAML files.
"""

import yaml
from typing import Dict, List, Any, Optional, Set, Sequence


class DependencyGraphParser:
    def __init__(self, dependency_file: str, exclude_folders: Optional[List[str]] = None) -> None:
        """Initialize dependency graph parser.

        Args:
            dependency_file: Path to dependency YAML file
            exclude_folders: List of folders to exclude from parsing
        """
        self.exclude_folders = exclude_folders or []
        self.dependencies: Dict[str, Any] = {}
        self.variables: Dict[str, Any] = {}
        self.raw_data: Dict[str, Any] = {}
        
        # Load dependencies from file
        try:
            with open(dependency_file) as f:
                data = yaml.safe_load(f)
                self.load_dependencies(data)
        except yaml.YAMLError:
            raise ValueError("Invalid YAML format")
        except FileNotFoundError:
            raise ValueError(f"Dependency file not found: {dependency_file}")

    def load_dependencies(self, data: Dict[str, Any]) -> None:
        """Load dependency graph from parsed YAML data.

        Args:
            data: Parsed YAML data
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid dependency graph format")

        # Store raw data for direct access in tests
        self.raw_data = data
        self.dependencies = {}
        self.variables = {}

        if not isinstance(data, dict):
            raise ValueError("Invalid dependency graph format")

        root = data.get("postman_collection_dependencies")
        if not root:
            raise ValueError("Missing postman_collection_dependencies key")

        # Extract endpoints and variables
        endpoints = root.get("endpoints", {})
        
        # Apply folder exclusions
        for endpoint, endpoint_data in endpoints.items():
            if not self._should_exclude(endpoint.split("/")):
                self.dependencies[endpoint] = endpoint_data

        self.variables = root.get("variables", {})

    def build_dependency_chain(self, endpoint: str) -> List[Dict[str, Any]]:
        """Build complete dependency chain for an endpoint.

        Args:
            endpoint: Target endpoint

        Returns:
            List of dependency endpoints in order
        """
        chain = []
        visited = set()

        def build_chain(ep: str) -> None:
            if ep in visited:
                return
            visited.add(ep)
            
            # Get direct dependencies
            deps = self.get_endpoint_dependencies(ep)
            for dep in deps:
                # Recursively build chain for each dependency
                build_chain(dep["endpoint"])
                if dep not in chain:
                    chain.append(dep)

        # Build chain for dependencies
        build_chain(endpoint)

        # Add target endpoint if it exists in dependencies
        if endpoint in self.dependencies:
            chain.append({
                "endpoint": endpoint,
                "request": self.dependencies[endpoint],
                "sets": []
            })

        return chain

    def get_endpoint_dependencies(self, endpoint: str) -> List[Dict[str, Any]]:
        """Get dependencies for an endpoint.

        Args:
            endpoint: Endpoint in format "HTTP_METHOD PATH"

        Returns:
            List of dependency endpoint information
        """
        if endpoint not in self.dependencies:
            return []

        if endpoint not in self.dependencies:
            return []

        endpoint_data = self.dependencies[endpoint]
        dependencies: List[Dict[str, Any]] = []

        # Get variables used by this endpoint
        used_vars = endpoint_data.get("uses_variables", {})

        # For each variable, add its setter endpoints as dependencies
        for var_name, var_data in used_vars.items():
            if isinstance(var_data, dict) and "set_by" in var_data:
                for setter in var_data["set_by"]:
                    if setter in self.dependencies:
                        dep_data = {
                            "endpoint": setter,
                            "request": self.dependencies[setter],
                            "sets": [var_name],
                            "uses_variables": self.dependencies[setter].get("uses_variables", {})
                        }
                        dependencies.append(dep_data)

        # Add uses_variables to each dependency
        for dep in dependencies:
            dep["uses_variables"] = self.dependencies[dep["endpoint"]].get("uses_variables", {})

        return dependencies

    def get_variable_dependencies(self, endpoint: str) -> Dict[str, List[str]]:
        """Get variable dependencies for an endpoint.

        Args:
            endpoint: Endpoint in format "HTTP_METHOD PATH"

        Returns:
            Dict mapping variable names to list of setter endpoints
        """
        if endpoint not in self.dependencies:
            return {}

        endpoint_data = self.dependencies[endpoint]
        variables: Dict[str, List[str]] = {}

        # Get variables used by this endpoint
        used_vars = endpoint_data.get("uses_variables", {})

        # For each variable, get its setter endpoints
        for var_name, var_data in used_vars.items():
            if isinstance(var_data, dict) and "set_by" in var_data:
                variables[var_name] = var_data["set_by"]

        return variables

    def _should_exclude(self, path: Sequence[str]) -> bool:
        """Check if path should be excluded.

        Args:
            path: Path components

        Returns:
            True if path should be excluded
        """
        path_str = "/".join(path)
        return any(exclude in path_str for exclude in self.exclude_folders)

    def get_all_endpoints(self) -> Set[str]:
        """Get all endpoints in dependency graph.

        Returns:
            Set of endpoint strings
        """
        return set(self.dependencies.keys())
