#!/usr/bin/env python3
import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WhatsAppAPI:
    def __init__(self):
        self.base_url = os.getenv('WHATSAPP_API_URL', 'http://localhost:3001')
        self.session_id = os.getenv('WHATSAPP_SESSION_ID', 'ABCD')
        
    def start_session(self):
        """Start or get an existing WhatsApp session."""
        endpoint = f"{self.base_url}/session/start/{self.session_id}"
        try:
            response = requests.get(endpoint)
            # 422 with "Session already exists" is okay
            if response.status_code == 422 and "Session already exists" in response.text:
                return {"success": True, "message": "Session already exists"}
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if response.status_code == 422 and "Session already exists" in response.text:
                return {"success": True, "message": "Session already exists"}
            print(f"Error starting session: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            sys.exit(1)
            
    def send_message(self, phone_number, message):
        """Send a WhatsApp message using the WhatsApp API."""
        endpoint = f"{self.base_url}/client/sendMessage/{self.session_id}"
        
        # Format phone number (remove any special characters)
        phone_number = ''.join(filter(str.isdigit, phone_number))
        
        # Add @c.us suffix if not present
        if not phone_number.endswith('@c.us'):
            phone_number = f"{phone_number}@c.us"
        
        payload = {
            "chatId": phone_number,
            "contentType": "string",
            "content": message
        }
        
        try:
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            sys.exit(1)

    def fetch_messages(self, phone_number):
        """Fetch messages from a specific chat."""
        endpoint = f"{self.base_url}/chat/fetchMessages/{self.session_id}"
        
        # Format phone number (remove any special characters)
        phone_number = ''.join(filter(str.isdigit, phone_number))
        
        # Add @c.us suffix if not present
        if not phone_number.endswith('@c.us'):
            phone_number = f"{phone_number}@c.us"
        
        payload = {
            "chatId": phone_number
        }
        
        try:
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching messages: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            sys.exit(1)

    def check_status(self):
        """Check if the WhatsApp API server is ready."""
        endpoint = f"{self.base_url}/session/status/{self.session_id}"
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error checking status: {e}")
            sys.exit(1)

def print_messages(messages):
    """Print messages in a readable format."""
    if not messages:
        print("No messages found.")
        return
        
    for msg in messages:
        sender = "You" if msg.get('fromMe') else "Contact"
        timestamp = msg.get('timestamp', 'Unknown time')
        body = msg.get('body', 'No content')
        print(f"{timestamp} - {sender}: {body}")

def main():
    """Main function to handle CLI arguments."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Send message:   python chai.py send <phone_number> <message>")
        print("  Get messages:   python chai.py get <phone_number>")
        print("\nExample:")
        print("  python chai.py send 1234567890 'Hello from WhatsApp!'")
        print("  python chai.py get 1234567890")
        sys.exit(1)

    command = sys.argv[1]
    if command not in ['send', 'get']:
        print("Invalid command. Use 'send' or 'get'")
        sys.exit(1)

    api = WhatsAppAPI()
    
    # Start or get session
    print("Starting WhatsApp session...")
    session = api.start_session()
    if session.get('success'):
        print("Session ready.")
    else:
        print("Failed to start session.")
        sys.exit(1)
    
    # Check if API is ready
    print("Checking session status...")
    status = api.check_status()
    if not status.get('state') == 'CONNECTED':
        print("WhatsApp is not connected. Please scan the QR code shown in the WhatsApp API server console.")
        print(f"Visit {api.base_url}/session/start/{api.session_id} to see the QR code.")
        sys.exit(1)

    try:
        if command == 'send':
            if len(sys.argv) != 4:
                print("Usage: python chai.py send <phone_number> <message>")
                sys.exit(1)
            phone_number = sys.argv[2]
            message = sys.argv[3]
            print("Sending message...")
            result = api.send_message(phone_number, message)
            print(f"Message sent successfully: {json.dumps(result, indent=2)}")
        else:  # command == 'get'
            if len(sys.argv) != 3:
                print("Usage: python chai.py get <phone_number>")
                sys.exit(1)
            phone_number = sys.argv[2]
            print("Fetching messages...")
            result = api.fetch_messages(phone_number)
            print_messages(result.get('messages', []))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
