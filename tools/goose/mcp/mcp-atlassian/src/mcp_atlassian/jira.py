import logging
import os
from datetime import datetime
from typing import List, Optional

from atlassian import Jira
from dotenv import load_dotenv

from .config import JiraConfig
from .preprocessing import TextPreprocessor
from .types import Document

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("mcp-jira")


class JiraFetcher:
    """Handles fetching, creating, and editing content in Jira."""

    def __init__(self):
        url = os.getenv("JIRA_URL")
        username = os.getenv("JIRA_USERNAME")
        token = os.getenv("JIRA_API_TOKEN")

        if not all([url, username, token]):
            raise ValueError("Missing required Jira environment variables")

        self.config = JiraConfig(url=url, username=username, api_token=token)
        self.jira = Jira(
            url=self.config.url,
            username=self.config.username,
            password=self.config.api_token,  # API token is used as password
            cloud=True,
        )
        self.preprocessor = TextPreprocessor(self.config.url)

    def _clean_text(self, text: str) -> str:
        """
        Clean text content by:
        1. Processing user mentions and links
        2. Converting HTML/wiki markup to markdown
        """
        if not text:
            return ""

        return self.preprocessor.clean_jira_text(text)

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

    def search_issues(
        self, jql: str, fields: str = "*all", start: int = 0, limit: int = 50, expand: Optional[str] = None
    ) -> List[Document]:
        """
        Search for issues using JQL.

        Args:
            jql: JQL query string
            fields: Comma-separated string of fields to return
            start: Starting index
            limit: Maximum results to return
            expand: Fields to expand

        Returns:
            List of Documents containing matching issues
        """
        try:
            results = self.jira.jql(jql, fields=fields, start=start, limit=limit, expand=expand)

            documents = []
            for issue in results["issues"]:
                try:
                    # Get full issue details
                    doc = self.get_issue(issue["key"], expand=expand)
                    documents.append(doc)
                except Exception as e:
                    logger.error(f"Error processing issue {issue['key']}: {str(e)}")
                    continue

            return documents

        except Exception as e:
            logger.error(f"Error searching issues with JQL {jql}: {str(e)}")
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

    def link_issues(
        self,
        inward_issue: str,
        outward_issue: str,
        link_type: str = "Relates",
        comment: Optional[str] = None
    ) -> Document:
        """
        Create a link between two Jira issues.

        Args:
            inward_issue: Key of the issue that is the source of the link
            outward_issue: Key of the issue that is the target of the link
            link_type: Type of link (e.g., 'Relates', 'Blocks', 'Depends')
            comment: Optional comment to add to the link

        Returns:
            Document containing the updated source issue
        """
        try:
            # Get available link types
            link_types = self.jira.get_issue_link_types()
            link_type_id = None
            for lt in link_types:
                if lt['name'].lower() == link_type.lower():
                    link_type_id = lt['id']
                    break
            
            if not link_type_id:
                raise ValueError(f"Link type '{link_type}' not found. Available types: {', '.join(lt['name'] for lt in link_types)}")

            # Create the link data
            link_data = {
                "type": {"name": link_type},
                "inwardIssue": {"key": inward_issue},
                "outwardIssue": {"key": outward_issue}
            }
            if comment:
                link_data["comment"] = {"body": comment}

            # Create the link
            self.jira.create_issue_link(link_data)
            
            # Return the updated inward issue
            return self.get_issue(inward_issue)

        except Exception as e:
            logger.error(f"Error linking issues {inward_issue} and {outward_issue}: {str(e)}")
            raise

    def get_project_issues(self, project_key: str, start: int = 0, limit: int = 50) -> List[Document]:
        """
        Get all issues for a project.

        Args:
            project_key: The project key
            start: Starting index
            limit: Maximum results to return

        Returns:
            List of Documents containing project issues
        """
        jql = f"project = {project_key} ORDER BY created DESC"
        return self.search_issues(jql, start=start, limit=limit)
