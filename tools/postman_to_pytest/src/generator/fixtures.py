"""
Generator for pytest fixtures from Postman variables.
"""

from typing import Dict, Any, List, Optional, Set
from pathlib import Path


class FixtureGenerator:
    """Generates pytest fixtures for test variables."""

    def __init__(self):
        """Initialize fixture generator."""
        self.fixtures: Dict[str, Dict[str, Any]] = {}

    def add_fixture(
        self,
        name: str,
        var_type: str,
        scope: str = "function",
        dependencies: Optional[List[str]] = None,
        docstring: Optional[str] = None,
    ) -> None:
        """Add a fixture definition.

        Args:
            name: Fixture name
            var_type: Type of variable ('static' or 'dynamic')
            scope: Fixture scope ('session', 'module', or 'function')
            dependencies: List of fixture dependencies
            docstring: Fixture documentation string
        """
        self.fixtures[name] = {
            "type": var_type,
            "scope": scope,
            "dependencies": dependencies or [],
            "docstring": docstring or f"Fixture for {name}",
        }

    def get_fixture_setup(self, name: str, value: Any) -> str:
        """Get fixture setup code.

        Args:
            name: Fixture name
            value: Value to set

        Returns:
            Setup code string

        Raises:
            ValueError: If fixture not found
        """
        if name not in self.fixtures:
            raise ValueError(f"Fixture {name} not found")

        # Format value based on type
        if isinstance(value, str):
            formatted_value = f"'{value}'"
        elif isinstance(value, (dict, list)):
            formatted_value = str(value)
        else:
            formatted_value = str(value)

        return f"_variable_store['{name}'] = {formatted_value}"

    def _get_dependency_depth(self, name: str, visited: Optional[Set[str]] = None) -> int:
        """Get the maximum depth of dependencies for a fixture.

        Args:
            name: Fixture name
            visited: Set of visited fixtures to detect cycles

        Returns:
            Maximum dependency depth
        """
        if visited is None:
            visited = set()

        if name in visited:
            return 0  # Break cycles

        visited.add(name)
        fixture = self.fixtures[name]
        
        if not fixture["dependencies"]:
            return 0

        max_depth = 0
        for dep in fixture["dependencies"]:
            depth = self._get_dependency_depth(dep, visited.copy())
            max_depth = max(max_depth, depth)

        return max_depth + 1

    def generate_fixture_file(self, output_dir: Path) -> str:
        """Generate conftest.py with fixtures.

        Args:
            output_dir: Output directory path

        Returns:
            Generated file content
        """
        lines = [
            "import pytest",
            "from typing import Dict, Any",
            "",
            "# Variable storage",
            "_variable_store: Dict[str, Any] = {}",
            "",
        ]

        # Sort fixtures by dependency depth
        sorted_fixtures = sorted(
            self.fixtures.items(),
            key=lambda x: (self._get_dependency_depth(x[0]), x[0])
        )

        # Generate fixture functions
        for name, fixture in sorted_fixtures:
            # Scope decorator - always include scope explicitly
            lines.append(f'@pytest.fixture(scope="{fixture["scope"]}")')

            # Function definition with dependencies
            if fixture["dependencies"]:
                deps = ", ".join(fixture["dependencies"])
                lines.append(f"def {name}({deps}):")
            else:
                lines.append(f"def {name}():")

            # Docstring
            lines.append(f'    """{fixture["docstring"]}"""')

            # Variable handling
            if fixture["type"] == "dynamic":
                lines.extend(
                    [
                        "    # Get value from store",
                        f"    value = _variable_store.get('{name}')",
                        "    yield value",
                        "    # Cleanup",
                        f"    if '{name}' in _variable_store:",
                        f"        del _variable_store['{name}']",
                    ]
                )
            else:  # static
                lines.extend(
                    [
                        "    # Return static value",
                        f"    return _variable_store.get('{name}')",
                    ]
                )

            lines.append("")

        # Write to file
        conftest_path = output_dir / "conftest.py"
        content = "\n".join(lines)
        conftest_path.write_text(content)

        return content
