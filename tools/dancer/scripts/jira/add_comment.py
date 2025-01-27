#!/usr/bin/env python3

import os
import sys
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

def format_date(date_str):
    """Format date string to readable format"""
    if not date_str:
        return "Not set"
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return date_str

def format_comment_result(data, ticket_id, comment_text):
    """Format comment result in a human-readable way"""
    if not data:
        return "Comment was not added."
    
    author = data.get('author', {}).get('displayName', 'Unknown')
    created = format_date(data.get('created'))
    
    output = [
        f"Comment added to {ticket_id}",
        f"Author: {author}",
        f"Time: {created}",
        "\nComment text:",
        comment_text
    ]
    
    return "\n".join(output)

def add_comment(ticket_id, comment_text):
    """
    Add a comment to a Jira ticket.
    
    Args:
        ticket_id (str): The Jira ticket ID (e.g., 'PROJ-123')
        comment_text (str): The comment text to add
    
    Returns:
        str: Formatted result if successful
        None: If request fails
    """
    load_dotenv()
    
    JIRA_URL = os.getenv('JIRA_URL')
    JIRA_TOKEN = os.getenv('JIRA_TOKEN')
    JIRA_EMAIL = os.getenv('JIRA_EMAIL')
    
    if not all([JIRA_URL, JIRA_TOKEN, JIRA_EMAIL]):
        print("Error: Missing required environment variables (JIRA_URL, JIRA_TOKEN, JIRA_EMAIL)")
        return None
    
    url = f"{JIRA_URL.rstrip('/')}/rest/api/2/issue/{ticket_id}/comment"
    
    # Create base64 encoded credentials
    import base64
    credentials = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_TOKEN}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    
    data = {
        "body": comment_text
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return format_comment_result(response.json(), ticket_id, comment_text)
    except requests.exceptions.RequestException as e:
        print(f"Error adding comment: {e}")
        return None

def main():
    if len(sys.argv) != 3:
        print("Usage: ./add_comment.py <ticket-id> \"<comment-text>\"")
        print("Example: ./add_comment.py PROJ-123 \"This is a comment\"")
        sys.exit(1)
    
    ticket_id = sys.argv[1]
    comment_text = sys.argv[2]
    
    result = add_comment(ticket_id, comment_text)
    
    if result:
        print(result)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()