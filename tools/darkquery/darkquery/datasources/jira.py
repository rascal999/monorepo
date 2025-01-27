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
            limit = query.get('limit')  # No default limit
            
            # Validate JQL from Ollama
            jql = self.jql_generator.generate(jql, context)
            
            # Execute JQL query
            if limit:
                self.logger.debug(f"Executing JQL: {jql} with limit {limit}")
                issues = self.client.search_issues(jql, maxResults=limit)
            else:
                self.logger.debug(f"Executing JQL: {jql} without limit")
                issues = self.client.search_issues(jql)
            
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
                if limit == 1 or len(issues) == 1:
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
    
    def delete_ticket(self, ticket_ids: List[str]) -> QueryResult:
        """Delete one or more JIRA tickets.
        
        Args:
            ticket_ids: List of JIRA ticket IDs to delete
            
        Returns:
            QueryResult containing the result of the operation
        """
        try:
            # Delete each ticket
            for ticket_id in ticket_ids:
                # Get issue first to validate it exists
                issue = self.client.issue(ticket_id)
                
                # Delete the issue
                issue.delete()
            
            return QueryResult(
                success=True,
                data={"tickets": ticket_ids},
                message=f"Successfully deleted {len(ticket_ids)} ticket(s)"
            )
            
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'response') and hasattr(e.response, 'json'):
                try:
                    error_data = e.response.json()
                    if 'errorMessages' in error_data and error_data['errorMessages']:
                        error_msg = error_data['errorMessages'][0]
                except:
                    pass
                    
            # Log full trace if verbose
            if self.verbose:
                self.logger.exception(f"Error deleting tickets: {ticket_ids}")
            else:
                self.logger.error(f"Error deleting tickets: {error_msg}")
                
            return QueryResult(
                success=False,
                data=None,
                message=error_msg
            )
            
    def add_comment(self, ticket_id: str, comment: str) -> QueryResult:
        """Add a comment to a JIRA ticket.
        
        Args:
            ticket_id: The JIRA ticket ID/key
            comment: The comment text to add
            
        Returns:
            QueryResult containing the result of the operation
        """
        try:
            # Get issue first to validate it exists
            issue = self.client.issue(ticket_id)
            
            # Add the comment
            self.client.add_comment(issue, comment)
            
            return QueryResult(
                success=True,
                data={"ticket": ticket_id, "comment": comment},
                message=f"Comment added successfully to {ticket_id}"
            )
            
        except Exception as e:
            self.logger.exception(f"Error adding comment to ticket {ticket_id}")
            return QueryResult(
                success=False,
                data=None,
                message=f"Error adding comment: {str(e)}"
            )
    
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