#!/usr/bin/env python3

import os
import sys
import requests
import json
import base64
from dotenv import load_dotenv

def read_repo_file(project_id, file_path, ref='main'):
    """
    Read a file from a GitLab repository.
    
    Args:
        project_id (str): The GitLab project ID
        file_path (str): Path to the file in the repository
        ref (str): Branch or tag name (default: 'main')
    
    Returns:
        str: File content if successful
        None: If request fails
    """
    load_dotenv()
    
    GITLAB_URL = os.getenv('GITLAB_URL')
    GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
    
    if not all([GITLAB_URL, GITLAB_TOKEN]):
        print("Error: Missing required environment variables (GITLAB_URL, GITLAB_TOKEN)")
        return None
    
    url = f"{GITLAB_URL.rstrip('/')}/api/v4/projects/{project_id}/repository/files/{file_path}/raw"
    
    headers = {
        "PRIVATE-TOKEN": GITLAB_TOKEN
    }
    
    params = {
        "ref": ref
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def read_multiple_files(project_id, file_paths, ref='main'):
    """
    Read multiple files from a GitLab repository.
    
    Args:
        project_id (str): The GitLab project ID
        file_paths (list): List of file paths to read
        ref (str): Branch or tag name (default: 'main')
    
    Returns:
        dict: Dictionary of file paths and their contents
    """
    results = {}
    for file_path in file_paths:
        content = read_repo_file(project_id, file_path, ref)
        if content is not None:
            results[file_path] = content
    return results

def main():
    if len(sys.argv) < 3:
        print("Usage: ./read_repo_files.py <project-id> <file-path> [file-path2 ...] [--ref branch-name]")
        print("Example: ./read_repo_files.py 123 src/main.py")
        print("         ./read_repo_files.py 123 src/main.py tests/test_main.py")
        print("         ./read_repo_files.py 123 src/main.py --ref develop")
        sys.exit(1)
    
    project_id = sys.argv[1]
    
    # Check if ref is specified
    if "--ref" in sys.argv:
        ref_index = sys.argv.index("--ref")
        ref = sys.argv[ref_index + 1]
        file_paths = sys.argv[2:ref_index]
    else:
        ref = 'main'
        file_paths = sys.argv[2:]
    
    if len(file_paths) == 1:
        # Single file
        content = read_repo_file(project_id, file_paths[0], ref)
        if content:
            print(f"=== Content of {file_paths[0]} ===")
            print(content)
        else:
            sys.exit(1)
    else:
        # Multiple files
        results = read_multiple_files(project_id, file_paths, ref)
        if results:
            for file_path, content in results.items():
                print(f"=== Content of {file_path} ===")
                print(content)
                print("\n" + "=" * 50 + "\n")
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()