from typing import Dict
from datetime import datetime

def format_message(msg: Dict) -> str:
    """Format a message for display"""
    timestamp = datetime.fromtimestamp(msg.get('timestamp', 0))
    
    # Get sender info
    sender = "Unknown"
    if msg.get('fromMe'):
        sender = "Me"
    elif msg.get('sender_name'):  # Use contact name if available
        sender = msg['sender_name']
    elif msg.get('from'):  # Fallback to number
        # Extract number from "number@c.us" format
        number = msg['from'].split('@')[0]
        sender = number
    
    # Get message content
    content = "No content"
    if msg.get('body'):
        content = msg['body']
    elif msg.get('type'):
        content = f"[{msg['type'].upper()} message]"
        if msg['type'] == 'image':
            caption = msg.get('caption')
            if caption:
                content = f"[IMAGE] {caption}"
        elif msg['type'] == 'video':
            caption = msg.get('caption')
            if caption:
                content = f"[VIDEO] {caption}"
        elif msg['type'] == 'audio':
            content = "[AUDIO message]"
        elif msg['type'] == 'document':
            filename = msg.get('filename', '')
            if filename:
                content = f"[DOCUMENT] {filename}"
        elif msg['type'] == 'location':
            loc = msg.get('location', {})
            if loc:
                content = f"[LOCATION] {loc.get('latitude')}, {loc.get('longitude')}"
                if loc.get('description'):
                    content += f" - {loc['description']}"
        elif msg['type'] == 'sticker':
            content = "[STICKER]"
    
    # Format timestamp based on how old the message is
    now = datetime.now()
    msg_time = datetime.fromtimestamp(msg.get('timestamp', 0))
    if msg_time.date() == now.date():
        # Today - show only time
        time_str = msg_time.strftime('%H:%M')
    elif msg_time.year == now.year:
        # This year - show date without year
        time_str = msg_time.strftime('%d %b %H:%M')
    else:
        # Different year - show full date
        time_str = msg_time.strftime('%Y-%m-%d %H:%M')
    
    return f"{time_str} - {sender}: {content}"

def format_contact(contact: 'Contact') -> str:  # type: ignore
    """Format a contact for display"""
    parts = [
        f"Name: {contact.name}",
        f"Number: {contact.number}"
    ]
    if contact.push_name:
        parts.append(f"Push Name: {contact.push_name}")
    if contact.business:
        parts.append("(Business Account)")
    return " | ".join(parts)