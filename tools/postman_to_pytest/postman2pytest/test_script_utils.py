"""
Utilities for converting Postman test scripts to pytest assertions.
"""
import re
from typing import List, Dict, Any
from pyjsparser import parse

def _process_js_node(node: Dict) -> str:
    """Process JavaScript AST node."""
    if node['type'] == 'MemberExpression':
        if node['object'].get('name') == 'response':
            # Handle response.Id
            if 'name' in node['property']:
                return f'response_data["{node["property"]["name"]}"]'
        elif (node['object'].get('type') == 'CallExpression' and
              node['object'].get('callee', {}).get('type') == 'MemberExpression' and
              node['object']['callee']['object'].get('name') == 'response' and
              node['object']['callee']['property'].get('name') == 'json'):
            # Handle response.json().Id
            return f'response.json()["{node["property"]["name"]}"]'
    elif node['type'] == 'Literal':
        return repr(node['value'])
    return None

def convert_test_script(script: Dict[str, Any], request_name: str, url: str) -> List[str]:
    """Convert Postman test script to pytest assertions."""
    js_code = script.get('exec', [])
    if not js_code:
        return []
    
    # Join all lines and normalize whitespace
    js_code = ' '.join(line.strip() for line in js_code if line.strip())
    
    assertions = []
    try:
        # Parse JavaScript code
        ast = parse(js_code)
        for node in ast['body']:
            if node['type'] == 'IfStatement':
                test = node['test']
                # Handle if (pm.response.code === 200) { ... }
                if (test['type'] == 'BinaryExpression' and
                    test['left']['type'] == 'MemberExpression' and
                    test['left']['object']['type'] == 'MemberExpression' and
                    test['left']['object']['object'].get('name') == 'pm' and
                    test['left']['object']['property'].get('name') == 'response' and
                    test['left']['property'].get('name') == 'code'):
                    
                    assertions.append('assert response.status_code == 200')
                    assertions.append('if response.status_code == 200:')
                    assertions.append('    response_data = response.json()')
                    
                    # Process the if block body
                    if node['consequent']['type'] == 'BlockStatement':
                        for stmt in node['consequent']['body']:
                            if stmt['type'] == 'ExpressionStatement':
                                expr = stmt['expression']
                                if expr['type'] == 'CallExpression':
                                    # Handle pm.environment.set() or pm.variables.set()
                                    callee = expr['callee']
                                    if (callee['type'] == 'MemberExpression' and
                                        callee['object']['type'] == 'MemberExpression' and
                                        callee['object']['object'].get('name') == 'pm' and
                                        callee['object']['property'].get('name') in ('environment', 'variables') and
                                        callee['property'].get('name') == 'set'):
                                        
                                        var_name = expr['arguments'][0]['value']
                                        value_node = expr['arguments'][1]
                                        value_expr = _process_js_node(value_node)
                                        if value_expr:
                                            assertions.append(f'    dynamic_vars["{var_name}"] = {value_expr}')
    except Exception as e:
        print(f"Warning: Failed to parse JavaScript: {js_code}")
        print(f"Error: {str(e)}")
    
    return assertions
