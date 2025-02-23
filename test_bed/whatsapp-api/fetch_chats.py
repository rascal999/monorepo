#!/usr/bin/env python3
import json
import sys
import argparse
from whatsapp import (
    WhatsAppClient,
    WhatsAppConfig,
    format_message,
    format_contact
)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='WhatsApp CLI Client')
    
    # Config
    parser.add_argument('--config', type=str, default='config.json',
                       help='Path to config file (default: config.json)')
    
    # Action group
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--list-chats', '-c', action='store_true',
                       help='List all chats and exit')
    action.add_argument('--list-contacts', '-n', action='store_true',
                       help='List all contacts with their numbers and exit')
    action.add_argument('--fetch', '-f', type=str, metavar='CONTACT',
                       help='Fetch messages from a contact (name or number)')
    action.add_argument('--send', '-s', type=str, metavar='CONTACT',
                       help='Send a message to a contact (name or number)')
    
    # Options
    parser.add_argument('--limit', '-l', type=int, default=50,
                       help='Number of messages to fetch (default: 50)')
    parser.add_argument('--message', '-m', type=str,
                       help='Message to send (required with --send)')
    
    args = parser.parse_args()
    
    # Validate send command has message
    if args.send and not args.message:
        parser.error("--send requires --message")
    
    return args

def load_config(config_path: str) -> WhatsAppConfig:
    """Load configuration from file"""
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        return WhatsAppConfig.from_dict(config_data)
    except FileNotFoundError:
        print(f"Error: {config_path} not found. Please create it with the following format:")
        print("""
        {
            "base_url": "http://localhost:3000",
            "api_key": "your-api-key-here",
            "session_id": "optional-session-id"  # Will generate UUID if not provided
        }
        """)
        sys.exit(1)

def main():
    args = parse_args()
    config = load_config(args.config)
    client = WhatsAppClient(config)

    # Start session or use existing one
    if not client.start_session():
        print("Failed to start session")
        sys.exit(1)

    if not client.check_session_exists() and not client.wait_for_session_connection():
        print("Session failed to connect within timeout")
        sys.exit(1)

    # List all contacts
    if args.list_contacts:
        contacts = client.get_contacts()
        print(f"\nFound {len(contacts)} contacts:")
        for contact in contacts:
            print(f"\n{format_contact(contact)}")
        sys.exit(0)

    # List all chats
    if args.list_chats:
        chats = client.get_chats()
        print(f"\nFound {len(chats)} chats:")
        for chat in chats:
            print(f"\nChat: {chat.name}")
            print(f"ID: {chat.id}")
            print(f"Last activity: {chat.timestamp}")
            print(f"Unread messages: {chat.unread_count}")
        sys.exit(0)

    # Send message
    if args.send:
        if client.send_message(args.send, args.message):
            sys.exit(0)
        else:
            sys.exit(1)

    # Fetch messages
    if args.fetch:
        # Try to find contact
        contact = client.find_contact(args.fetch)
        if contact:
            chat_id = contact.id
            recipient_name = contact.name
        else:
            # Try as phone number
            chat_id = client.find_chat_by_number(args.fetch)
            if not chat_id:
                print(f"No chat found for: {args.fetch}")
                sys.exit(1)
            recipient_name = args.fetch
        
        messages = client.fetch_messages(chat_id, args.limit)
        if not messages:
            print("No messages found")
            sys.exit(0)
        
        print(f"\nLast {len(messages)} messages from {recipient_name}:")
        for msg in messages:
            print(format_message(msg))
        sys.exit(0)

if __name__ == '__main__':
    main()