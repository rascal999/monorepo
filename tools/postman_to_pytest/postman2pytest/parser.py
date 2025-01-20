"""
Parser module for handling Postman collections and dependency configurations.
"""

import json
import yaml
from typing import Dict, List, Any, Optional
from .name_utils import sanitize_name

class PostmanRequest:
    """Represents a Postman request with its test scripts and variables."""
    def __init__(self, name: str, method: str, url: str, body: Optional[Dict] = None,
                 headers: Optional[List[Dict]] = None, tests: Optional[List[Dict]] = None,
                 description: Optional[str] = None):
        self.name = name
        self.method = method
        self.url = url
        self.body = body or {}
        self.headers = headers or []
        self.tests = tests or []
        self.description = description
        self.path = []  # Store the full path to this request in the collection

    @property
    def endpoint_id(self) -> str:
        """Generate a unique identifier for this endpoint."""
        # Format matches YAML config: "METHOD Collection/Folder/Name"
        # Join all path components including the name
        full_path = self.path + [self.name]
        return f"{self.method} {'/'.join(full_path)}"

    @property
    def test_name(self) -> str:
        """Generate the test function name."""
        return f"test_{sanitize_name(self.name)}"

    @classmethod
    def from_dict(cls, data: Dict[str, Any], path: List[str]) -> Optional['PostmanRequest']:
        """Create a PostmanRequest instance from a dictionary."""
        if 'request' not in data:
            return None

        req_data = data['request']
        name = data.get('name', '')
        method = req_data.get('method', 'GET')
        url = req_data.get('url', {}).get('raw', '') if isinstance(req_data.get('url'), dict) else req_data.get('url', '')
        # Handle request body
        body_data = req_data.get('body', {})
        if isinstance(body_data, dict):
            # If it's a dict with mode=raw, get the raw content
            if body_data.get('mode') == 'raw':
                raw_content = body_data.get('raw', '')
                # Try to parse raw content as JSON if it's a string
                if isinstance(raw_content, str):
                    try:
                        # Parse JSON and keep it as raw dict
                        body = {'mode': 'raw', 'raw': json.loads(raw_content)}
                    except json.JSONDecodeError:
                        # If parsing fails, keep as string
                        body = {'mode': 'raw', 'raw': raw_content}
                else:
                    # If raw content is already parsed, use it
                    body = {'mode': 'raw', 'raw': raw_content}
            else:
                body = body_data
        else:
            # If it's not a dict, wrap it in the expected format
            body = {'mode': 'raw', 'raw': body_data}
        headers = req_data.get('header', [])

        # Extract test scripts
        tests = []
        for event in data.get('event', []):
            if event.get('listen') == 'test':
                tests.append(event.get('script', {}))

        # Extract description from item level
        description = data.get('description', '')
        
        request = cls(name, method, url, body, headers, tests, description)
        request.path = path  # Store the full path from collection
        return request

class DependencyConfig:
    """Represents the dependency configuration for endpoints."""
    def __init__(self, data: Dict[str, Any]):
        self.endpoints = data.get('postman_collection_dependencies', {}).get('endpoints', {})

    def get_dependencies(self, endpoint_id: str) -> Dict[str, Any]:
        """Get dependency information for an endpoint."""
        # Try exact match first
        deps = self.endpoints.get(endpoint_id, {})
        if deps:
            return deps
            
        # Try without method prefix
        if ' ' in endpoint_id:
            _, path = endpoint_id.split(' ', 1)
            return self.endpoints.get(path, {})
        return {}

    def get_variable_dependencies(self, endpoint_id: str) -> Dict[str, Dict[str, Any]]:
        """Get variables used by an endpoint and their sources."""
        deps = self.get_dependencies(endpoint_id)
        var_deps = deps.get('uses_variables', {})
        
        # Normalize dependency names in set_by lists
        for var_info in var_deps.values():
            if var_info.get('type') == 'dynamic' and 'set_by' in var_info:
                # Extract just the name part from the full path
                var_info['set_by'] = [
                    dep.split('/')[-1]
                    for dep in var_info['set_by']
                ]
        
        return var_deps

    def get_set_variables(self, endpoint_id: str) -> List[str]:
        """Get variables set by an endpoint."""
        deps = self.get_dependencies(endpoint_id)
        return deps.get('sets_variables', [])

def parse_postman_collection(collection_path: str) -> List[PostmanRequest]:
    """Parse a Postman collection file and return a list of requests."""
    with open(collection_path) as f:
        collection = json.load(f)

    requests = []
    
    def process_items(items: List[Dict], current_path: List[str]):
        for item in items:
            if 'item' in item:
                # This is a folder
                process_items(item['item'], current_path + [item['name']])
            else:
                # This is a request
                request = PostmanRequest.from_dict(item, current_path)
                if request:
                    requests.append(request)

    # Start processing from the root items
    process_items(collection.get('item', []), [])
    return requests

def parse_dependency_config(config_path: str) -> DependencyConfig:
    """Parse a dependency configuration YAML file."""
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return DependencyConfig(config)
