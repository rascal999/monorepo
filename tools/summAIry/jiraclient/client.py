import sys
from jira import JIRA
from jira.exceptions import JIRAError
from datetime import datetime, timedelta

class JiraClient:
    def __init__(self, url, email, token):
        self.url = url
        self.email = email
        self.token = token
        self.client = None

    def connect(self):
        """Initialize and test Jira connection"""
        print(f"Connecting to Jira at {self.url}...", file=sys.stderr)
        try:
            self.client = JIRA(
                server=self.url,
                basic_auth=(self.email, self.token)
            )
            # Test connection
            self.client.myself()
            return True
        except JIRAError as e:
            if e.status_code == 401:
                print("Error: Invalid Jira credentials", file=sys.stderr)
            else:
                print(f"Error connecting to Jira: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Unexpected error while connecting to Jira: {e}", file=sys.stderr)
            return False

    def get_issue(self, issue_id):
        """Fetch a single issue"""
        if not self.client:
            print("Error: Not connected to Jira", file=sys.stderr)
            return None

        try:
            return self.client.issue(issue_id)
        except JIRAError as e:
            if e.status_code == 404:
                print(f"Error: Issue {issue_id} not found or no access", file=sys.stderr)
            else:
                print(f"Error fetching issue: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return None

    def search_issues(self, jql, max_results=50):
        """Search for issues using JQL"""
        if not self.client:
            print("Error: Not connected to Jira", file=sys.stderr)
            return None

        try:
            return self.client.search_issues(jql, maxResults=max_results)
        except JIRAError as e:
            print(f"Error searching issues: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return None

    def get_recent_issues_by_user(self, username, days=30):
        """Get issues created by user in the last N days"""
        if not self.client:
            print("Error: Not connected to Jira", file=sys.stderr)
            return None

        date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        jql = f'creator = "{username}" AND created >= {date} ORDER BY created DESC'
        
        try:
            print(f"Searching for tickets created by {username} since {date}...", file=sys.stderr)
            return self.search_issues(jql)
        except JIRAError as e:
            print(f"Error searching issues: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return None

    def get_user_info(self, username):
        """Get user information"""
        if not self.client:
            print("Error: Not connected to Jira", file=sys.stderr)
            return None

        try:
            return self.client.search_users(username)
        except JIRAError as e:
            print(f"Error searching user: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return None

    def add_comment(self, issue_id, comment_text):
        """Add a comment to an issue"""
        if not self.client:
            print("Error: Not connected to Jira", file=sys.stderr)
            return False

        try:
            issue = self.get_issue(issue_id)
            if not issue:
                return False
                
            self.client.add_comment(issue, comment_text)
            return True
        except JIRAError as e:
            print(f"Error adding comment: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return False