#!/usr/bin/env python3
"""
Postman Dependency Graph Generator
Analyzes Postman collections to generate a text-based dependency graph
showing relationships between API endpoints based on variable usage.
"""

import json
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

def extract_script_variables(script: dict) -> Tuple[Set[str], Set[str]]:
    """Extract variables that are set and used in pre/post request scripts."""
    if not script or 'exec' not in script:
        return set(), set()

    code = '\n'.join(script['exec'])
    set_vars = set()
    used_vars = set()
    
    # Variables set in script
    lines = code.split('\n')
    for line in lines:
        # Check for variable assignments
        if 'pm.environment.set' in line or 'pm.variables.set' in line:
            try:
                var_name = line.split('"')[1]
                set_vars.add(var_name)
            except IndexError:
                continue
        
        # Check for variable usage
        if 'pm.environment.get' in line or 'pm.variables.get' in line:
            try:
                var_name = line.split('"')[1]
                used_vars.add(var_name)
            except IndexError:
                continue
        
        # Check for direct variable references
        if '{{' in line and '}}' in line:
            try:
                var_name = line.split('{{')[1].split('}}')[0]
                used_vars.add(var_name)
            except IndexError:
                continue
    
    return set_vars, used_vars

def extract_variables_from_string(text: str) -> Set[str]:
    """Extract all {{variable}} patterns from a string."""
    variables = set()
    start = 0
    while True:
        start = text.find('{{', start)
        if start == -1:
            break
        end = text.find('}}', start)
        if end == -1:
            break
        variables.add(text[start+2:end])
        start = end + 2
    return variables

def extract_url_variables(url: dict) -> Set[str]:
    """Extract variables from URL path and query parameters."""
    variables = set()
    
    # Handle URL string format
    if isinstance(url, str):
        return extract_variables_from_string(url)

    # Handle URL object format
    # Check raw URL if present
    raw_url = url.get('raw', '')
    if raw_url:
        variables.update(extract_variables_from_string(raw_url))

    # Check host array
    for host in url.get('host', []):
        if isinstance(host, str):
            variables.update(extract_variables_from_string(host))
    
    # Check path array
    for segment in url.get('path', []):
        if isinstance(segment, str):
            variables.update(extract_variables_from_string(segment))
    
    # Check query parameters
    for param in url.get('query', []):
        value = param.get('value', '')
        if isinstance(value, str):
            variables.update(extract_variables_from_string(value))
    
    return variables

def extract_body_variables(body: dict) -> Set[str]:
    """Extract variables from request body."""
    variables = set()
    
    if not body:
        return variables
    
    # Handle raw body
    raw = body.get('raw', '')
    if raw and isinstance(raw, str):
        variables.update(extract_variables_from_string(raw))
    
    # Handle form data
    formdata = body.get('formdata', [])
    if formdata:
        for item in formdata:
            value = item.get('value', '')
            if isinstance(value, str):
                variables.update(extract_variables_from_string(value))
    
    # Handle urlencoded data
    urlencoded = body.get('urlencoded', [])
    if urlencoded:
        for item in urlencoded:
            value = item.get('value', '')
            if isinstance(value, str):
                variables.update(extract_variables_from_string(value))
    
    return variables

def analyze_request_dependencies(item: dict) -> Tuple[Set[str], Set[str]]:
    """Analyze request for all variable dependencies including URL, body, and scripts."""
    set_vars = set()
    used_vars = set()
    
    if 'request' in item:
        request = item['request']
        
        # Check URL variables
        url = request.get('url', {})
        url_vars = extract_url_variables(url)
        used_vars.update(url_vars)
        
        # Check body variables
        body = request.get('body', {})
        body_vars = extract_body_variables(body)
        used_vars.update(body_vars)
    
    # Check pre-request script
    pre_request = next((script for script in item.get('event', [])
                       if script.get('listen') == 'prerequest'), None)
    if pre_request:
        pre_set, pre_used = extract_script_variables(pre_request.get('script', {}))
        set_vars.update(pre_set)
        used_vars.update(pre_used)
    
    # Check test script
    test_script = next((script for script in item.get('event', [])
                       if script.get('listen') == 'test'), None)
    if test_script:
        test_set, test_used = extract_script_variables(test_script.get('script', {}))
        set_vars.update(test_set)
        used_vars.update(test_used)
    
    return set_vars, used_vars

def consolidate_variable_sets(endpoint_data: Dict) -> List[str]:
    """Consolidate multiple variable sets into a single list."""
    all_vars = set()
    if 'sets_variables' in endpoint_data:
        for var in endpoint_data['sets_variables']:
            all_vars.add(var)
    return sorted(list(all_vars))

def analyze_collection(collection_path: str) -> Dict[str, Any]:
    """Analyze Postman collection and generate dependency text output."""
    with open(collection_path) as f:
        collection = json.load(f)
    
    # Store endpoint dependencies
    dependencies: Dict[str, Set[str]] = {}
    # Store variables set by each endpoint
    variables_set: Dict[str, Set[str]] = {}
    
    def process_item(item: dict, folder_path: str = ""):
        """Process a collection item (request or folder)."""
        if 'request' in item:
            # This is a request
            name = f"{folder_path}/{item['name']}" if folder_path else item['name']
            endpoint = f"{item['request'].get('method', 'GET')} {name}"
            
            # Analyze all dependencies including URL and scripts
            set_vars, used_vars = analyze_request_dependencies(item)
            
            # Store used and set variables
            dependencies[endpoint] = used_vars
            variables_set[endpoint] = set_vars
                
        elif 'item' in item:
            # This is a folder
            new_folder_path = f"{folder_path}/{item['name']}" if folder_path else item['name']
            for subitem in item['item']:
                process_item(subitem, new_folder_path)
    
    # Process all items in collection
    for item in collection['item']:
        process_item(item)
    
    # Generate YAML structure
    output = {
        "postman_collection_dependencies": {
            "endpoints": {}
        }
    }
    
    # Build endpoint dependencies
    for endpoint, used_vars in dependencies.items():
        endpoint_data = {}
        
        if used_vars:
            used_variables = {}
            for var in sorted(used_vars):
                # Find which endpoints set this variable
                # Find setters for this variable
                setters = [ep for ep, vars_set in variables_set.items() 
                          if var in vars_set and ep != endpoint]  # Exclude self-references
                
                if setters:
                    used_variables[var] = {
                        "type": "dynamic",
                        "set_by": sorted(setters)  # Sort for consistent output
                    }
                else:
                    used_variables[var] = {
                        "type": "environment"
                    }
            endpoint_data["uses_variables"] = used_variables
        
        # Get variables set by this endpoint
        vars_set = variables_set.get(endpoint, set())
        if vars_set:
            endpoint_data["sets_variables"] = sorted(list(vars_set))
        
        output["postman_collection_dependencies"]["endpoints"][endpoint] = endpoint_data
    
    return output

def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_collection.json>")
        sys.exit(1)
    
    collection_path = sys.argv[1]
    if not Path(collection_path).exists():
        print(f"Error: Collection file not found: {collection_path}")
        sys.exit(1)
    
    try:
        output = analyze_collection(collection_path)
        # Output YAML with proper formatting
        yaml_str = yaml.dump(output, sort_keys=False, allow_unicode=True, default_flow_style=False)
        print(yaml_str)
    except Exception as e:
        print(f"Error analyzing collection: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
