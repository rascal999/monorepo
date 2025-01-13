"""Variable handling utilities."""

import re
from pathlib import Path
from typing import Dict, Optional
from .variable_types import Variable, VariableType
from .parser import PostmanItem


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


def extract_variables(source: str, context: Optional[str] = None) -> Dict[str, Variable]:
    """Extract variables from text with {{variable}} syntax."""
    variables = {}
    
    # First check for Postman dynamic variables (e.g., $randomFirstName)
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


def collect_variables_from_request(item: PostmanItem) -> Dict[str, Variable]:
    """Extract all variables from a Postman request."""
    variables = {}
    
    # Check URL
    url = item.request.url.raw if isinstance(item.request.url, str) else item.request.url.raw
    url_vars = extract_variables(url, context='url')
    variables.update(url_vars)
    
    # Check headers
    if item.request.header:
        for header in item.request.header:
            if isinstance(header, dict) and not header.get('disabled', False):
                header_vars = extract_variables(header.get('value', ''), context='header')
                variables.update(header_vars)
    
    # Check body
    if item.request.body:
        if isinstance(item.request.body, dict) and 'raw' in item.request.body:
            body_vars = extract_variables(item.request.body['raw'], context='body')
            variables.update(body_vars)
    
    # Extract default values where possible
    for var_name in variables:
        default_value = extract_default_value(item, var_name)
        if default_value:
            variables[var_name].default_value = default_value
    
    return variables


def extract_default_value(item: PostmanItem, variable_name: str) -> Optional[str]:
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


def generate_env_file(variables: Dict[str, Variable], output_path: Path) -> None:
    """Generate .env file template with extracted variables."""
    env_content = []
    
    # Group variables by type
    by_type = {}
    for var in variables.values():
        if var.type not in by_type:
            by_type[var.type] = []
        by_type[var.type].append(var)
    
    # Generate sections by type
    for var_type in VariableType:
        if var_type in by_type:
            env_content.append(f"\n# {var_type.value.upper()} Variables")
            for var in sorted(by_type[var_type], key=lambda x: x.name):
                if var.description:
                    env_content.append(f"# {var.description}")
                default = f"={var.default_value}" if var.default_value else ""
                env_content.append(f"{var.name.upper()}{default}")
    
    # Write to file
    output_path.write_text("\n".join(env_content))


def generate_variable_registry(variables: Dict[str, Variable], 
                             output_path: Path,
                             collection_name: str = "",
                             collection_version: str = "",
                             overwrite: bool = False) -> None:
    """Generate variable registry JSON file."""
    from .variable_registry import VariableRegistry
    
    # Try to load existing registry
    registry = VariableRegistry.load(output_path)
    if registry:
        # Merge new variables with existing registry
        registry.merge_variables(variables)
    else:
        # Create new registry
        registry = VariableRegistry.from_variables(variables, collection_name, collection_version)
    
    # Save registry
    registry.save(output_path, overwrite)


def copy_variable_registry(src_path: Path, dest_path: Path) -> None:
    """Copy variable registry to destination if source exists."""
    if src_path.exists():
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(src_path.read_text())


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
