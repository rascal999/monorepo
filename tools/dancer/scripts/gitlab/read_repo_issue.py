#!/usr/bin/env python3

import os
import sys
import requests
import json
from dotenv import load_dotenv

def read_repo_issue(project_id, issue_iid):
    """
    Read detailed information about a specific GitLab issue.
    
    Args:
        project_id (str): The GitLab project ID
        issue_iid (str): The internal issue ID
    
    Returns:
        dict: Issue data if successful
        None: If request fails
    """
    load_dotenv()
    
    GITLAB_URL = os.getenv('GITLAB_URL')
    GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
    
    if not all([GITLAB_URL, GITLAB_TOKEN]):
        print("Error: Missing required environment variables (GITLAB_URL, GITLAB_TOKEN)")
        return None
    
    url = f"{GITLAB_URL.rstrip('/')}/api/v4/projects/{project_id}/issues/{issue_iid}"
    
    headers = {
        "PRIVATE-TOKEN": GITLAB_TOKEN,
        "Content-Type": "application/json"
    }
    
    try:
        # Get issue details
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        issue = response.json()
        
        # Get issue notes (comments)
        notes_url = f"{url}/notes"
        notes_response = requests.get(notes_url, headers=headers)
        notes_response.raise_for_status()
        notes = notes_response.json()
        
        # Combine issue data with notes
        issue['notes'] = notes
        return issue
    except requests.exceptions.RequestException as e:
        print(f"Error reading issue: {e}")
        return None

def format_issue_output(issue):
    """Format issue data for readable console output."""
    output = []
    output.append("=== Issue Details ===")
    output.append(f"Title: {issue['title']}")
    output.append(f"ID: {issue['iid']}")
    output.append(f"State: {issue['state']}")
    output.append(f"Author: {issue['author']['name']}")
    output.append(f"Created: {issue['created_at']}")
    output.append(f"Updated: {issue['updated_at']}")
    output.append(f"Labels: {', '.join(issue['labels']) if issue['labels'] else 'None'}")
    output.append(f"Assignees: {', '.join(a['name'] for a in issue['assignees']) if issue['assignees'] else 'None'}")
    output.append(f"URL: {issue['web_url']}")
    output.append("\nDescription:")
    output.append(issue['description'] if issue['description'] else 'No description')
    
    if issue.get('notes'):
        output.append("\n=== Comments ===")
        for note in issue['notes']:
            output.append(f"\n[{note['author']['name']} on {note['created_at']}]")
            output.append(note['body'])
            output.append("-" * 50)
    
    return "\n".join(output)

def main():
    if len(sys.argv) != 3:
        print("Usage: ./read_repo_issue.py <project-id> <issue-iid>")
        print("Example: ./read_repo_issue.py 123 45")
        sys.exit(1)
    
    project_id = sys.argv[1]
    issue_iid = sys.argv[2]
    
    result = read_repo_issue(project_id, issue_iid)
    
    if result:
        if '--json' in sys.argv:
            # Output raw JSON if requested
            print(json.dumps(result, indent=2))
        else:
            # Output formatted text
            print(format_issue_output(result))
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()