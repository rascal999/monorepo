#!/usr/bin/env python3

import os
import sys
import requests
import json
from dotenv import load_dotenv

def list_group_repos(group_id=None):
    """
    List repositories for a GitLab group.
    
    Args:
        group_id (str): The GitLab group ID. If None, uses GITLAB_GROUP from env
    
    Returns:
        list: List of repositories if successful
        None: If request fails
    """
    load_dotenv()
    
    GITLAB_URL = os.getenv('GITLAB_URL')
    GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
    
    if not group_id:
        group_id = os.getenv('GITLAB_GROUP')
    
    if not all([GITLAB_URL, GITLAB_TOKEN]):
        print("Error: Missing required environment variables (GITLAB_URL, GITLAB_TOKEN)")
        return None
    
    url = f"{GITLAB_URL.rstrip('/')}/api/v4/groups/{group_id}/projects"
    
    headers = {
        "PRIVATE-TOKEN": GITLAB_TOKEN,
        "Content-Type": "application/json"
    }
    
    params = {
        "include_subgroups": True,
        "per_page": 100  # Adjust as needed
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        repos = response.json()
        return repos
    except requests.exceptions.RequestException as e:
        print(f"Error listing repositories: {e}")
        return None

def main():
    group_id = None
    if len(sys.argv) > 1:
        group_id = sys.argv[1]
    
    result = list_group_repos(group_id)
    
    if result:
        # Format and print repository information
        for repo in result:
            print(f"Name: {repo['name']}")
            print(f"ID: {repo['id']}")
            print(f"URL: {repo['web_url']}")
            print(f"Description: {repo.get('description', 'N/A')}")
            print("-" * 50)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()