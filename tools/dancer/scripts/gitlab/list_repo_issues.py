#!/usr/bin/env python3

import os
import sys
import requests
import json
from dotenv import load_dotenv

def list_repo_issues(project_id, state=None, labels=None, page=1):
    """
    List issues in a GitLab repository.
    
    Args:
        project_id (str): The GitLab project ID
        state (str): Optional filter by state ('opened', 'closed', 'all')
        labels (str): Optional comma-separated list of labels
        page (int): Page number for pagination
    
    Returns:
        list: List of issues if successful
        None: If request fails
    """
    load_dotenv()
    
    GITLAB_URL = os.getenv('GITLAB_URL')
    GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
    
    if not all([GITLAB_URL, GITLAB_TOKEN]):
        print("Error: Missing required environment variables (GITLAB_URL, GITLAB_TOKEN)")
        return None
    
    url = f"{GITLAB_URL.rstrip('/')}/api/v4/projects/{project_id}/issues"
    
    headers = {
        "PRIVATE-TOKEN": GITLAB_TOKEN,
        "Content-Type": "application/json"
    }
    
    params = {
        "per_page": 20,
        "page": page
    }
    
    if state:
        params["state"] = state
    if labels:
        params["labels"] = labels
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        # Get total pages from headers
        total_pages = int(response.headers.get('X-Total-Pages', 1))
        current_page = int(response.headers.get('X-Page', 1))
        
        issues = response.json()
        return {
            'issues': issues,
            'pagination': {
                'current_page': current_page,
                'total_pages': total_pages
            }
        }
    except requests.exceptions.RequestException as e:
        print(f"Error listing issues: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: ./list_repo_issues.py <project-id> [--state state] [--labels label1,label2] [--page num]")
        print("Example: ./list_repo_issues.py 123")
        print("         ./list_repo_issues.py 123 --state opened")
        print("         ./list_repo_issues.py 123 --labels bug,critical")
        print("         ./list_repo_issues.py 123 --page 2")
        sys.exit(1)
    
    project_id = sys.argv[1]
    state = None
    labels = None
    page = 1
    
    # Parse optional arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--state" and i + 1 < len(sys.argv):
            state = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--labels" and i + 1 < len(sys.argv):
            labels = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--page" and i + 1 < len(sys.argv):
            page = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    result = list_repo_issues(project_id, state, labels, page)
    
    if result:
        issues = result['issues']
        pagination = result['pagination']
        
        # Print pagination info
        print(f"Page {pagination['current_page']} of {pagination['total_pages']}")
        print("-" * 50)
        
        # Format and print issue information
        for issue in issues:
            print(f"Title: {issue['title']}")
            print(f"ID: {issue['iid']}")
            print(f"State: {issue['state']}")
            print(f"Labels: {', '.join(issue['labels']) if issue['labels'] else 'None'}")
            print(f"Created: {issue['created_at']}")
            print(f"URL: {issue['web_url']}")
            print("-" * 50)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()