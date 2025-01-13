"""Variable extraction and classification utilities."""

import re
from typing import Dict, Optional, Union, Any
from .variable_types import Variable, VariableType

def is_domain_variable(name: str) -> bool:
    """Check if variable name indicates a domain/URL variable."""
    domain_indicators = {'url', 'domain', 'host', 'baseurl', 'base_url', 'api'}
    name_lower = name.lower()
    return any(indicator in name_lower for indicator in domain_indicators)

def classify_variable(name: str, context: Optional[str] = None) -> VariableType:
    """Classify variable type based on name and context."""
    name_lower = name.lower()
    
    if is_domain_variable(name):
        return VariableType.DOMAIN
        
    if context:
        context_lower = context.lower()
        if 'url' in context_lower:
            return VariableType.PATH
        if 'header' in context_lower:
            return VariableType.HEADER
        if 'body' in context_lower:
            return VariableType.BODY
        if any(auth in context_lower for auth in ['auth', 'token', 'key']):
            return VariableType.AUTH
            
    # Try to classify based on name patterns
    if any(q in name_lower for q in ['query', 'param', 'filter']):
        return VariableType.QUERY
    if any(p in name_lower for p in ['path', 'route']):
        return VariableType.PATH
    if any(h in name_lower for h in ['header', 'content-type', 'accept']):
        return VariableType.HEADER
    if any(a in name_lower for a in ['auth', 'token', 'key', 'secret', 'password']):
        return VariableType.AUTH
        
    return VariableType.UNKNOWN

def extract_variables(source: Union[str, Any], context: Optional[str] = None) -> Dict[str, Variable]:
    """Extract Postman variables from text or PostmanItem."""
    if isinstance(source, str):
        # First check for Postman dynamic variables (e.g., $randomFirstName)
        variables = {}
        for name in RANDOM_VAR_MAPPING.keys():
            if name in source:
                variables[name] = Variable(
                    name=name,
                    type=VariableType.BODY if context == 'body' else VariableType.UNKNOWN,
                    description=f"Random {name[7:].lower()} using Faker"  # Remove '$random' prefix
                )
        
        # Then check for regular variables in {{...}} syntax
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.finditer(pattern, source)
        for match in matches:
            # Keep original case from Postman collection
            name = match.group(1)
            var_type = classify_variable(name, context)
            variables[name] = Variable(
                name=name,  # Preserve original case
                type=var_type
            )
        
        return variables
    else:
        # Handle PostmanItem - avoid circular import by checking attributes
        if hasattr(source, 'request'):
            return collect_variables_from_request(source)
        return {}

def extract_default_value(item: Any, variable_name: str) -> Optional[str]:
    """Extract potential default value for a variable from collection item."""
    # Check collection variables
    if hasattr(item, 'variable'):
        for var in item.variable:
            if var.key == variable_name:
                return var.value
                
    # Check environment defaults
    if hasattr(item, 'environment') and item.environment:
        for env_var in item.environment:
            if env_var.key == variable_name:
                return env_var.value
    
    return None

def collect_variables_from_request(item: 'PostmanItem') -> Dict[str, Variable]:
    """Extract all variables from a Postman request."""
    variables = {}
    
    # Check URL
    url = item.request.url.raw if isinstance(item.request.url, str) else item.request.url.raw
    url_vars = extract_variables(url, context='url')
    variables.update(url_vars)
    
    # Check headers
    if item.request.header:
        for header in item.request.header:
            if not header.disabled:
                header_vars = extract_variables(header.value, context='header')
                variables.update(header_vars)
    
    # Check body
    if item.request.body and item.request.body.raw:
        body_vars = extract_variables(item.request.body.raw, context='body')
        variables.update(body_vars)
    
    # Extract default values where possible
    for var_name in variables:
        default_value = extract_default_value(item, var_name)
        if default_value:
            variables[var_name].default_value = default_value
    
    return variables

# Map Postman random variables to Faker methods
RANDOM_VAR_MAPPING = {
    "$randomFirstName": "first_name",
    "$randomLastName": "last_name",
    "$randomFullName": "name",
    "$randomEmail": "email",
    "$randomStreetAddress": "street_address",
    "$randomStreetName": "street_name",
    "$randomCity": "city",
    "$randomCountryCode": "country_code",
    "$randomCountry": "country",
    "$randomPhoneNumber": "phone_number",
    "$randomInt": "random_int",
    "$randomUUID": "uuid4",
    "$randomIP": "ipv4",
    "$randomIPV6": "ipv6",
    "$randomPassword": "password",
    "$randomCompanyName": "company",
    "$randomUrl": "url",
    "$randomDomainName": "domain_name",
    "$randomUserName": "user_name",
    "$randomProtocol": "random_element",  # ['http', 'https', 'ftp', 'sftp']
    "$randomPort": "port_number",
    "$randomMACAddress": "mac_address",
    "$randomGUID": "uuid4",
    "$randomJobTitle": "job",
    "$randomJobArea": "job",
    "$randomJobType": "job",
    "$randomDatetime": "datetime",
    "$randomDate": "date",
    "$randomTime": "time",
    "$randomFileExt": "file_extension",
    "$randomFileName": "file_name",
    "$randomFilePath": "file_path",
    "$randomMimeType": "mime_type",
    "$randomImageUrl": "image_url",
    "$randomWords": "words",
    "$randomWord": "word",
    "$randomSentence": "sentence",
    "$randomParagraph": "paragraph",
}
