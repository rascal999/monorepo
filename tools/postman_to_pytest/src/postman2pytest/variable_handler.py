"""Variable extraction and management utilities."""

import re
import json
import datetime
from pathlib import Path
from typing import Set, Dict, Optional, Any, Union, List
from dataclasses import dataclass
from enum import Enum

class VariableSource(Enum):
    """Source types for variables in registry."""
    VALUE = "value"        # Variables defined directly in registry
    FIXTURE = "fixture"    # Variables from pytest fixtures
    RESPONSE = "response"  # Variables extracted from HTTP responses
    COLLECTION = "collection"  # Variables from Postman collection
    RANDOM = "random"      # Variables generated using Faker methods

class VariableType(Enum):
    """Types of variables in Postman collections."""
    DOMAIN = "domain"    # Base URL, environment URLs
    PATH = "path"        # URL path parameters
    QUERY = "query"      # Query parameters
    HEADER = "header"    # Header variables
    BODY = "body"        # Request body variables
    AUTH = "auth"        # Authentication related
    UNKNOWN = "unknown"  # Unclassified variables

@dataclass
class Variable:
    """Represents a variable extracted from Postman collection."""
    name: str
    type: VariableType
    default_value: Optional[str] = None
    description: Optional[str] = None
    required: bool = True

def is_domain_variable(name: str) -> bool:
    """Check if variable name indicates a domain/URL variable."""
    domain_indicators = {'url', 'domain', 'host', 'baseurl', 'base_url', 'api'}
    name_lower = name.lower()
    return any(indicator in name_lower for indicator in domain_indicators)

def classify_variable(name: str, context: Optional[str] = None) -> VariableType:
    """Classify variable type based on name and context.
    
    Args:
        name: Variable name
        context: Optional context where variable was found (url, header, etc.)
        
    Returns:
        VariableType indicating the classified type
    """
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
    """Extract Postman variables from text or PostmanItem.
    
    Args:
        source: Text containing variables or PostmanItem to extract from
        context: Optional context where variables were found
        
    Returns:
        Dictionary mapping variable names to Variable objects
    """
    if isinstance(source, str):
        # First check for Postman dynamic variables (e.g., $randomFirstName)
        variables = {}
        for name in VariableRegistry.RANDOM_VAR_MAPPING.keys():
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
    """Extract potential default value for a variable from collection item.
    
    Args:
        item: PostmanItem or similar object containing request details
        variable_name: Name of variable to find default for
        
    Returns:
        Optional default value if found
    """
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
    """Generate .env file template with extracted variables.
    
    Args:
        variables: Dictionary of Variable objects
        output_path: Path to write .env file
    """
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

def replace_variables(text: str, variables: Dict[str, Variable], sanitize_func) -> str:
    """Replace Postman variables with Python format strings.
    
    Args:
        text: Text containing Postman variables
        variables: Set of variable names to replace
        sanitize_func: Function to sanitize variable names
        
    Returns:
        Text with variables replaced with Python format strings
    """
    result = text
    for var_name, var in variables.items():
        if var_name.startswith('$random'):  # Postman dynamic variable
            result = result.replace(
                var_name,  # Direct replacement without {{...}}
                "{" + var_name[1:] + "}"  # Remove $ prefix for Python identifiers
            )
        else:  # Regular Postman variable
            result = result.replace(
                f"{{{{{var_name}}}}}",  # Use original case from collection
                "{" + sanitize_func(var_name) + "}"  # Keep original case
            )
    return result

def collect_variables_from_request(item: 'PostmanItem') -> Dict[str, Variable]:
    """Extract all variables from a Postman request.
    
    Checks URL, headers, and body for variables.
    
    Args:
        item: PostmanItem containing the request
        
    Returns:
        Dictionary mapping variable names to Variable objects
    """
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

@dataclass
class RegistryVariable:
    """Variable entry in the registry."""
    source: VariableSource
    fixture: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None
    response_pattern: Optional[Dict[str, str]] = None
    faker_method: Optional[str] = None  # Faker method to use for random generation

class VariableRegistry:
    """Manages variable registry for postman2pytest."""
    
    def __init__(self, collection_name: str = "", collection_version: str = ""):
        self.variables: Dict[str, RegistryVariable] = {}
        self.collection_name = collection_name
        self.collection_version = collection_version

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

    def add_variable(self, name: str, var_type: VariableType, default_value: Optional[str] = None,
                    description: Optional[str] = None) -> None:
        """Add variable to registry with appropriate source type."""
        # Check if this is a random variable from Postman
        if name in self.RANDOM_VAR_MAPPING:
            source = VariableSource.RANDOM
            fixture_name = None
            faker_method = self.RANDOM_VAR_MAPPING[name]
        # Determine source type based on variable type and value
        elif var_type in [VariableType.AUTH, VariableType.DOMAIN] and default_value:
            # Auth and domain variables with values are stored directly
            source = VariableSource.VALUE
            fixture_name = None
            faker_method = None
        else:
            # Other variables default to fixture
            source = VariableSource.FIXTURE
            fixture_name = f"{name.lower()}_fixture"
            faker_method = None
        
        # Create response pattern template if it's a response-type variable
        response_pattern = None
        if var_type in [VariableType.BODY, VariableType.QUERY]:
            response_pattern = {
                "regex": f'"{name}":\\s*"([^"]+)"',
                "group": 1,
                "description": f"Extracts {name} from response"
            }
        
        self.variables[name] = RegistryVariable(
            source=source,
            fixture=fixture_name,
            value=default_value,
            description=description or f"Variable {name} ({var_type.value})",
            response_pattern=response_pattern,
            faker_method=faker_method
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert registry to dictionary format."""
        return {
            "variables": {
                name: {
                    "source": var.source.value,
                    "fixture": var.fixture,
                    "value": var.value,
                    "description": var.description,
                    "response_pattern": var.response_pattern,
                    "faker_method": var.faker_method
                }
                for name, var in self.variables.items()
            },
            "metadata": {
                "generated_from": self.collection_name,
                "generated_at": datetime.datetime.utcnow().isoformat(),
                "postman_collection_version": self.collection_version
            },
            "sources": {
                "value": "Variables defined directly in registry",
                "fixture": "Variables provided by pytest fixtures (default for new variables)",
                "response": "Variables extracted from HTTP responses using regex",
                "collection": "Variables defined in Postman collection",
                "random": "Variables generated using Faker methods (see https://faker.readthedocs.io/en/master/providers.html for available methods)"
            }
        }

    def save(self, path: Path, overwrite: bool = False) -> bool:
        """Save registry to file if it doesn't exist or overwrite is True."""
        if path.exists() and not overwrite:
            return False
            
        with path.open('w') as f:
            json.dump(self.to_dict(), f, indent=4)
        return True

    @classmethod
    def load(cls, path: Path) -> Optional['VariableRegistry']:
        """Load registry from file if it exists."""
        if not path.exists():
            return None
            
        try:
            data = json.loads(path.read_text())
            registry = cls(
                collection_name=data.get("metadata", {}).get("generated_from", ""),
                collection_version=data.get("metadata", {}).get("postman_collection_version", "")
            )
            
            for name, var_data in data.get("variables", {}).items():
                registry.variables[name] = RegistryVariable(
                    source=VariableSource(var_data.get("source", "fixture")),
                    fixture=var_data.get("fixture"),
                    value=var_data.get("value"),
                    description=var_data.get("description"),
                    response_pattern=var_data.get("response_pattern"),
                    faker_method=var_data.get("faker_method")
                )
            
            return registry
        except Exception:
            return None

    def merge_variables(self, variables: Dict[str, Variable]) -> None:
        """Merge new variables from collection with existing registry.
        
        Only adds variables that don't exist in registry.
        """
        for name, var in variables.items():
            if name not in self.variables:
                self.add_variable(name, var.type, var.default_value, var.description)

    @classmethod
    def from_variables(cls, variables: Dict[str, Variable], 
                      collection_name: str = "", 
                      collection_version: str = "") -> 'VariableRegistry':
        """Create registry from Variable dictionary."""
        registry = cls(collection_name, collection_version)
        for name, var in variables.items():
            registry.add_variable(name, var.type, var.default_value, var.description)
        return registry

def generate_variable_registry(variables: Dict[str, Variable], 
                             output_path: Path,
                             collection_name: str = "",
                             collection_version: str = "",
                             overwrite: bool = False) -> None:
    """Generate variable registry JSON file.
    
    If registry exists, merges new variables with existing ones.
    If registry doesn't exist, creates new one.
    
    Args:
        variables: Dictionary of Variable objects
        output_path: Path to write registry file
        collection_name: Name of Postman collection
        collection_version: Version of Postman collection
        overwrite: Whether to overwrite existing registry
    """
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
