import os
import base64
import requests
from urllib.parse import quote, urlparse
from smolagents import tool

def _get_gitlab_headers():
    """Get GitLab API headers with authentication."""
    token = os.getenv("GITLAB_TOKEN")
    if not token:
        raise ValueError("GITLAB_TOKEN environment variable is not set")
    return {
        "PRIVATE-TOKEN": token,
        "Accept": "application/json",
    }

def _extract_project_path(project_id: str) -> str:
    """Extract project path from URL or return project_id if it's already a path."""
    if project_id.startswith(('http://', 'https://')):
        parsed = urlparse(project_id)
        # Remove the domain and leading slash
        path = parsed.path.lstrip('/')
        print(f"DEBUG: Extracted project path '{path}' from URL '{project_id}'")
        return path
    return project_id

def _try_refs(file_url: str, headers: dict, file_path: str, project_id: str) -> tuple[str, str]:
    """Try different refs (main, master) to get file content."""
    for ref in ['main', 'master']:
        print(f"DEBUG: Trying ref: {ref}")
        response = requests.get(file_url, headers=headers, params={"ref": ref})
        print(f"DEBUG: Response status for {ref}: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            content = base64.b64decode(data['content']).decode('utf-8')
            return f"File: {file_path} (ref: {ref})\n\n{content}", None
            
    return None, f"File not found: {file_path} in project {project_id} (tried refs: main, master)"

def _get_group_info(gitlab_url: str, headers: dict, group_path: str) -> tuple[list, str]:
    """Get information about a GitLab group and its subgroups."""
    result = []
    error = None
    
    try:
        # Get group information
        group_url = f"{gitlab_url}/api/v4/groups/{quote(group_path, safe='')}"
        response = requests.get(group_url, headers=headers)
        
        if response.status_code == 200:
            group = response.json()
            result.append(f"Group: {group['full_name']}")
            result.append(f"Description: {group.get('description', 'No description')}")
            result.append(f"Visibility: {group['visibility']}")
            result.append(f"URL: {group['web_url']}\n")

            # Get subgroups
            subgroups_url = f"{gitlab_url}/api/v4/groups/{quote(group_path, safe='')}/subgroups"
            response = requests.get(subgroups_url, headers=headers)
            
            if response.status_code == 200:
                subgroups = response.json()
                if subgroups:
                    result.append("Subgroups:")
                    for subgroup in subgroups:
                        result.append(f"- {subgroup['name']}")
                        result.append(f"  Full path: {subgroup['full_path']}")
                        result.append(f"  Visibility: {subgroup['visibility']}")
                        result.append(f"  URL: {subgroup['web_url']}\n")

            # Get projects in the group
            projects_url = f"{gitlab_url}/api/v4/groups/{quote(group_path, safe='')}/projects"
            response = requests.get(projects_url, headers=headers, params={"include_subgroups": True})
            
            if response.status_code == 200:
                projects = response.json()
                if projects:
                    result.append("Projects:")
                    for project in projects:
                        result.append(f"- {project['name']}")
                        result.append(f"  Full path: {project['path_with_namespace']}")
                        result.append(f"  Description: {project.get('description', 'No description')}")
                        result.append(f"  Visibility: {project['visibility']}")
                        result.append(f"  URL: {project['web_url']}\n")
        else:
            error = f"Failed to get group info: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        error = str(e)
        
    return result, error

@tool
def gitlab_search(query: str) -> str:
    """
    Search GitLab groups, projects, and issues.

    Args:
        query: The search query for GitLab.
        Examples:
        - "security in:title" (search in titles)
        - "author:john" (search by author)
        - "created_after:2025-01-01" (search by date)
        - "mangopay/appsec" (search in specific group)

    Returns:
        A string containing search results.
    """
    try:
        gitlab_url = os.getenv("GITLAB_URL")
        headers = _get_gitlab_headers()
        result = []

        # Check if query contains a group path
        if '/' in query and not any(keyword in query for keyword in ['in:', 'author:', 'created_']):
            # Search for groups
            group_path = query.strip()
            result, error = _get_group_info(gitlab_url, headers, group_path)
            
            if error:
                if "404" in error:
                    return "Group not found. Check if the path is correct and you have access to it."
                elif "403" in error:
                    return "Access denied. Check if you have the necessary permissions."
                return f"Error searching group: {error}"
                
        else:
            # Regular search for projects
            projects_url = f"{gitlab_url}/api/v4/projects"
            params = {
                "search": query,
                "per_page": 3
            }
            
            response = requests.get(projects_url, headers=headers, params=params)
            response.raise_for_status()
            
            projects = response.json()
            if projects:
                result.append("Projects:")
                for project in projects:
                    result.append(f"- {project['name']}")
                    result.append(f"  Full path: {project['path_with_namespace']}")
                    result.append(f"  Description: {project.get('description', 'No description')}")
                    result.append(f"  Visibility: {project['visibility']}")
                    result.append(f"  URL: {project['web_url']}\n")
            
            # Search issues
            issues_url = f"{gitlab_url}/api/v4/issues"
            params = {
                "search": query,
                "per_page": 3,
                "scope": "all"
            }
            
            response = requests.get(issues_url, headers=headers, params=params)
            response.raise_for_status()
            
            issues = response.json()
            if issues:
                result.append("Issues:")
                for issue in issues:
                    result.append(f"- {issue['title']}")
                    result.append(f"  Project: {issue['references']['full']}")
                    result.append(f"  State: {issue['state']}")
                    result.append(f"  URL: {issue['web_url']}\n")
        
        return "\n".join(result) if result else "No results found in GitLab."
        
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 404:
                return "Group or project not found. Check if the path is correct and you have access to it."
            elif e.response.status_code == 403:
                return "Access denied. Check if you have the necessary permissions."
        return f"Error searching GitLab: {str(e)}"

@tool
def get_gitlab_file(project_id: str, file_path: str, ref: str = None) -> str:
    """
    Get the contents of a file from GitLab.

    Args:
        project_id: The project ID or path (e.g., "group/project") or URL
        file_path: Path to the file in the repository
        ref: Branch name or commit SHA (optional, will try main and master if not specified)

    Examples:
        - get_gitlab_file("mygroup/myproject", "README.md")
        - get_gitlab_file("12345", "src/main.py", "develop")
        - get_gitlab_file("https://gitlab.com/org/repo", ".gitlab-ci.yml")

    Returns:
        A string containing the file contents.
    """
    try:
        gitlab_url = os.getenv("GITLAB_URL")
        if not gitlab_url:
            return "GITLAB_URL environment variable is not set"
            
        print(f"DEBUG: Using GitLab URL: {gitlab_url}")
        
        headers = _get_gitlab_headers()
        print(f"DEBUG: Headers set (token: {'present' if 'PRIVATE-TOKEN' in headers else 'missing'})")
        
        # Extract project path if URL was provided
        project_path = _extract_project_path(project_id)
        
        # URL encode both project_path and file_path
        encoded_project = quote(project_path, safe='')
        encoded_path = quote(file_path, safe='')
        
        file_url = f"{gitlab_url}/api/v4/projects/{encoded_project}/repository/files/{encoded_path}"
        print(f"DEBUG: Base URL: {file_url}")
        
        if ref:
            # Try specific ref if provided
            print(f"DEBUG: Using specified ref: {ref}")
            response = requests.get(file_url, headers=headers, params={"ref": ref})
            print(f"DEBUG: Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content = base64.b64decode(data['content']).decode('utf-8')
                return f"File: {file_path} (ref: {ref})\n\n{content}"
            elif response.status_code == 401:
                return "GitLab authentication failed. Check your GITLAB_TOKEN."
        else:
            # Try main and master
            content, error = _try_refs(file_url, headers, file_path, project_path)
            if content:
                return content
            return error
            
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Request error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"DEBUG: Response content: {e.response.text}")
        return f"Error fetching file from GitLab: {str(e)}"
    except Exception as e:
        print(f"DEBUG: Unexpected error: {str(e)}")
        return f"Error: {str(e)}"

@tool
def list_gitlab_branches(project_id: str) -> str:
    """
    List branches in a GitLab project.

    Args:
        project_id: The project ID or path (e.g., "group/project") or URL

    Returns:
        A string containing the list of branches.
    """
    try:
        gitlab_url = os.getenv("GITLAB_URL")
        headers = _get_gitlab_headers()
        
        # Extract project path if URL was provided
        project_path = _extract_project_path(project_id)
        
        # URL encode project_path
        encoded_project = quote(project_path, safe='')
        branches_url = f"{gitlab_url}/api/v4/projects/{encoded_project}/repository/branches"
        
        print(f"DEBUG: Requesting URL: {branches_url}")
        response = requests.get(branches_url, headers=headers)
        print(f"DEBUG: Response status: {response.status_code}")
        
        if response.status_code == 401:
            return "GitLab authentication failed. Check your GITLAB_TOKEN."
            
        response.raise_for_status()
        
        branches = response.json()
        if not branches:
            return f"No branches found in project {project_path}"
            
        result = [f"Branches in {project_path}:"]
        for branch in branches:
            result.append(f"- {branch['name']}")
            if branch.get('default', False):
                result[-1] += " (default)"
            commit = branch.get('commit', {})
            result.append(f"  Last commit: {commit.get('title', 'Unknown')}")
            result.append(f"  Updated: {commit.get('committed_date', 'Unknown')}\n")
            
        return "\n".join(result)
        
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Request error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"DEBUG: Response content: {e.response.text}")
        return f"Error listing branches: {str(e)}"

@tool
def get_gitlab_commits(project_id: str, ref: str = None, limit: int = 5) -> str:
    """
    Get recent commits from a GitLab project.

    Args:
        project_id: The project ID or path (e.g., "group/project") or URL
        ref: Branch name or commit SHA (optional, will try main and master if not specified)
        limit: Number of commits to fetch (default: 5)

    Returns:
        A string containing recent commits.
    """
    try:
        gitlab_url = os.getenv("GITLAB_URL")
        headers = _get_gitlab_headers()
        
        # Extract project path if URL was provided
        project_path = _extract_project_path(project_id)
        
        # URL encode project_path
        encoded_project = quote(project_path, safe='')
        commits_url = f"{gitlab_url}/api/v4/projects/{encoded_project}/repository/commits"
        
        if not ref:
            # Try to find the default branch
            for default_ref in ['main', 'master']:
                print(f"DEBUG: Trying ref: {default_ref}")
                response = requests.get(commits_url, headers=headers, params={"ref_name": default_ref, "per_page": limit})
                if response.status_code == 200:
                    ref = default_ref
                    break
        
        if not ref:
            return f"Could not determine default branch for {project_path}"
            
        params = {
            "ref_name": ref,
            "per_page": limit
        }
        
        print(f"DEBUG: Requesting URL: {commits_url}")
        print(f"DEBUG: With params: {params}")
        response = requests.get(commits_url, headers=headers, params=params)
        print(f"DEBUG: Response status: {response.status_code}")
        
        if response.status_code == 401:
            return "GitLab authentication failed. Check your GITLAB_TOKEN."
            
        response.raise_for_status()
        
        commits = response.json()
        if not commits:
            return f"No commits found in {project_path} (ref: {ref})"
            
        result = [f"Recent commits in {project_path} (ref: {ref}):"]
        for commit in commits:
            result.append(f"- {commit['short_id']}: {commit['title']}")
            result.append(f"  Author: {commit['author_name']}")
            result.append(f"  Date: {commit['committed_date']}\n")
            
        return "\n".join(result)
        
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Request error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"DEBUG: Response content: {e.response.text}")
        return f"Error fetching commits: {str(e)}"