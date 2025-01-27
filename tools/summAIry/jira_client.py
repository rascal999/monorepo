from jira.exceptions import JIRAError
from jiraclient import JiraClient, IssueFormatter

class JiraTicketManager:
    def __init__(self, url, email, token):
        self.client = JiraClient(url, email, token)
        self.formatter = None

    def connect(self):
        """Initialize connection to Jira"""
        if self.client.connect():
            self.formatter = IssueFormatter(self.client.client)
            return True
        return False

    def get_related_tickets(self, ticket_id):
        """Fetch the ticket and all related tickets (children, epics, links)"""
        if not self.client.client:
            print("Error: Not connected to Jira")
            return None

        issues = []
        try:
            # Get main ticket
            issue = self.client.get_issue(ticket_id)
            if not issue:
                return None
            issues.append(issue)
            
            # Get epic if ticket is part of one
            if hasattr(issue.fields, 'customfield_10014') and issue.fields.customfield_10014:
                epic = self.client.get_issue(issue.fields.customfield_10014)
                if epic:
                    issues.append(epic)
            
            # Get subtasks/children
            if issue.fields.subtasks:
                for subtask in issue.fields.subtasks:
                    child = self.client.get_issue(subtask.key)
                    if child:
                        issues.append(child)
            
            return issues
            
        except JIRAError as e:
            print(f"Error accessing Jira: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def format_ticket_data(self, issues):
        """Format ticket data for the LLM"""
        if not self.formatter:
            print("Error: Not connected to Jira")
            return None
            
        return self.formatter.format_ticket_data(issues)