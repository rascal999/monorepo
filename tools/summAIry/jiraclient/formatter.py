import sys
from .comments import CommentManager
from .stakeholders import StakeholderManager
from .links import LinkManager

class IssueFormatter:
    def __init__(self, client):
        self.client = client
        self.comment_manager = CommentManager(client)
        self.stakeholder_manager = StakeholderManager(client)
        self.link_manager = LinkManager(client)

    def format_ticket_data(self, issues):
        """Format ticket data for the LLM"""
        formatted = []
        all_stakeholders = set()
        
        for issue in issues:
            print(f"Processing data for {issue.key}...", file=sys.stderr)
            
            # Get all related data
            comments = self.comment_manager.get_comments(issue)
            stakeholders = self.stakeholder_manager.get_stakeholders(issue)
            linked_issues = self.link_manager.get_linked_issues(issue)
            
            # Add stakeholders to global set
            all_stakeholders.update(stakeholders)
            
            # Format linked issues
            links = []
            for link in linked_issues:
                formatted_link = self.link_manager.format_link_data(link)
                if formatted_link:
                    links.append(formatted_link)
            
            # Format ticket data
            ticket = {
                'key': issue.key,
                'summary': issue.fields.summary,
                'description': issue.fields.description or '',
                'status': issue.fields.status.name,
                'type': issue.fields.issuetype.name,
                'comments': comments,
                'stakeholders': stakeholders,
                'links': links
            }
            
            # Add epic information if available
            if hasattr(issue.fields, 'customfield_10014') and issue.fields.customfield_10014:
                ticket['epic'] = issue.fields.customfield_10014
            
            # Add subtasks if available
            if hasattr(issue.fields, 'subtasks') and issue.fields.subtasks:
                ticket['subtasks'] = [
                    {'key': subtask.key, 'summary': subtask.fields.summary}
                    for subtask in issue.fields.subtasks
                ]
            
            formatted.append(ticket)
        
        # Add consolidated stakeholders list at the top level
        return {
            'tickets': formatted,
            'stakeholders': list(all_stakeholders)
        }