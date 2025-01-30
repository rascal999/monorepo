from datetime import datetime
from typing import List, Optional

from .jira_client import JiraClient, logger
from .types import Document

class JiraIssues(JiraClient):
    """Handles Jira issue operations."""

    def _parse_date(self, date_str: str) -> str:
        """Parse date string from Jira and return formatted date."""
        try:
            # Handle timezone offset in format +HHMM
            if '+' in date_str:
                date_part, tz_part = date_str.split('+')
                if len(tz_part) == 4:  # Format: HHMM
                    tz_part = f"{tz_part[:2]}:{tz_part[2:]}"
                date_str = f"{date_part}+{tz_part}"
            elif date_str.endswith('Z'):
                date_str = date_str.replace('Z', '+00:00')
            
            date = datetime.fromisoformat(date_str)
            return date.strftime("%Y-%m-%d")
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse date {date_str}: {str(e)}")
            return date_str

    def get_issue(self, issue_key: str, expand: Optional[str] = None) -> Document:
        """
        Get a single issue with all its details.

        Args:
            issue_key: The issue key (e.g. 'PROJ-123')
            expand: Optional fields to expand

        Returns:
            Document containing issue content and metadata
        """
        try:
            issue = self.jira.issue(issue_key, expand=expand)

            # Process description and comments
            description = self._clean_text(issue["fields"].get("description", ""))

            # Get comments
            comments = []
            if "comment" in issue["fields"]:
                for comment in issue["fields"]["comment"]["comments"]:
                    processed_comment = self._clean_text(comment["body"])
                    created = self._parse_date(comment["created"])
                    author = comment["author"].get("displayName", "Unknown")
                    comments.append(
                        {"body": processed_comment, "created": created, "author": author}
                    )

            # Format created date
            created_date = self._parse_date(issue["fields"]["created"])

            # Combine content in a more structured way
            content = f"""Issue: {issue_key}
Title: {issue['fields'].get('summary', '')}
Type: {issue['fields']['issuetype']['name']}
Status: {issue['fields']['status']['name']}
Created: {created_date}

Description:
{description}

Comments:
""" + "\n".join(
                [f"{c['created']} - {c['author']}: {c['body']}" for c in comments]
            )

            # Streamlined metadata with only essential information
            metadata = {
                "key": issue_key,
                "title": issue["fields"].get("summary", ""),
                "type": issue["fields"]["issuetype"]["name"],
                "status": issue["fields"]["status"]["name"],
                "created_date": created_date,
                "priority": issue["fields"].get("priority", {}).get("name", "None"),
                "link": f"{self.config.url.rstrip('/')}/browse/{issue_key}",
            }

            return Document(page_content=content, metadata=metadata)

        except Exception as e:
            logger.error(f"Error fetching issue {issue_key}: {str(e)}")
            raise

    def create_issue(
        self,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = "Task",
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ) -> Document:
        """
        Create a new Jira issue.

        Args:
            project_key: The project key where the issue will be created
            summary: Issue title/summary
            description: Detailed description of the issue
            issue_type: Type of issue (e.g., 'Task', 'Bug', 'Story')
            priority: Priority level (e.g., 'High', 'Medium', 'Low')
            assignee: Username of the assignee
            labels: List of labels to add to the issue

        Returns:
            Document containing the created issue
        """
        try:
            fields = {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type},
            }

            if priority:
                fields["priority"] = {"name": priority}
            if assignee:
                fields["assignee"] = {"name": assignee}
            if labels:
                fields["labels"] = labels

            new_issue = self.jira.create_issue(fields=fields)
            
            # Return the newly created issue as a Document
            return self.get_issue(new_issue["key"])

        except Exception as e:
            logger.error(f"Error creating issue in project {project_key}: {str(e)}")
            raise

    def update_issue(
        self,
        issue_key: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ) -> Document:
        """
        Update an existing Jira issue.

        Args:
            issue_key: The issue key to update (e.g., 'PROJ-123')
            summary: New summary/title
            description: New description
            status: New status
            priority: New priority level
            assignee: New assignee username
            labels: New list of labels (replaces existing labels)

        Returns:
            Document containing the updated issue
        """
        try:
            fields = {}
            
            if summary is not None:
                fields["summary"] = summary
            if description is not None:
                fields["description"] = description
            if priority is not None:
                fields["priority"] = {"name": priority}
            if assignee is not None:
                fields["assignee"] = {"name": assignee}
            if labels is not None:
                fields["labels"] = labels

            # Update the issue fields
            if fields:
                self.jira.update_issue_field(issue_key, fields)

            # Handle status transition if requested
            if status is not None:
                transitions = self.jira.get_issue_transitions(issue_key)
                transition_id = None
                for t in transitions:
                    if t["name"].lower() == status.lower():
                        transition_id = t["id"]
                        break
                
                if transition_id:
                    self.jira.transition_issue(issue_key, transition_id)
                else:
                    logger.warning(f"Could not find transition to status '{status}' for issue {issue_key}")

            # Return the updated issue
            return self.get_issue(issue_key)

        except Exception as e:
            logger.error(f"Error updating issue {issue_key}: {str(e)}")
            raise

    def add_comment(self, issue_key: str, comment: str) -> Document:
        """
        Add a comment to an existing Jira issue.

        Args:
            issue_key: The issue key to comment on (e.g., 'PROJ-123')
            comment: The comment text to add

        Returns:
            Document containing the updated issue with the new comment
        """
        try:
            self.jira.issue_add_comment(issue_key, comment)
            return self.get_issue(issue_key)

        except Exception as e:
            logger.error(f"Error adding comment to issue {issue_key}: {str(e)}")
            raise