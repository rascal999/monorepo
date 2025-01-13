"""Variable registry management."""

import json
import datetime
from pathlib import Path
from typing import Dict, Optional, Any
from .variable_types import Variable, VariableType, VariableSource, RegistryVariable


class VariableRegistry:
    """Manages variable registry for postman2pytest."""
    
    def __init__(self, collection_name: str = "", collection_version: str = ""):
        self.variables: Dict[str, RegistryVariable] = {}
        self.collection_name = collection_name
        self.collection_version = collection_version

    def add_variable(self, name: str, var_type: VariableType, default_value: Optional[str] = None,
                    description: Optional[str] = None, source_test: Optional[str] = None,
                    source_file: Optional[str] = None) -> None:
        """Add variable to registry with appropriate source type."""
        # Check if this is a random variable from Postman
        if name in RANDOM_VAR_MAPPING:
            source = VariableSource.RANDOM
            fixture_name = None
            faker_method = RANDOM_VAR_MAPPING[name]
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
        if var_type == VariableType.PATH:
            # For path variables, extract from Id field in response
            response_pattern = {
                "regex": f'"Id":\\s*"([^"]+)"',
                "group": 1,
                "source_test": source_test,
                "source_file": source_file,
                "description": f"Extracts {name} from response Id field"
            }
        elif var_type in [VariableType.BODY, VariableType.QUERY]:
            response_pattern = {
                "regex": f'"{name}":\\s*"([^"]+)"',
                "group": 1,
                "source_test": source_test,
                "source_file": source_file,
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
        """Merge new variables from collection with existing registry."""
        for name, var in variables.items():
            if name not in self.variables:
                self.add_variable(
                    name, 
                    var.type, 
                    var.default_value, 
                    var.description,
                    var.source_test,
                    var.source_file
                )

    @classmethod
    def from_variables(cls, variables: Dict[str, Variable], 
                      collection_name: str = "", 
                      collection_version: str = "") -> 'VariableRegistry':
        """Create registry from Variable dictionary."""
        registry = cls(collection_name, collection_version)
        for name, var in variables.items():
            registry.add_variable(
                name, 
                var.type, 
                var.default_value, 
                var.description,
                var.source_test,
                var.source_file
            )
        return registry


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
