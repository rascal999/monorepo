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

def format_ticket(data):
    """Format ticket data in a human-readable way"""
    fields = data.get('fields', {})
    
    # Basic information
    output = [
        f"Ticket: {data.get('key', 'Unknown')}",
        f"Title: {fields.get('summary', 'No title')}",
        f"Status: {fields.get('status', {}).get('name', 'Unknown')}",
        f"Type: {fields.get('issuetype', {}).get('name', 'Unknown')}",
        f"Priority: {fields.get('priority', {}).get('name', 'Not set')}",
    ]
    
    # Dates
    output.extend([
        f"Created: {format_date(fields.get('created'))}",
        f"Updated: {format_date(fields.get('updated'))}",
        f"Due Date: {format_date(fields.get('duedate'))}"
    ])
    
    # People
    reporter = fields.get('reporter', {}).get('displayName', 'Unknown')
    assignee = fields.get('assignee', {}).get('displayName', 'Unassigned')
    output.extend([
        f"Reporter: {reporter}",
        f"Assignee: {assignee}"
    ])
    
    # Labels and components
    labels = fields.get('labels', [])
    components = [c.get('name', '') for c in fields.get('components', [])]
    if labels:
        output.append(f"Labels: {', '.join(labels)}")
    if components:
        output.append(f"Components: {', '.join(components)}")
    
    # Description
    description = fields.get('description', '').strip()
    if description:
        output.extend([
            "\nDescription:",
            description
        ])
    
    # Comments
    comments = fields.get('comment', {}).get('comments', [])
    if comments:
        output.append("\nRecent Comments:")
        for comment in comments[-3:]:  # Show last 3 comments
            author = comment.get('author', {}).get('displayName', 'Unknown')
            created = format_date(comment.get('created'))
            body = comment.get('body', '').strip()
            output.extend([
                f"\n[{author} on {created}]",
                body,
                "-" * 40
            ])
    
    return "\n".join(output)

def fetch_ticket(ticket_id):
    """
    Fetch a Jira ticket by its ID.
    
    Args:
        ticket_id (str): The Jira ticket ID (e.g., 'PROJ-123')
    
    Returns:
        str: Formatted ticket data if successful
        None: If request fails
    """
    load_dotenv()
    
    JIRA_URL = os.getenv('JIRA_URL')
    JIRA_TOKEN = os.getenv('JIRA_TOKEN')
    JIRA_EMAIL = os.getenv('JIRA_EMAIL')
    
    if not all([JIRA_URL, JIRA_TOKEN, JIRA_EMAIL]):
        print("Error: Missing required environment variables (JIRA_URL, JIRA_TOKEN, JIRA_EMAIL)")
        return None
    
    url = f"{JIRA_URL.rstrip('/')}/rest/api/2/issue/{ticket_id}"
    
    # Create base64 encoded credentials
    import base64
    credentials = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_TOKEN}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    
    params = {
        "expand": "renderedFields,comments"  # Include comments in response
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return format_ticket(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ticket: {e}")
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: ./fetch_ticket.py <ticket-id>")
        sys.exit(1)
    
    ticket_id = sys.argv[1]
    result = fetch_ticket(ticket_id)
    
    if result:
        print(result)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()