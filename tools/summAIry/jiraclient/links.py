import sys
from jira.exceptions import JIRAError

class LinkManager:
    def __init__(self, client):
        self.client = client
        self.visited = set()  # Track visited tickets to prevent cycles

    def get_linked_issues(self, issue):
        """Get all linked issues"""
        linked_issues = []
        
        # Skip if we've already processed this ticket
        if issue.key in self.visited:
            return linked_issues
            
        self.visited.add(issue.key)
        
        try:
            if hasattr(issue.fields, 'issuelinks') and issue.fields.issuelinks:
                print(f"Fetching linked issues for {issue.key}...", file=sys.stderr)
                for link in issue.fields.issuelinks:
                    try:
                        if hasattr(link, 'outwardIssue'):
                            linked_key = link.outwardIssue.key
                            if linked_key not in self.visited:
                                linked = self.client.issue(linked_key)
                                linked_issues.append({
                                    'issue': linked,
                                    'type': link.type.outward,
                                    'direction': 'outward'
                                })
                                
                                # Recursively get links from linked issues
                                nested_links = self.get_linked_issues(linked)
                                linked_issues.extend(nested_links)
                            
                        elif hasattr(link, 'inwardIssue'):
                            linked_key = link.inwardIssue.key
                            if linked_key not in self.visited:
                                linked = self.client.issue(linked_key)
                                linked_issues.append({
                                    'issue': linked,
                                    'type': link.type.inward,
                                    'direction': 'inward'
                                })
                                
                                # Recursively get links from linked issues
                                nested_links = self.get_linked_issues(linked)
                                linked_issues.extend(nested_links)
                            
                    except JIRAError as e:
                        print(f"Warning: Could not fetch linked issue: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Error processing issue links for {issue.key}: {e}", file=sys.stderr)
        
        return linked_issues

    def format_link_data(self, link):
        """Format a link for output"""
        try:
            return {
                'key': link['issue'].key,
                'summary': link['issue'].fields.summary,
                'type': link['type'],
                'direction': link['direction']
            }
        except Exception as e:
            print(f"Warning: Error formatting link data: {e}", file=sys.stderr)
            return None