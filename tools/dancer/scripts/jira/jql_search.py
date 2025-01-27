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

def format_search_results(data):
    """Format JQL search results in a human-readable way"""
    total = data.get('total', 0)
    issues = data.get('issues', [])
    
    if total == 0:
        return "No issues found."
    
    output = [f"Found {total} issue{'s' if total != 1 else ''}:"]
    
    for issue in issues:
        fields = issue.get('fields', {})
        
        # Basic information
        key = issue.get('key', 'Unknown')
        summary = fields.get('summary', 'No title')
        status = fields.get('status', {}).get('name', 'Unknown')
        issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
        priority = fields.get('priority', {}).get('name', 'Not set')
        assignee = fields.get('assignee', {}).get('displayName', 'Unassigned')
        updated = format_date(fields.get('updated'))
        
        output.extend([
            "\n" + "=" * 40,
            f"{key}: {summary}",
            f"Type: {issue_type}",
            f"Status: {status}",
            f"Priority: {priority}",
            f"Assignee: {assignee}",
            f"Updated: {updated}"
        ])
        
        # Labels
        labels = fields.get('labels', [])
        if labels:
            output.append(f"Labels: {', '.join(labels)}")
    
    if total > len(issues):
        output.append(f"\nShowing {len(issues)} of {total} issues")
    
    return "\n".join(output)

def jql_search(jql_query):
    """
    Search Jira tickets using JQL query.
    
    Args:
        jql_query (str): JQL search query
    
    Returns:
        str: Formatted search results if successful
        None: If request fails
    """
    load_dotenv()
    
    JIRA_URL = os.getenv('JIRA_URL')
    JIRA_TOKEN = os.getenv('JIRA_TOKEN')
    JIRA_EMAIL = os.getenv('JIRA_EMAIL')
    
    if not all([JIRA_URL, JIRA_TOKEN, JIRA_EMAIL]):
        print("Error: Missing required environment variables (JIRA_URL, JIRA_TOKEN, JIRA_EMAIL)")
        return None
    
    url = f"{JIRA_URL.rstrip('/')}/rest/api/2/search"
    
    # Create base64 encoded credentials
    import base64
    credentials = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_TOKEN}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    
    params = {
        "jql": jql_query,
        "maxResults": 20  # Adjust as needed
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return format_search_results(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error executing JQL search: {e}")
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: ./jql_search.py \"<jql-query>\"")
        print("Example: ./jql_search.py \"project = PROJ AND status = Open\"")
        sys.exit(1)
    
    jql_query = sys.argv[1]
    result = jql_search(jql_query)
    
    if result:
        print(result)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()