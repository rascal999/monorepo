#!/usr/bin/env python3

import os
import sys
import requests
import json
from dotenv import load_dotenv

def list_repo_files(project_id, path=None, ref='main'):
    """
    List files in a GitLab repository.
    
    Args:
        project_id (str): The GitLab project ID
        path (str): Optional path within the repository
        ref (str): Branch or tag name (default: 'main')
    
    Returns:
        list: List of files if successful
        None: If request fails
    """
    load_dotenv()
    
    GITLAB_URL = os.getenv('GITLAB_URL')
    GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
    
    if not all([GITLAB_URL, GITLAB_TOKEN]):
        print("Error: Missing required environment variables (GITLAB_URL, GITLAB_TOKEN)")
        return None
    
    url = f"{GITLAB_URL.rstrip('/')}/api/v4/projects/{project_id}/repository/tree"
    
    headers = {
        "PRIVATE-TOKEN": GITLAB_TOKEN,
        "Content-Type": "application/json"
    }
    
    params = {
        "ref": ref,
        "per_page": 100  # Adjust as needed
    }
    
    if path:
        params["path"] = path
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        files = response.json()
        return files
    except requests.exceptions.RequestException as e:
        print(f"Error listing files: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: ./list_repo_files.py <project-id> [path] [ref]")
        print("Example: ./list_repo_files.py 123")
        print("         ./list_repo_files.py 123 src/")
        print("         ./list_repo_files.py 123 src/ develop")
        sys.exit(1)
    
    project_id = sys.argv[1]
    path = sys.argv[2] if len(sys.argv) > 2 else None
    ref = sys.argv[3] if len(sys.argv) > 3 else 'main'
    
    result = list_repo_files(project_id, path, ref)
    
    if result:
        # Format and print file information
        for item in result:
            type_icon = "📁" if item["type"] == "tree" else "📄"
            print(f"{type_icon} {item['path']}")
            if "id" in item:
                print(f"   ID: {item['id']}")
            print(f"   Type: {item['type']}")
            print("-" * 50)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()