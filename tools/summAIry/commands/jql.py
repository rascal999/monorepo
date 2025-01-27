import re
from .base import BaseCommandHandler
from jql_validator import JQLValidator
from color_utils import Colors
from prompts import JQL_QUERY

class JQLCommandHandler(BaseCommandHandler):
    def handle_jql(self, cmd, current_ticket=None, ticket_data=None):
        """Handle JQL search command"""
        # Validate and fix JQL query
        original_query = cmd['query']
        fixed_query = JQLValidator.validate_and_fix(original_query)
        
        # Handle LIMIT clause
        max_results = 50  # Default
        if 'LIMIT' in fixed_query.upper():
            # Extract limit value
            limit_match = re.search(r'LIMIT\s+(\d+)', fixed_query, re.IGNORECASE)
            if limit_match:
                max_results = int(limit_match.group(1))
            # Remove LIMIT clause as it's not supported in JQL
            fixed_query = JQLValidator.fix_maxResults(fixed_query)
        
        if fixed_query != original_query:
            print(f"\nFixed JQL query: {Colors.colorize(fixed_query, Colors.YELLOW)}")
        else:
            print(f"\nExecuting JQL: {Colors.colorize(fixed_query, Colors.YELLOW)}")
        
        # Get all results and handle limit manually
        issues = self.jira.search_issues(fixed_query)
        if not issues:
            return self.error("No tickets found")
        
        # Limit results if needed
        if len(issues) > max_results:
            issues = issues[:max_results]
        
        # Store first issue for comments command
        if issues:
            self.last_issue = issues[0]
            
        result = []
        print("\nFound tickets:")
        for issue in issues:
            ticket_info = self.format_ticket_info(issue)
            result.append(ticket_info)
            print(ticket_info)
        result = "\n".join(result)
        
        # Add to history
        self.add_to_history(cmd, result, current_ticket, ticket_data)
        return True
def get_command_context(self, query, history_context=""):
    """Get context for JQL commands"""
    return JQL_QUERY.format(
        history_context=history_context,
        query=query
    )