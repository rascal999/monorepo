#!/usr/bin/env python3

import os
import sys
import requests
from dotenv import load_dotenv

def format_delete_result(success, ticket_id, error=None):
    """Format delete result in a human-readable way"""
    if success:
        return f"Successfully deleted ticket {ticket_id}"
    else:
        error_msg = f": {error}" if error else ""
        return f"Failed to delete ticket {ticket_id}{error_msg}"

def delete_ticket(ticket_id, force=False):
    """
    Delete a Jira ticket.
    
    Args:
        ticket_id (str): The Jira ticket ID (e.g., 'PROJ-123')
        force (bool): Skip confirmation if True
    
    Returns:
        str: Formatted result message
    """
    load_dotenv()
    
    JIRA_URL = os.getenv('JIRA_URL')
    JIRA_TOKEN = os.getenv('JIRA_TOKEN')
    JIRA_EMAIL = os.getenv('JIRA_EMAIL')
    
    if not all([JIRA_URL, JIRA_TOKEN, JIRA_EMAIL]):
        return "Error: Missing required environment variables (JIRA_URL, JIRA_TOKEN, JIRA_EMAIL)"
    
    url = f"{JIRA_URL.rstrip('/')}/rest/api/2/issue/{ticket_id}"
    
    # Create base64 encoded credentials
    import base64
    credentials = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_TOKEN}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    
    # Confirm deletion unless force flag is used
    if not force:
        confirm = input(f"Are you sure you want to delete ticket {ticket_id}? This cannot be undone. (y/N): ")
        if confirm.lower() != 'y':
            return "Operation cancelled by user."
    
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return format_delete_result(True, ticket_id)
    except requests.exceptions.RequestException as e:
        return format_delete_result(False, ticket_id, str(e))

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: ./delete_ticket.py <ticket-id> [--force]")
        print("Example: ./delete_ticket.py PROJ-123")
        print("         ./delete_ticket.py PROJ-123 --force")
        sys.exit(1)
    
    ticket_id = sys.argv[1]
    force = len(sys.argv) == 3 and sys.argv[2] == '--force'
    
    result = delete_ticket(ticket_id, force)
    print(result)
    
    if "Failed" in result or "Error" in result:
        sys.exit(1)

if __name__ == "__main__":
    main()