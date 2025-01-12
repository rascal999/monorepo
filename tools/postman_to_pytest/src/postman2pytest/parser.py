"""Parser module for Postman collection JSON files."""

from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class RequestUrl(BaseModel):
    """Postman request URL model."""
    raw: str
    protocol: Optional[str] = None
    host: Optional[List[str]] = None
    path: Optional[List[str]] = None
    query: Optional[List[Dict[str, str]]] = None


class RequestBody(BaseModel):
    """Postman request body model."""
    mode: Optional[str] = None
    raw: Optional[str] = None
    formdata: Optional[List[Dict[str, str]]] = None
    urlencoded: Optional[List[Dict[str, str]]] = None


class HeaderItem(BaseModel):
    """Postman header item model."""
    key: str
    value: str
    disabled: Optional[Union[bool, str]] = None
    description: Optional[str] = None


class Request(BaseModel):
    """Postman request model."""
    method: str
    url: Union[str, RequestUrl]
    description: Optional[str] = None
    header: Optional[List[HeaderItem]] = None
    body: Optional[RequestBody] = None
    auth: Optional[Dict] = None


class PostmanItem(BaseModel):
    """Postman collection item model."""
    name: str
    request: Optional[Request] = None
    response: Optional[List[Dict]] = None
    event: Optional[List[Dict]] = None
    item: Optional[List[Union['PostmanItemGroup', 'PostmanItem']]] = None


class PostmanItemGroup(BaseModel):
    """Postman collection item group model."""
    name: str
    item: Optional[List[Union['PostmanItemGroup', PostmanItem]]] = Field(default_factory=list)
    auth: Optional[Dict] = None
    event: Optional[List[Dict]] = None


class PostmanCollection(BaseModel):
    """Postman collection model."""
    info: Dict
    item: List[Union[PostmanItemGroup, PostmanItem]]
    auth: Optional[Dict] = None
    event: Optional[List[Dict]] = None


def parse_collection(file_path: Path) -> PostmanCollection:
    """Parse a Postman collection JSON file.

    Args:
        file_path: Path to the Postman collection JSON file

    Returns:
        PostmanCollection object representing the parsed collection

    Raises:
        ValueError: If the file is not a valid Postman collection
        FileNotFoundError: If the file does not exist
        JSONDecodeError: If the file is not valid JSON
    """
    try:
        json_data = file_path.read_text()
        collection = PostmanCollection.model_validate_json(json_data)
        return collection
    except FileNotFoundError:
        raise FileNotFoundError(f"Collection file not found: {file_path}")
    except Exception as e:
        error_msg = f"Failed to parse Postman collection: {str(e)}\n"
        error_msg += "Common issues:\n"
        error_msg += "- Missing required fields in request objects\n"
        error_msg += "- Invalid header field types\n"
        error_msg += "- Malformed item structure in collection\n"
        error_msg += "Please ensure your collection follows the Postman v2.1.0 schema"
        raise ValueError(error_msg) from e
