import os
import requests
from smolagents import tool

def safe_get(d, *keys, default=""):
    """Safely get nested dictionary values."""
    for key in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(key)
        if d is None:
            return default
    return d

@tool
def jira_search(query: str) -> str:
    """
    Search Jira issues using JQL (Jira Query Language).

    Common JQL patterns:
    - Project: project = "SECOPS"
    - Status: status in ("Open", "In Progress", "To Do")
    - Priority: priority in ("High", "Highest")
    - Assignee: assignee = currentUser() or assignee = "John Smith"
    - Issue Type: issuetype = Bug
    
    Date queries:
    - Today: created >= startOfDay() AND created <= endOfDay()
    - Specific date (e.g., Feb 4, 2025): 
      project = SECOPS AND created >= "2025-02-04" AND created < "2025-02-05"
    - Date range: created >= "2025-02-01" AND created <= "2025-02-05"
    - Last 7 days: created >= -7d
    - Updated date: updated >= "2025-02-05"
    
    Other filters:
    - Labels: labels = security
    - Resolution: resolution = Unresolved
    - Components: component = "API"
    
    Ordering:
    - ORDER BY created DESC
    - ORDER BY priority DESC, updated ASC

    Example queries:
    - project = SECOPS AND status = Open
    - project = SECOPS AND created >= "2025-02-04" AND created < "2025-02-05"
    - project = SECOPS AND priority = High AND assignee = currentUser()
    - project = SECOPS AND issuetype = Bug AND status != Closed
    - project = SECOPS AND created >= -7d ORDER BY priority DESC

    Args:
        query: JQL query string (e.g., "project = SECOPS AND status = Open")

    Returns:
        A string containing Jira issue results.
    """
    try:
        jira_url = os.getenv("JIRA_URL")
        jira_username = os.getenv("JIRA_USERNAME")
        jira_token = os.getenv("JIRA_TOKEN")
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        auth = (jira_username, jira_token)
        search_url = f"{jira_url}/rest/api/2/search"
        
        # Send the JQL query
        response = requests.get(
            search_url,
            headers=headers,
            auth=auth,
            params={"jql": query, "maxResults": 5},
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Check if we have issues in the response
        if "issues" not in data or not data["issues"]:
            return f"No Jira issues found for query: {query}"
            
        result = []
        for issue in data["issues"]:
            fields = issue.get("fields", {})
            
            # Safely get nested values
            key = issue.get("key", "Unknown")
            summary = safe_get(fields, "summary", default="No summary")
            status = safe_get(fields, "status", "name", default="Unknown")
            assignee = safe_get(fields, "assignee", "displayName", default="Unassigned")
            priority = safe_get(fields, "priority", "name", default="None")
            created = fields.get("created", "Unknown")
            
            result.append(f"- {key}: {summary}")
            result.append(f"  Status: {status} | Priority: {priority} | Assignee: {assignee}")
            result.append(f"  Created: {created}")
            
        return "Found Jira issues:\n" + "\n".join(result)
        
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Jira: {str(e)}"
    except Exception as e:
        return f"Error searching Jira: {str(e)}"

@tool
def get_jira_ticket(ticket_id: str) -> str:
    """
    Get detailed information about a specific Jira ticket.

    The ticket_id should be in the format PROJECT-NUMBER (e.g., SECOPS-123).
    This will fetch:
    - Basic info (summary, status, priority, assignee)
    - Description
    - Creation and update dates
    - Recent comments (last 3)

    Args:
        ticket_id: The Jira ticket ID (e.g., "SECOPS-123")

    Returns:
        A string containing detailed ticket information.
    """
    try:
        jira_url = os.getenv("JIRA_URL")
        jira_username = os.getenv("JIRA_USERNAME")
        jira_token = os.getenv("JIRA_TOKEN")
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        auth = (jira_username, jira_token)
        issue_url = f"{jira_url}/rest/api/2/issue/{ticket_id}"
        
        response = requests.get(issue_url, headers=headers, auth=auth)
        response.raise_for_status()
        
        issue = response.json()
        fields = issue.get("fields", {})
        
        # Use safe_get for nested values
        key = issue.get("key", "Unknown")
        summary = safe_get(fields, "summary", default="No summary")
        status = safe_get(fields, "status", "name", default="Unknown")
        assignee = safe_get(fields, "assignee", "displayName", default="Unassigned")
        priority = safe_get(fields, "priority", "name", default="None")
        description = fields.get("description", "No description")
        created = fields.get("created", "Unknown")
        updated = fields.get("updated", "Unknown")
        
        # Format the output
        result = [
            f"Ticket: {key}",
            f"Summary: {summary}",
            f"Status: {status}",
            f"Priority: {priority}",
            f"Assignee: {assignee}",
            f"Created: {created}",
            f"Updated: {updated}",
            "",
            "Description:",
            description
        ]
        
        # Get comments if available
        comments_url = f"{issue_url}/comment"
        comments_response = requests.get(comments_url, headers=headers, auth=auth)
        if comments_response.status_code == 200:
            comments = comments_response.json().get("comments", [])
            if comments:
                result.append("\nRecent Comments:")
                for comment in comments[-3:]:  # Show last 3 comments
                    author = safe_get(comment, "author", "displayName", default="Unknown")
                    created = comment.get("created", "Unknown")
                    body = comment.get("body", "No content")
                    result.extend([
                        f"\n{author} ({created}):",
                        body
                    ])
        
        return "\n".join(result)
        
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Jira: {str(e)}"
    except Exception as e:
        return f"Error fetching Jira ticket: {str(e)}"