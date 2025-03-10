from dataclasses import dataclass
from typing import Dict, Optional, Union
from datetime import datetime
import uuid

@dataclass
class WhatsAppConfig:
    """Configuration for WhatsApp API client"""
    base_url: str
    api_key: str
    session_id: str
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"  # Default to llama2 which is more commonly available

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'WhatsAppConfig':
        """Create config from dictionary, using default session ID if not provided"""
        return cls(
            base_url=data['base_url'],
            api_key=data['api_key'],
            session_id=data.get('session_id', str(uuid.uuid4())),
            ollama_url=data.get('ollama_url', "http://localhost:11434"),
            ollama_model=data.get('ollama_model', "llama2")
        )

@dataclass
class Chat:
    """Represents a WhatsApp chat"""
    id: Union[str, Dict]  # Can be string or serialized ID object
    name: str
    timestamp: datetime
    unread_count: int

    @classmethod
    def from_dict(cls, data: Dict) -> 'Chat':
        """Create chat from API response dictionary"""
        return cls(
            id=data.get('id'),  # Keep raw ID format for flexibility
            name=data.get('name', 'Unknown'),
            timestamp=datetime.fromtimestamp(data.get('timestamp', 0)),
            unread_count=data.get('unreadCount', 0)
        )

@dataclass
class Contact:
    """Represents a WhatsApp contact"""
    id: str
    name: str
    number: str
    push_name: Optional[str] = None
    business: bool = False

    @classmethod
    def from_dict(cls, data: Dict) -> Optional['Contact']:
        """Create contact from API response dictionary"""
        # Handle nested ID structure
        contact_id = None
        if isinstance(data.get('id'), dict):
            contact_id = data['id'].get('_serialized')
        else:
            contact_id = data.get('id')

        # Skip invalid contacts
        if not contact_id or not isinstance(contact_id, str) or not contact_id.endswith('@c.us'):
            return None
            
        # Get name from either name or shortName field
        name = data.get('name') or data.get('shortName', 'Unknown')
        
        return cls(
            id=contact_id,
            name=str(name),
            number=str(data.get('number', '')),
            push_name=data.get('pushName'),
            business=bool(data.get('isBusiness', False))
        )