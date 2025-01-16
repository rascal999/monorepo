"""Variable initialization utilities."""

from typing import Dict, Any, List
from src.generator.handlers.fixtures import FixtureGenerator


class VariableInitializer:
    """Handles variable initialization for test generation."""

    def __init__(self, fixture_generator: FixtureGenerator):
        """Initialize variable initializer.

        Args:
            fixture_generator: Generator for test fixtures
        """
        self.fixture_generator = fixture_generator

    def initialize_variables(
        self,
        request: Dict[str, Any],
        dependencies: List[Dict[str, Any]],
    ) -> None:
        """Initialize variable lists for request and dependencies.

        Args:
            request: Request details
            dependencies: List of dependent requests
        """
        # Initialize uses list if not present
        if "uses" not in request:
            request["uses"] = []

        # Add dynamic variables to request uses
        if "uses_variables" in request:
            for var_name, var_info in request["uses_variables"].items():
                if isinstance(var_info, dict) and var_info.get("type") == "dynamic":
                    request["uses"].append((var_name, "dynamic"))

        # Initialize dependency uses and sets lists
        for dep in dependencies:
            # Initialize uses list
            if "uses" not in dep:
                dep["uses"] = []
            if "uses_variables" in dep:
                for var_name, var_info in dep["uses_variables"].items():
                    if isinstance(var_info, dict) and var_info.get("type") == "dynamic":
                        dep["uses"].append((var_name, "dynamic"))
            
            # Initialize sets list and add fixture for each set variable
            if "sets" in dep:
                for var_name in dep["sets"]:
                    # Add fixture for the variable this dependency sets
                    self.fixture_generator.add_fixture(
                        name=var_name,
                        var_type="dynamic",
                        scope="function",
                        docstring=f"Variable set by {dep['endpoint']}"
                    )
