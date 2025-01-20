"""
Utilities for handling test dependencies.
"""
from typing import Dict, List, Set, Optional

def get_variable_setters(var_name: str, config: Dict) -> List[str]:
    """Get all requests that set a given variable."""
    setters = []
    for endpoint, deps in config.get('endpoints', {}).items():
        if var_name in deps.get('sets_variables', []):
            setters.append(endpoint)
    return setters

def get_variable_users(var_name: str, config: Dict) -> List[str]:
    """Get all requests that use a given variable."""
    users = []
    for endpoint, deps in config.get('endpoints', {}).items():
        var_deps = deps.get('uses_variables', {})
        if var_name in var_deps and var_deps[var_name].get('type') == 'dynamic':
            users.append(endpoint)
    return users

def find_related_requests(request_id: str, config: Dict) -> Set[str]:
    """Find all requests that share variables with a given request."""
    related = set()
    deps = config.get('endpoints', {}).get(request_id, {})
    
    # Add requests that set variables this request uses
    for var_name, var_info in deps.get('uses_variables', {}).items():
        if var_info.get('type') == 'dynamic':
            related.update(get_variable_setters(var_name, config))
    
    # Add requests that use variables this request sets
    for var_name in deps.get('sets_variables', []):
        related.update(get_variable_users(var_name, config))
    
    return related

def get_primary_request(request_id: str, config: Dict) -> Optional[str]:
    """Find the primary request that sets variables for a group of related requests."""
    deps = config.get('endpoints', {}).get(request_id, {})
    
    # If this request sets variables, it's the primary
    if deps.get('sets_variables'):
        return request_id
        
    # Otherwise, find the first request that sets any variable this request uses
    for var_name, var_info in deps.get('uses_variables', {}).items():
        if var_info.get('type') == 'dynamic':
            setters = get_variable_setters(var_name, config)
            if setters:
                return setters[0]
    
    return None
