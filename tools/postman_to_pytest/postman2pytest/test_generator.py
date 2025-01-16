"""
Generator module for creating pytest test files from Postman requests.
"""
import os
from typing import List
from .parser import PostmanRequest
from .resolver import DependencyResolver
from .file_utils import (
    copy_env_file,
    copy_conftest_file,
    create_directory_structure,
    create_test_directory,
)
from .converter import (
    sanitize_name,
    convert_test_script,
    convert_request_body,
    get_request_description,
    process_url,
)

class TestGenerator:
    """Generates pytest test files from Postman requests."""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy required files and create directory structure
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        copy_env_file(base_dir, output_dir)
        copy_conftest_file(base_dir, output_dir)
        create_directory_structure(output_dir)

    def _generate_test_function(self, request: PostmanRequest, resolver: DependencyResolver) -> List[str]:
        """Generate a pytest test function for a Postman request."""
        lines = []
        func_name = sanitize_name(request.name)
        
        # Add docstring
        description = get_request_description(request.name, getattr(request, 'description', None))
        lines.extend([
            f'"""{description}"""',
            'import pytest',
            '',
            '',
        ])

        # Add dependency marker
        lines.append(f'@pytest.mark.dependency(name="{func_name}")')
        
        # Add function definition
        lines.append(f'def {func_name}(api_session, env_vars, faker_vars, dynamic_vars):')
        lines.append(f'    """{description}"""')

        # Process URL
        lines.append(process_url(request.url))
        lines.append('')

        # Process request body if present
        if request.body:
            body_lines = convert_request_body(request.body)
            if body_lines:
                lines.append(body_lines)
                lines.append('')

        # Make the request
        if request.body and request.method.upper() != 'GET':
            lines.append(f'    response = api_session.{request.method.lower()}(url, json=body)')
        else:
            lines.append(f'    response = api_session.{request.method.lower()}(url)')

        # Add assertions
        if request.tests:
            for test in request.tests:
                assertions = convert_test_script(test)
                lines.extend(f'    {assertion}' for assertion in assertions)
        else:
            # Add default status code assertion if no specific tests
            lines.append('    assert response.status_code == 200')

        return lines

    def _get_output_path(self, request: PostmanRequest) -> str:
        """Get the output path for a test file based on request path."""
        if not request.path:
            return os.path.join(self.output_dir, f'test_{sanitize_name(request.name)}.py')
        
        # Create path based on collection structure
        folder_path = create_test_directory(self.output_dir, request.path[:-1])
        return os.path.join(folder_path, f'test_{sanitize_name(request.path[-1])}.py')

    def generate_test_file(self, request: PostmanRequest, resolver: DependencyResolver):
        """Generate a pytest test file for a single request."""
        lines = self._generate_test_function(request, resolver)
        
        # Write the test file
        output_path = self._get_output_path(request)
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))

    def generate_test_files(self, requests: List[PostmanRequest], resolver: DependencyResolver):
        """Generate pytest test files for a collection of requests."""
        # Generate test files in dependency order
        ordered_requests = resolver.resolve_order()
        for request in ordered_requests:
            self.generate_test_file(request, resolver)
