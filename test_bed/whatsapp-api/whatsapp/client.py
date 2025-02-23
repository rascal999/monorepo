import requests
import time
import sys
import json
from typing import Dict, List, Optional, Union
from .models import WhatsAppConfig, Chat, Contact

class WhatsAppClient:
    """Client for interacting with WhatsApp API"""
    
    def __init__(self, config: WhatsAppConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': config.api_key,
            'Content-Type': 'application/json'
        })
        self._contacts_cache = {}  # Cache for contact lookups

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to API with error handling"""
        url = f"{self.config.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, json=data)
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {endpoint}: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            sys.exit(1)

    def _get_serialized_id(self, id_data: Union[str, Dict]) -> Optional[str]:
        """Extract serialized ID from various formats"""
        if isinstance(id_data, str):
            return id_data
        if isinstance(id_data, dict):
            return id_data.get('_serialized')
        return None

    def check_session_exists(self) -> bool:
        """Check if the session already exists and is connected"""
        try:
            response = self._make_request('GET', f'/session/status/{self.config.session_id}')
            return response.get('state') == 'CONNECTED'
        except:
            return False

    def start_session(self) -> bool:
        """Start a new WhatsApp session if not already connected"""
        # First check if session exists and is connected
        if self.check_session_exists():
            print(f"Using existing session {self.config.session_id}")
            return True

        print(f"Starting new session {self.config.session_id}...")
        response = self._make_request('GET', f'/session/start/{self.config.session_id}')
        return response.get('success', False)

    def wait_for_session_connection(self, timeout: int = 60) -> bool:
        """Wait for session to be connected"""
        print("Waiting for session to connect...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self._make_request('GET', f'/session/status/{self.config.session_id}')
            if response.get('state') == 'CONNECTED':
                return True
            time.sleep(2)
        return False

    def get_contacts(self) -> List[Contact]:
        """Get all contacts"""
        print("Fetching contacts...")
        response = self._make_request('GET', f'/client/getContacts/{self.config.session_id}')
        
        contacts = []
        for contact_data in response.get('contacts', []):
            contact = Contact.from_dict(contact_data)
            if contact:  # Skip None results (non-contacts)
                contacts.append(contact)
                # Update cache
                self._contacts_cache[contact.id] = contact
                if contact.number:
                    self._contacts_cache[f"{contact.number}@c.us"] = contact
        return sorted(contacts, key=lambda x: x.name.lower())

    def get_contact_by_id(self, contact_id: str) -> Optional[Contact]:
        """Get contact by ID, using cache if available"""
        # Check cache first
        if contact_id in self._contacts_cache:
            return self._contacts_cache[contact_id]
            
        # If not in cache, try to fetch contact
        response = self._make_request(
            'POST',
            f'/client/getContactById/{self.config.session_id}',
            {'contactId': contact_id}
        )
        
        if response.get('contact'):
            contact = Contact.from_dict(response['contact'])
            if contact:
                self._contacts_cache[contact_id] = contact
                if contact.number:
                    self._contacts_cache[f"{contact.number}@c.us"] = contact
                return contact
        return None

    def find_contact(self, identifier: str) -> Optional[Contact]:
        """Find contact by name or number"""
        # First try exact number match
        if identifier.replace('+', '').isdigit():
            number = identifier.replace('+', '')
            contact_id = f"{number}@c.us"
            contact = self.get_contact_by_id(contact_id)
            if contact:
                return contact
        
        # Then try name match
        contacts = self.get_contacts()
        for contact in contacts:
            if contact.name.lower() == identifier.lower():
                return contact
            if contact.number == identifier.replace('+', ''):
                return contact
        return None

    def get_chats(self) -> List[Chat]:
        """Get all chats"""
        print("Fetching chats...")
        response = self._make_request('GET', f'/client/getChats/{self.config.session_id}')
        
        return [
            Chat.from_dict(chat_data)
            for chat_data in response.get('chats', [])
        ]

    def find_chat_by_number(self, phone_number: str) -> Optional[str]:
        """Find chat ID by phone number"""
        # Ensure number is in proper format
        number = phone_number.strip().replace('+', '')
        if not number.endswith('@c.us'):
            number = f"{number}@c.us"
        
        print(f"\nDebug: Looking up number: {number}")
        
        # First try to get all chats and find a match
        chats = self.get_chats()
        for chat in chats:
            chat_id = self._get_serialized_id(chat.id)
            print(f"Debug: Checking chat: {chat_id}")
            if chat_id == number:
                print(f"Debug: Found matching chat ID: {chat_id}")
                return chat_id
        
        # If not found in existing chats, try getNumberId
        print("\nDebug: Chat not found in existing chats, trying getNumberId...")
        response = self._make_request(
            'POST',
            f'/client/getNumberId/{self.config.session_id}',
            {'number': number}
        )
        
        print(f"Debug: getNumberId response: {json.dumps(response, indent=2)}")
        
        # Handle success response with result object
        if response.get('success') and response.get('result'):
            chat_id = self._get_serialized_id(response['result'])
            if chat_id:
                print(f"Debug: Found chat ID via getNumberId: {chat_id}")
                return chat_id
            
        print("Debug: Number not found via getNumberId")
        return None

    def send_message(self, recipient: str, message: str) -> bool:
        """Send a message to a contact by name or number"""
        # First try to find the contact
        contact = self.find_contact(recipient)
        if contact:
            chat_id = contact.id
        else:
            # If no contact found, try to use the number directly
            chat_id = self.find_chat_by_number(recipient)
            if not chat_id:
                print(f"Could not find recipient: {recipient}")
                return False
        
        # Send the message
        data = {
            'chatId': chat_id,
            'contentType': 'string',
            'content': message
        }
        
        response = self._make_request(
            'POST',
            f'/client/sendMessage/{self.config.session_id}',
            data
        )
        
        success = response.get('success', False)
        if success:
            print(f"Message sent successfully to {recipient}")
        else:
            print(f"Failed to send message: {response.get('error', 'Unknown error')}")
        return success

    def fetch_messages(self, chat_id: str, limit: int = 50) -> List[Dict]:
        """Fetch messages from a specific chat"""
        print(f"Fetching messages for chat {chat_id}...")
        data = {
            'chatId': chat_id,
            'searchOptions': {
                'limit': limit
            }
        }
        response = self._make_request(
            'POST', 
            f'/chat/fetchMessages/{self.config.session_id}',
            data
        )
        
        messages = response.get('messages', [])
        
        # Add contact info to messages
        for msg in messages:
            if not msg.get('fromMe'):
                contact_id = msg.get('from')
                if contact_id:
                    contact = self.get_contact_by_id(contact_id)
                    if contact:
                        msg['sender_name'] = contact.name
            
        return messages