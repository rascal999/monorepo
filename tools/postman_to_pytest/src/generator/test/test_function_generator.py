"""Test function generation utilities."""

from typing import Dict, Any, List
from src.generator.handlers.fixtures import FixtureGenerator
from src.generator.formatters.request_formatter import RequestFormatter
from src.generator.handlers.variable_handler import handle_response_variables


class TestFunctionGenerator:
    """Generator for test functions."""

    def __init__(self):
        """Initialize test function generator."""
        self.request_formatter = RequestFormatter()

    def generate_test_function(
        self,
        name: str,
        request_details: Dict[str, Any],
        dependencies: List[str],
        variables: List[str],
        fixture_generator: FixtureGenerator,
    ) -> List[str]:
        """Generate a test function.

        Args:
            name: Test function name
            request_details: Request details from Postman
            dependencies: List of dependent test names
            variables: List of required variables
            fixture_generator: Generator for test fixtures

        Returns:
            List of lines for test function
        """
        function_lines = []

        # Add dependency marker
        if dependencies:
            deps_str = '", "'.join(dependencies)
            function_lines.append(f'@pytest.mark.dependency(depends=["{deps_str}"])')
        else:
            function_lines.append('@pytest.mark.dependency()')

        # Function definition with fixtures
        fixtures = ["auth_session", "env_url", "tls_verify"] + variables
        fixtures_str = ", ".join(fixtures)
        function_lines.append(f"def {name}({fixtures_str}):")

        # Function docstring
        function_lines.append(
            f'    """{request_details.get("name", "Test request")}."""'
        )

        # Format request details
        request = request_details.get("request", request_details)
        # Get dynamic variables from variables list and request
        dynamic_vars = set(variables)  # Add all variables from function parameters
        if "uses_variables" in request_details:
            for var_name, var_info in request_details["uses_variables"].items():
                if isinstance(var_info, dict) and var_info.get("type") == "dynamic":
                    dynamic_vars.add(var_name)
        function_lines.extend(self.request_formatter.format_request_details(request, dynamic_vars, request_details))

        # Handle response variables if needed
        function_lines.extend(handle_response_variables(request_details))

        function_lines.append("")
        return function_lines

    def order_tests(
        self,
        request_details: Dict[str, Any],
        dependencies: List[Dict[str, Any]],
        variables: Dict[str, List[str]],
        format_test_name_fn,
    ) -> List[Dict[str, Any]]:
        """Order tests based on dependencies.

        Args:
            request_details: Main request details
            dependencies: List of dependent requests
            variables: Variable dependency mapping
            format_test_name_fn: Function to format test names

        Returns:
            List of ordered test configurations
        """
        all_tests = []
        
        # Process dependencies in original order
        for dep in dependencies:
            method = dep.get("request", {}).get("method", "")
            dep_name = format_test_name_fn(dep.get("name", dep["endpoint"]), method, include_method=False)
            # Find tests this dependency depends on
            dep_deps = []
            if "uses_variables" in dep:
                for var_name, var_info in dep["uses_variables"].items():
                    if isinstance(var_info, dict) and var_info.get("type") == "dynamic":
                        # Find tests that set this variable
                        for other_dep in dependencies:
                            if "sets" in other_dep and var_name in other_dep["sets"]:
                                # Only add dependency if it comes before this test
                                # to break circular dependencies
                                if dependencies.index(other_dep) < dependencies.index(dep):
                                    other_method = other_dep.get("request", {}).get("method", "")
                                    other_name = format_test_name_fn(other_dep.get("name", other_dep["endpoint"]), other_method, include_method=False)
                                    if other_name not in dep_deps:
                                        dep_deps.append(other_name)
            
            all_tests.append({
                "name": dep_name,
                "details": dep,
                "dependencies": dep_deps,
                "variables": [v for v in variables if dep.get("sets", []) and v in dep["sets"]]
            })

        # Add main test
        main_method = request_details.get("request", {}).get("method", "")
        main_name = format_test_name_fn(request_details["name"], main_method, include_method=False)
        main_deps = []
        # Add all dependencies that set variables used by the main test
        for dep in dependencies:
            if "sets" in dep:
                for var in dep["sets"]:
                    if var in variables:
                        dep_method = dep.get("request", {}).get("method", "")
                        dep_name = format_test_name_fn(dep.get("name", dep["endpoint"]), dep_method, include_method=False)
                        if dep_name not in main_deps:
                            main_deps.append(dep_name)
        
        all_tests.append({
            "name": main_name,
            "details": request_details,
            "dependencies": main_deps,
            "variables": list(variables.keys())
        })

        # Order tests based on dependencies
        ordered_tests = []
        while all_tests:
            # Find test with no unresolved dependencies
            for test in all_tests:
                unresolved_deps = [d for d in test["dependencies"] 
                                 if d not in [t["name"] for t in ordered_tests]]
                if not unresolved_deps:
                    ordered_tests.append(test)
                    all_tests.remove(test)
                    break
            else:
                # If we get here, we have a circular dependency
                # Add remaining tests in current order
                ordered_tests.extend(all_tests)
                break

        return ordered_tests
