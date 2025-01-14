"""
Generator for pytest fixtures from variable dependencies.
"""

from typing import Dict, List, Optional, Any


class FixtureGenerator:
    def __init__(self) -> None:
        """Initialize fixture generator."""
        self.fixtures: Dict[str, Dict[str, Any]] = {}

    def add_fixture(
        self,
        name: str,
        var_type: str = "dynamic",
        scope: str = "function",
        dependencies: Optional[List[str]] = None,
        docstring: Optional[str] = None,
    ) -> None:
        """Add fixture definition.

        Args:
            name: Fixture name
            var_type: Variable type (static or dynamic)
            scope: Fixture scope (function, class, module, session)
            dependencies: List of fixture dependencies
            docstring: Fixture documentation string
        """
        self.fixtures[name] = {
            "type": var_type,
            "scope": scope,
            "dependencies": dependencies or [],
            "docstring": docstring or f"{name} fixture",
        }

    def generate_fixture_file(self, output_path: str) -> str:
        """Generate pytest fixture file.

        Args:
            output_path: Path to write fixture file

        Returns:
            Generated fixture file content
        """
        from pathlib import Path
        lines = [
            "import pytest",
            "from typing import Dict, Any",
            "",
            "# Store for sharing variables between tests",
            "_variable_store: Dict[str, Any] = {}",
            "",
        ]

        # Generate fixtures in dependency order
        for name, fixture in self.fixtures.items():
            # Add fixture decorator
            scope = fixture["scope"]
            deps = fixture["dependencies"]
            if deps:
                lines.append(f'@pytest.fixture(scope="{scope}", autouse=True)')
                lines.append(f'def {name}({", ".join(deps)}):')
            else:
                lines.append(f'@pytest.fixture(scope="{scope}")')
                lines.append(f"def {name}():")

            # Add docstring
            lines.append(f'    """{fixture["docstring"]}"""')

            # Add fixture setup
            if fixture["type"] == "dynamic":
                lines.append("    value = _variable_store.get(name)")
                lines.append("    yield value")
                lines.append(f"    if '{name}' in _variable_store:")
                lines.append(f"        del _variable_store['{name}']")
            else:
                lines.append("    return None")

            lines.append("")

        content = "\n".join(lines)
        
        # Write the file
        output_file = Path(output_path) / "conftest.py"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content)
        
        return content

    def get_fixture_setup(self, name: str, value: Any) -> str:
        """Get code to set up a fixture value.

        Args:
            name: Name of the fixture
            value: Value to set

        Returns:
            Python code string to set up fixture

        Raises:
            ValueError: If fixture not found
        """
        if name not in self.fixtures:
            raise ValueError(f"Unknown fixture: {name}")

        if isinstance(value, str):
            value = f"'{value}'"
        return f"_variable_store['{name}'] = {value}"
