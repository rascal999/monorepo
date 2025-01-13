"""Parser for Postman collection JSON files."""

import json
from pathlib import Path
from typing import List, Optional, Union, Any
from dataclasses import dataclass, field


@dataclass
class PostmanUrl:
    """Represents a Postman URL."""
    raw: str
    protocol: Optional[str] = None
    host: Optional[List[str]] = None
    path: Optional[List[str]] = None
    query: Optional[List[dict]] = None
    variable: Optional[List[dict]] = None


@dataclass
class PostmanRequest:
    """Represents a Postman request."""
    method: str
    url: PostmanUrl
    header: List[dict] = field(default_factory=list)
    body: Optional[Any] = None
    description: Optional[str] = None


@dataclass
class PostmanItem:
    """Represents a Postman collection item (request)."""
    name: str
    request: Optional[PostmanRequest] = None
    response: Optional[List[dict]] = field(default_factory=list)
    event: Optional[List[dict]] = field(default_factory=list)


@dataclass
class PostmanItemGroup:
    """Represents a Postman item group (folder)."""
    name: str
    item: List[Union['PostmanItemGroup', PostmanItem]]
    description: Optional[str] = None
    auth: Optional[dict] = None
    event: Optional[List[dict]] = field(default_factory=list)
    variable: Optional[List[dict]] = field(default_factory=list)


@dataclass
class PostmanInfo:
    """Represents Postman collection info."""
    name: str
    schema: str
    description: Optional[str] = None
    version: Optional[str] = None


@dataclass
class PostmanCollection:
    """Represents a complete Postman collection."""
    info: PostmanInfo
    item: List[Union[PostmanItemGroup, PostmanItem]]
    auth: Optional[dict] = None
    event: Optional[List[dict]] = field(default_factory=list)
    variable: Optional[List[dict]] = field(default_factory=list)


def _parse_url(url_data: Union[str, dict]) -> PostmanUrl:
    """Parse URL data from Postman format."""
    if isinstance(url_data, str):
        return PostmanUrl(raw=url_data)
    
    return PostmanUrl(
        raw=url_data.get('raw', ''),
        protocol=url_data.get('protocol'),
        host=url_data.get('host'),
        path=url_data.get('path'),
        query=url_data.get('query'),
        variable=url_data.get('variable')
    )


def _parse_request(request_data: dict) -> PostmanRequest:
    """Parse request data from Postman format."""
    return PostmanRequest(
        method=request_data.get('method', 'GET'),
        url=_parse_url(request_data.get('url', '')),
        header=request_data.get('header', []),
        body=request_data.get('body'),
        description=request_data.get('description')
    )


def _parse_item(item_data: dict) -> Union[PostmanItem, PostmanItemGroup]:
    """Parse item data from Postman format."""
    if 'item' in item_data:
        # This is an item group (folder)
        return PostmanItemGroup(
            name=item_data.get('name', ''),
            item=[_parse_item(i) for i in item_data.get('item', [])],
            description=item_data.get('description'),
            auth=item_data.get('auth'),
            event=item_data.get('event', []),
            variable=item_data.get('variable', [])
        )
    else:
        # This is a request item
        return PostmanItem(
            name=item_data.get('name', ''),
            request=_parse_request(item_data['request']) if 'request' in item_data else None,
            response=item_data.get('response', []),
            event=item_data.get('event', [])
        )


def parse_collection(collection_path: Union[str, Path]) -> PostmanCollection:
    """Parse a Postman collection from a JSON file.
    
    Args:
        collection_path: Path to the collection JSON file
        
    Returns:
        PostmanCollection object representing the parsed collection
        
    Raises:
        FileNotFoundError: If collection file doesn't exist
        json.JSONDecodeError: If collection JSON is invalid
        KeyError: If collection JSON is missing required fields
    """
    path = Path(collection_path)
    if not path.exists():
        raise FileNotFoundError(f"Collection file not found: {path}")
        
    with path.open() as f:
        data = json.load(f)
        
    if 'info' not in data:
        raise KeyError("Collection JSON missing 'info' field")
        
    return PostmanCollection(
        info=PostmanInfo(
            name=data['info'].get('name', ''),
            schema=data['info'].get('schema', ''),
            description=data['info'].get('description'),
            version=data['info'].get('version')
        ),
        item=[_parse_item(i) for i in data.get('item', [])],
        auth=data.get('auth'),
        event=data.get('event', []),
        variable=data.get('variable', [])
    )
