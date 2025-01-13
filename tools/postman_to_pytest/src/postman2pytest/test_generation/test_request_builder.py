"""Request building utilities for test generation."""

import json
import logging
import re
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

def build_headers(item: 'PostmanItem', auth_config: Optional[dict] = None) -> Dict[str, str]:
    """Build request headers from Postman request."""
    headers = {}
    
    # Extract headers from Postman request
    if hasattr(item.request, 'header') and item.request.header:
        for header in item.request.header:
            if isinstance(header, dict) and not header.get('disabled', False):
                headers[header.get('key', '')] = header.get('value', '')

    # Add Content-Type for JSON if not present
    if item.request.body and isinstance(item.request.body, dict) and 'raw' in item.request.body:
        is_json = False
        # Check if mode is raw and options indicate JSON
        if (item.request.body.get('mode') == 'raw' and
            'options' in item.request.body and 
            item.request.body['options'].get('raw', {}).get('language') == 'json'):
            is_json = True
        # Fallback: try to parse as JSON
        if not is_json:
            try:
                # Try to fix common JSON formatting issues
                raw_json = item.request.body['raw']
                # Replace single quotes with double quotes
                raw_json = raw_json.replace("'", '"')
                # Add quotes around unquoted property names
                raw_json = re.sub(r'(\s*)(\w+)(\s*):([^:])', r'\1"\2"\3:\4', raw_json)
                # Try to parse the fixed JSON
                json.loads(raw_json)
                is_json = True
            except (json.JSONDecodeError, KeyError):
                pass
        
        if is_json and 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'

    return headers

def prepare_request_body(item: 'PostmanItem') -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Prepare request body and determine content type."""
    if not (item.request.body and isinstance(item.request.body, dict) and 'raw' in item.request.body):
        return None, None

    # Check request mode and options
    mode = item.request.body.get('mode', 'raw')
    is_json = (mode == 'raw' and 
              'options' in item.request.body and 
              item.request.body['options'].get('raw', {}).get('language') == 'json')
    
    if mode == 'urlencoded' and not is_json:
        # Handle form data
        form_data = {}
        pairs = item.request.body['raw'].split('&')
        for pair in pairs:
            key, value = pair.split('=', 1)
            if key in form_data:
                if not isinstance(form_data[key], list):
                    form_data[key] = [form_data[key]]
                form_data[key].append(value)
            else:
                form_data[key] = value
        return 'application/x-www-form-urlencoded', form_data
    else:
        # Handle raw/JSON data
            try:
                # Try to fix common JSON formatting issues
                raw_json = item.request.body['raw']
                # Replace single quotes with double quotes
                raw_json = raw_json.replace("'", '"')
                # Add quotes around unquoted property names
                raw_json = re.sub(r'(\s*)(\w+)(\s*):([^:])', r'\1"\2"\3:\4', raw_json)
                # Try to parse the fixed JSON
                json_data = json.loads(raw_json)
                return 'application/json', json_data
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f'Failed to parse request body as JSON: {e}')
                return None, None

def generate_request_setup() -> str:
    """Generate code for request session setup."""
    return '''
    # Get request configuration
    verify = os.getenv('TLS_VERIFY', 'true').lower() == 'true'
    cert_path = os.getenv('CERT_PATH')
    verify_arg = cert_path if cert_path else verify

    # Get proxy settings
    http_proxy = os.getenv('HTTP_PROXY')
    https_proxy = os.getenv('HTTPS_PROXY')
    proxies = {
        'http': http_proxy,
        'https': https_proxy
    } if http_proxy or https_proxy else None
    logger.debug(f'Using proxy settings: {proxies}')

    # Create session with SSL verification and proxy
    with requests.Session() as session:
        session.verify = verify_arg
        logger.debug(f'SSL verification setting: verify_arg={verify_arg}, cert_path={cert_path}')

        if proxies:
            session.proxies = proxies
            logger.debug('Applied proxy settings to session')
'''.strip()

def generate_response_handling() -> str:
    """Generate code for response handling and logging."""
    return '''
        # Log response for variable extraction
        try:
            response_data = response.json()
            logger.debug(f'Response data for variable extraction: {json.dumps(response_data, indent=2)}')
            logger.debug(f'Response logged to {Path(__file__).resolve().parent.parent / "test_responses.log"}')
        except json.JSONDecodeError as e:
            logger.error(f'Failed to parse response as JSON: {e}')
            logger.debug(f'Raw response content: {response.text}')
        except Exception as e:
            logger.error(f'Unexpected error processing response: {e}')
'''.strip()

def generate_json_processor() -> str:
    """Generate code for processing JSON values with variables."""
    return '''
        # Process variables in the JSON structure
        def process_json_value(value):
            if isinstance(value, dict):
                return {k: process_json_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [process_json_value(v) for v in value]
            elif isinstance(value, str):
                if '{{' in value and '}}' in value:
                    var_name = value.split('{{')[1].split('}}')[0]
                    return resolve_variable(var_name)
                return value
            return value
'''.strip()
