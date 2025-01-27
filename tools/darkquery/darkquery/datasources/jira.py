"""JIRA data source implementation."""
import logging
from typing import Any, Dict, List, Optional

from jira import JIRA
from .base import DataSource, QueryResult
from ..generators.jql import JQLGenerator


class JIRADataSource(DataSource):
    """JIRA data source implementation."""
    
    DEFAULT_LIMIT = 5  # Default number of results to return
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        """Initialize JIRA data source.
        
        Args:
            config: Optional configuration dictionary containing:
                   - url: JIRA instance URL
                   - email: JIRA email
                   - token: JIRA API token
        """
        self.config = config or {}
        self.logger = logging.getLogger("darkquery.jira")
        self.jql_generator = JQLGenerator()
        
        # Initialize JIRA client
        self.client = JIRA(
            server=self.config['url'],
            basic_auth=(self.config['email'], self.config['token'])
        )
    
    def query(self, query: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute a query against JIRA.
        
        Args:
            query: Query dictionary containing:
                  - query: JQL query string
                  - limit: Number of results to return
            context: Optional context information
            
        Returns:
            QueryResult containing the query results
        """
        try:
            # Extract JQL and limit from query
            jql = query.get('query')
            limit = query.get('limit', self.DEFAULT_LIMIT)
            
            # Validate JQL from Ollama
            jql = self.jql_generator.generate(jql, context)
            
            self.logger.debug(f"Executing JQL: {jql} with limit {limit}")
            
            # Execute JQL query with maxResults
            issues = self.client.search_issues(jql, maxResults=limit)
            
            # Format results
            results = []
            for issue in issues:
                # Basic fields for list view
                ticket = {
                    "key": issue.key,
                    "summary": issue.fields.summary,
                    "status": str(issue.fields.status)
                }
                
                # Add more fields for single ticket view
                if limit == 1:
                    # Get full ticket with comments
                    full_issue = self.client.issue(issue.key, expand='comments')
                    
                    ticket.update({
                        "description": full_issue.fields.description or "",
                        "priority": str(full_issue.fields.priority) if hasattr(full_issue.fields, 'priority') else None,
                        "assignee": str(full_issue.fields.assignee) if full_issue.fields.assignee else None,
                        "reporter": str(full_issue.fields.reporter) if full_issue.fields.reporter else None,
                        "created": str(full_issue.fields.created),
                        "updated": str(full_issue.fields.updated),
                        "labels": full_issue.fields.labels,
                        "components": [str(c) for c in full_issue.fields.components],
                        "type": str(full_issue.fields.issuetype),
                        "resolution": str(full_issue.fields.resolution) if full_issue.fields.resolution else None,
                        "comments": [
                            {
                                "author": str(comment.author),
                                "created": str(comment.created),
                                "body": comment.body
                            }
                            for comment in full_issue.fields.comment.comments
                        ] if hasattr(full_issue.fields, 'comment') else []
                    })
                
                results.append(ticket)
            
            return QueryResult(
                success=True,
                data=results,
                metadata={"jql": jql, "limit": limit}
            )
            
        except Exception as e:
            self.logger.exception("Error executing JIRA query")
            return QueryResult(
                success=False,
                data=None,
                message=f"Error executing query: {str(e)}"
            )
    
    def validate_query(self, query: Dict[str, Any]) -> bool:
        """Validate if a query can be processed for JIRA.
        
        Args:
            query: Query dictionary to validate
            
        Returns:
            bool indicating if query is valid
        """
        # Check required fields
        if not isinstance(query, dict):
            return False
            
        if 'query' not in query:
            return False
            
        # Validate JQL
        return self.jql_generator.validate_jql(query['query'])
    
    def get_capabilities(self) -> List[str]:
        """Get list of supported JIRA query capabilities.
        
        Returns:
            List of capability strings
        """
        return [
            "ticket_search",
            "ticket_details",
            "ticket_comments",
            "ticket_related",
            "ticket_status",
            "ticket_assignment"
        ]
    
    def get_schema(self) -> Dict[str, Any]:
        """Get JIRA schema information.
        
        Returns:
            Dict containing schema information
        """
        return {
            "ticket_fields": {
                "key": "string",
                "summary": "string",
                "description": "string",
                "status": "string",
                "assignee": "string",
                "reporter": "string",
                "created": "datetime",
                "updated": "datetime",
                "priority": "string",
                "type": "string",
                "resolution": "string",
                "labels": "list[string]",
                "components": "list[string]",
                "comments": "list[comment]"
            },
            "supported_queries": [
                "recent tickets",
                "tickets created this week",
                "open bugs",
                "critical bugs in progress",
                "tickets assigned to {user}",
                "unassigned tickets in current sprint"
            ]
        }