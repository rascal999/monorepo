import sys
from jira.exceptions import JIRAError

class StakeholderManager:
    def __init__(self, client):
        self.client = client

    def get_stakeholders(self, issue):
        """Extract stakeholders from ticket"""
        stakeholders = set()
        
        try:
            # Add reporter
            if hasattr(issue.fields, 'reporter') and issue.fields.reporter:
                stakeholders.add((
                    issue.fields.reporter.displayName,
                    'Reporter',
                    issue.fields.reporter.emailAddress
                ))
            
            # Add assignee
            if hasattr(issue.fields, 'assignee') and issue.fields.assignee:
                stakeholders.add((
                    issue.fields.assignee.displayName,
                    'Assignee',
                    issue.fields.assignee.emailAddress
                ))
            
            # Add commenters
            try:
                comments = self.client.comments(issue)
                for comment in comments:
                    stakeholders.add((
                        comment.author.displayName,
                        'Commenter',
                        comment.author.emailAddress
                    ))
            except JIRAError as e:
                print(f"Warning: Could not fetch commenters for {issue.key}: {e}", file=sys.stderr)
            
            # Add watchers
            try:
                watchers = self.client.watchers(issue)
                for watcher in watchers.watchers:
                    stakeholders.add((
                        watcher.displayName,
                        'Watcher',
                        watcher.emailAddress
                    ))
            except JIRAError as e:
                print(f"Warning: Could not fetch watchers for {issue.key}: {e}", file=sys.stderr)
            
            return list(stakeholders)
            
        except Exception as e:
            print(f"Warning: Error fetching stakeholders for {issue.key}: {e}", file=sys.stderr)
            return []