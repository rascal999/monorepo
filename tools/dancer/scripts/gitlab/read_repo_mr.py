#!/usr/bin/env python3

import os
import sys
import requests
import json
from dotenv import load_dotenv

def read_repo_mr(project_id, mr_iid):
    """
    Read detailed information about a specific GitLab merge request.
    
    Args:
        project_id (str): The GitLab project ID
        mr_iid (str): The internal merge request ID
    
    Returns:
        dict: Merge request data if successful
        None: If request fails
    """
    load_dotenv()
    
    GITLAB_URL = os.getenv('GITLAB_URL')
    GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
    
    if not all([GITLAB_URL, GITLAB_TOKEN]):
        print("Error: Missing required environment variables (GITLAB_URL, GITLAB_TOKEN)")
        return None
    
    base_url = f"{GITLAB_URL.rstrip('/')}/api/v4/projects/{project_id}/merge_requests/{mr_iid}"
    
    headers = {
        "PRIVATE-TOKEN": GITLAB_TOKEN,
        "Content-Type": "application/json"
    }
    
    try:
        # Get MR details
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        mr = response.json()
        
        # Get discussions (comments and code reviews)
        discussions_url = f"{base_url}/discussions"
        discussions_response = requests.get(discussions_url, headers=headers)
        discussions_response.raise_for_status()
        discussions = discussions_response.json()
        
        # Get changes
        changes_url = f"{base_url}/changes"
        changes_response = requests.get(changes_url, headers=headers)
        changes_response.raise_for_status()
        changes = changes_response.json()
        
        # Combine all data
        mr['discussions'] = discussions
        mr['changes'] = changes.get('changes', [])
        return mr
    except requests.exceptions.RequestException as e:
        print(f"Error reading merge request: {e}")
        return None

def format_mr_output(mr):
    """Format merge request data for readable console output."""
    output = []
    output.append("=== Merge Request Details ===")
    output.append(f"Title: {mr['title']}")
    output.append(f"ID: {mr['iid']}")
    output.append(f"State: {mr['state']}")
    output.append(f"Author: {mr['author']['name']}")
    output.append(f"Source Branch: {mr['source_branch']}")
    output.append(f"Target Branch: {mr['target_branch']}")
    output.append(f"Created: {mr['created_at']}")
    output.append(f"Updated: {mr['updated_at']}")
    output.append(f"Labels: {', '.join(mr['labels']) if mr['labels'] else 'None'}")
    output.append(f"Assignees: {', '.join(a['name'] for a in mr['assignees']) if mr['assignees'] else 'None'}")
    output.append(f"URL: {mr['web_url']}")
    
    output.append("\nDescription:")
    output.append(mr['description'] if mr['description'] else 'No description')
    
    if mr.get('discussions'):
        output.append("\n=== Discussions ===")
        for discussion in mr['discussions']:
            for note in discussion['notes']:
                output.append(f"\n[{note['author']['name']} on {note['created_at']}]")
                if note.get('position'):
                    output.append(f"File: {note['position']['new_path']}")
                    output.append(f"Line: {note['position'].get('new_line', 'N/A')}")
                output.append(note['body'])
                output.append("-" * 50)
    
    if mr.get('changes'):
        output.append("\n=== Changes ===")
        for change in mr['changes']:
            output.append(f"\nFile: {change['new_path']}")
            output.append(f"Status: {change.get('deleted_file', False) and 'Deleted' or change.get('new_file', False) and 'Added' or 'Modified'}")
            output.append(f"Changes: +{change.get('additions', 0)} -{change.get('deletions', 0)}")
            output.append("-" * 50)
    
    return "\n".join(output)

def main():
    if len(sys.argv) != 3:
        print("Usage: ./read_repo_mr.py <project-id> <mr-iid>")
        print("Example: ./read_repo_mr.py 123 45")
        sys.exit(1)
    
    project_id = sys.argv[1]
    mr_iid = sys.argv[2]
    
    result = read_repo_mr(project_id, mr_iid)
    
    if result:
        if '--json' in sys.argv:
            # Output raw JSON if requested
            print(json.dumps(result, indent=2))
        else:
            # Output formatted text
            print(format_mr_output(result))
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()