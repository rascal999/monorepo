"""
Tests for variable dependency handling in test generation.
"""

import pytest
from pathlib import Path
from src.generator.test import ContentGenerator
from src.generator.handlers.fixtures import FixtureGenerator
from src.utils.auth import AuthManager


@pytest.fixture
def auth_manager():
    """Create auth manager for testing."""
    return AuthManager()


@pytest.fixture
def fixture_generator():
    """Create fixture generator with test fixtures."""
    generator = FixtureGenerator()
    generator.add_fixture(
        name="resource_id",
        var_type="dynamic",
        scope="module",
        docstring="Resource ID from create response",
    )
    return generator


class TestVariableDependency:
    """Tests for variable dependency handling."""

    def test_dynamic_variable_handling(self, tmp_path: Path, auth_manager, fixture_generator):
        """Test handling of dynamic variables between dependent tests."""
        # Setup test data
        create_request = {
            "name": "Create Resource",
            "request": {
                "method": "POST",
                "url": {"raw": "{{env_url}}/api/resources"},
                "body": {
                    "mode": "raw",
                    "raw": "{\"name\": \"{{resource_name}}\"}",
                },
            },
            "sets": ["resource_id"],  # This test sets the resource_id variable
        }

        view_request = {
            "name": "View Resource",
            "request": {
                "method": "GET",
                "url": {"raw": "{{env_url}}/api/resources/{{resource_id}}"},
            },
            "uses_variables": {
                "resource_id": {"type": "dynamic"},
            },
        }

        dependencies = [{
            "endpoint": "Create Resource",
            "request": create_request["request"],
            "sets": ["resource_id"],
        }]

        variables = {"resource_id": ["Create Resource"]}

        # Generate test content
        generator = ContentGenerator(auth_manager)
        content = generator.generate_test_content(
            view_request,
            dependencies,
            variables,
            fixture_generator,
        )

        # Verify generated content
        assert "_variable_store: Dict[str, Any] = {}" in content
        assert "RESOURCE_ID = os.getenv('RESOURCE_ID')" not in content
        assert '@pytest.fixture(scope="module")' in content
        assert "def resource_id():" in content
        assert "_variable_store['resource_id'] = response_data['Id']" in content
        assert "def test_test_view_resource(auth_session, env_url, tls_verify, resource_id):" in content
        assert "/resources/{resource_id}" in content
        assert "@pytest.mark.dependency(depends=[" in content
