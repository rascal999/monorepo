from typing import List, Optional

from .jira_client import JiraClient, logger
from .types import Document

class JiraLinks(JiraClient):
    """Handles Jira issue link operations."""

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

    def get_issue_links(self, issue_key: str) -> List[dict]:
        """
        Get all links for a Jira issue.

        Args:
            issue_key: The issue key to get links for

        Returns:
            List of link details including IDs and relationship types
        """
        try:
            issue = self.jira.issue(issue_key, fields="issuelinks")
            links = []
            
            for link in issue["fields"].get("issuelinks", []):
                link_data = {
                    "id": link["id"],
                    "type": link["type"]["name"],
                }
                
                if "inwardIssue" in link:
                    link_data.update({
                        "direction": "inward",
                        "issue_key": link["inwardIssue"]["key"],
                        "issue_summary": link["inwardIssue"]["fields"]["summary"]
                    })
                elif "outwardIssue" in link:
                    link_data.update({
                        "direction": "outward",
                        "issue_key": link["outwardIssue"]["key"],
                        "issue_summary": link["outwardIssue"]["fields"]["summary"]
                    })
                
                links.append(link_data)
            
            return links

        except Exception as e:
            logger.error(f"Error getting links for issue {issue_key}: {str(e)}")
            raise

    def remove_link(self, issue_key: str, link_id: str) -> Document:
        """
        Remove a link between two Jira issues.

        Args:
            issue_key: Key of the issue to return after removing the link
            link_id: ID of the link to remove

        Returns:
            Document containing the updated issue
        """
        try:
            # Remove the link
            self.jira.remove_issue_link(link_id)
            
            # Return the updated issue
            return self.get_issue(issue_key)

        except Exception as e:
            logger.error(f"Error removing link {link_id} from issue {issue_key}: {str(e)}")
            raise