"""
Generator module for creating pytest test files from Postman requests.
"""
import os
from typing import List, Set, Dict
from .parser import PostmanRequest
from .resolver import DependencyResolver
from .file_utils import (
    copy_env_file,
    copy_conftest_file,
    create_directory_structure,
    create_test_directory,
    normalize_path,
)
from .converter import (
    convert_test_script,
    convert_request_body,
    get_request_description,
    process_url,
)
from .name_utils import sanitize_name
from .dependency_utils import find_related_requests, get_primary_request

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
        raw_name = request.name  # Original name for dependencies
        func_name = f"test_{sanitize_name(request.name)}"  # Sanitized name for function
        
        # Add docstring and imports
        description = get_request_description(request.name, getattr(request, 'description', None))
        lines.extend([
            f'"""{description}"""',
            'import pytest',
            '',
            '',
        ])

        # Add dependency markers
        deps = resolver.get_dependencies(request)
        if deps:
            dep_names = [f"test_{sanitize_name(dep.name)}" for dep in deps]
            lines.append(f'@pytest.mark.dependency(depends={dep_names})')
        
        # Always add name marker for other tests to depend on
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
                assertions = convert_test_script(test, request.name, request.url)
                for assertion in assertions:
                    lines.append(f'    {assertion}')
        else:
            # Add default status code assertion if no specific tests
            lines.append('    assert response.status_code == 200')

        return lines

    def _get_output_path(self, request: PostmanRequest, primary_request: PostmanRequest, resolver: DependencyResolver) -> str:
        """Get the output path for a test file based on request path."""
        # Get dependencies and dependents
        deps = resolver.get_dependencies(request)
        dependents = resolver.get_dependents(request)
        
        # If this request has dependents, use its own name
        if dependents:
            filename = f"test_{sanitize_name(request.name)}.py"
        # If this request has dependencies, use the first dependency's name
        elif deps:
            filename = f"test_{sanitize_name(deps[0].name)}.py"
        # Otherwise use this request's name
        else:
            filename = f"test_{sanitize_name(request.name)}.py"
        
        # Always use all_mangopay_endpoints/users path
        path_parts = ["all_mangopay_endpoints", "users"]
        
        # Create path based on collection structure
        folder_path = create_test_directory(self.output_dir, path_parts)
        return os.path.join(folder_path, filename)

    def _write_test_file(self, output_path: str, lines: List[str], mode: str = 'w'):
        """Write or append lines to a test file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, mode) as f:
            if mode == 'a':
                f.write('\n\n')  # Add spacing between tests
            f.write('\n'.join(lines))

    def generate_test_files(self, requests: List[PostmanRequest], resolver: DependencyResolver):
        """Generate pytest test files for a collection of requests."""
        # Sort requests by dependency order
        ordered_requests, cycles = resolver.resolve_order()
        
        # Track which requests have been written
        written_requests = set()
        
        # Group requests by their dependencies
        dependency_groups: Dict[str, List[PostmanRequest]] = {}
        for request in ordered_requests:
            deps = resolver.get_dependencies(request)
            if deps:
                # Use the first dependency's name as the key
                key = deps[0].name
                if key not in dependency_groups:
                    dependency_groups[key] = []
                # Add dependency first if not already in group
                if deps[0] not in dependency_groups[key]:
                    dependency_groups[key].append(deps[0])
                # Then add the dependent request
                dependency_groups[key].append(request)
        
        # Write files for dependency groups
        for group_key, group_requests in dependency_groups.items():
            # Get output path using the dependent test's name (last request in group)
            output_path = os.path.join(
                create_test_directory(self.output_dir, ["all_mangopay_endpoints", "users"]),
                f"test_{sanitize_name(group_requests[-1].name)}.py"
            )
            
            # Write all tests in the group
            first = True
            for request in group_requests:
                if request not in written_requests:
                    lines = self._generate_test_function(request, resolver)
                    self._write_test_file(output_path, lines, 'w' if first else 'a')
                    written_requests.add(request)
                    first = False
        
        # Write files for standalone requests
        for request in ordered_requests:
            if request in written_requests:
                continue
                
            # Get output path using this request's name
            output_path = os.path.join(
                create_test_directory(self.output_dir, ["all_mangopay_endpoints", "users"]),
                f"test_{sanitize_name(request.name)}.py"
            )
            
            # Write the test
            lines = self._generate_test_function(request, resolver)
            self._write_test_file(output_path, lines, 'w')
            written_requests.add(request)
