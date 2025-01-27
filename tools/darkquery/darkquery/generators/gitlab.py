"""GitLab query generator implementation."""
import logging
from typing import Any, Dict, Optional


class GitLabQueryGenerator:
    """Generator for GitLab API queries."""

    def __init__(self):
        """Initialize GitLab query generator."""
        self.logger = logging.getLogger("darkquery.gitlab")

    def generate(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate GitLab API parameters from natural language query.
        
        Args:
            query: Natural language query string
            context: Optional context information
            
        Returns:
            Dict containing GitLab API parameters
        """
        params = {}
        query = query.lower()

        # Handle common query patterns
        if "open" in query:
            params["state"] = "opened"
        elif "closed" in query:
            params["state"] = "closed"
        elif "merged" in query:
            params["state"] = "merged"

        if "created this week" in query:
            params["created_after"] = "week"
        elif "created today" in query:
            params["created_after"] = "day"

        if "assigned to me" in query and context and "username" in context:
            params["assignee_username"] = context["username"]
        elif "created by me" in query and context and "username" in context:
            params["author_username"] = context["username"]

        if "label" in query:
            # Extract label after "label:" or "label "
            import re
            label_match = re.search(r"label[:\s]+(\w+)", query)
            if label_match:
                params["labels"] = label_match.group(1)

        # Determine scope
        params["scope"] = "all"
        if "projects" in query or "project list" in query or "list projects" in query:
            params["scope"] = "projects"
        elif "issues" in query:
            params["scope"] = "issues"
        elif "merge requests" in query or "mr" in query:
            params["scope"] = "merge_requests"

        # Handle group project listing
        if params["scope"] == "projects" and "in group" in query:
            # Extract group name (e.g., "projects in group appsec" -> "appsec")
            import re
            group_match = re.search(r"in group\s+(\w+)", query)
            if group_match:
                params["query"] = f"project={group_match.group(1)}/*"

        # Default ordering
        params["order_by"] = "created_at"
        params["sort"] = "desc"

        return params

    def validate_query(self, query: str) -> bool:
        """Validate if a query can be processed for GitLab.
        
        Args:
            query: Query string to validate
            
        Returns:
            bool indicating if query is valid
        """
        # GitLab queries are quite flexible, mainly validate it's not empty
        return bool(query and query.strip())