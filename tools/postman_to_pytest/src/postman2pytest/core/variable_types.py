"""Variable type definitions."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any


class VariableType(Enum):
    """Types of variables found in Postman requests."""
    UNKNOWN = "unknown"
    PATH = "path"
    QUERY = "query"
    HEADER = "header"
    BODY = "body"
    AUTH = "auth"
    DOMAIN = "domain"


class VariableSource(Enum):
    """Source types for variables in registry."""
    VALUE = "value"  # Direct value in registry
    FIXTURE = "fixture"  # Value from pytest fixture
    RANDOM = "random"  # Random value using Faker
    COLLECTION = "collection"  # Value from Postman collection


@dataclass
class Variable:
    """Represents a variable found in a Postman request."""
    name: str
    type: VariableType = VariableType.UNKNOWN
    description: Optional[str] = None
    default_value: Optional[str] = None
    source_test: Optional[str] = None  # Test that provides this variable
    source_file: Optional[str] = None  # File containing source test


@dataclass
class RegistryVariable:
    """Represents a variable in the registry."""
    source: VariableSource
    fixture: Optional[str] = None  # Name of pytest fixture
    value: Optional[str] = None  # Direct value if source is VALUE
    description: Optional[str] = None
    response_pattern: Optional[Dict[str, Any]] = None  # For extracting from responses
    faker_method: Optional[str] = None  # For random values
