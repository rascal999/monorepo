import sys
from jira.exceptions import JIRAError

class CommentManager:
    def __init__(self, client):
        self.client = client

    def get_comments(self, issue):
        """Fetch comments for a ticket"""
        try:
            print(f"Fetching comments for {issue.key}...", file=sys.stderr)
            comments = self.client.comments(issue)
            return [
                {
                    'author': comment.author.displayName,
                    'body': comment.body,
                    'created': comment.created
                }
                for comment in comments
            ]
        except JIRAError as e:
            print(f"Warning: Could not fetch comments for {issue.key}: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"Warning: Error processing comments for {issue.key}: {e}", file=sys.stderr)
            return []