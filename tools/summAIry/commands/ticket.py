from .base import BaseCommandHandler
from color_utils import Colors

class TicketCommandHandler(BaseCommandHandler):
    def handle_fetch_ticket(self, cmd, current_ticket=None, ticket_data=None):
        """Handle fetch ticket command"""
        issue = self.jira.get_issue(cmd['ticket_id'])
        if not issue:
            return self.error(f"Could not fetch ticket {cmd['ticket_id']}")
        
        self.last_issue = issue  # Store for comments command
            
        result = []
        created = self.format_datetime(issue.fields.created)
        updated = self.format_datetime(issue.fields.updated)
        
        key = Colors.colorize(issue.key, Colors.CYAN + Colors.BOLD)
        status = Colors.colorize(issue.fields.status.name, Colors.status_color(issue.fields.status.name))
        timestamps = Colors.colorize(f"Created {created}, Updated {updated}", Colors.MAGENTA)
        
        print(f"\nTicket {key}:")
        result.append(f"Summary: {issue.fields.summary}")
        result.append(f"Status: {status}")
        result.append(f"Type: {issue.fields.issuetype.name}")
        result.append(f"Timestamps: {timestamps}")
        
        print("\n".join(result))
        if issue.fields.description:
            desc = f"\nDescription:\n{issue.fields.description}"
            result.append(desc)
            print(desc)
        result = "\n".join(result)
        
        # Add to history
        self.add_to_history(cmd, result, current_ticket, ticket_data)
        return True

    def handle_add_comment(self, cmd, current_ticket=None, ticket_data=None):
        """Handle add comment command"""
        ticket_id = cmd['ticket_id']
        comment = cmd['comment']
        
        # Show preview and ask for confirmation
        print(f"\nAbout to add comment to {Colors.colorize(ticket_id, Colors.CYAN)}")
        print(Colors.colorize("-" * 40, Colors.WHITE))
        print(comment)
        print(Colors.colorize("-" * 40, Colors.WHITE))
        
        confirm = input("\nAdd this comment? [y/N] ").strip().lower()
        if confirm == 'y':
            if self.jira.add_comment(ticket_id, comment):
                result = self.success("Comment added successfully")
                self.add_to_history(cmd, result, current_ticket, ticket_data)
                return True
            else:
                return self.error("Failed to add comment")
        else:
            return self.warning("Comment cancelled")

    def handle_comments(self, cmd, current_ticket=None, ticket_data=None):
        """Handle show comments command"""
        if not self.last_issue:
            return self.error("No ticket selected. Please fetch or search for a ticket first.")
        
        comments = self.jira.comments(self.last_issue)
        if not comments:
            result = self.warning(f"No comments found for {self.last_issue.key}")
            print(f"\n{result}")
            return True
        
        result = []
        key = Colors.colorize(self.last_issue.key, Colors.CYAN)
        print(f"\nComments for {key}:")
        for comment in comments:
            created = self.format_datetime(comment.created)
            updated = self.format_datetime(comment.updated)
            timestamp_info = f"Created {created}"
            if created != updated:
                timestamp_info += f", Updated {updated}"
                
            comment_text = [
                Colors.colorize("-" * 40, Colors.WHITE),
                Colors.colorize(f"Author: {comment.author.displayName}", Colors.GREEN) + 
                Colors.colorize(f" [{timestamp_info}]", Colors.MAGENTA),
                Colors.colorize("-" * 40, Colors.WHITE),
                comment.body,
                ""
            ]
            result.extend(comment_text)
            print("\n".join(comment_text))
        result = "\n".join(result)
        
        # Add to history
        self.add_to_history(cmd, result, current_ticket, ticket_data)
        return True

    def get_command_context(self, query, current_ticket=None, ticket_summary=None, ticket_data=None, chat_history=None, history_context=""):
        """Get context for ticket commands"""
        if current_ticket and ticket_data:
            return f"""Previous ticket summary ({current_ticket}):
{ticket_summary}

Chat history:
{chat_history or 'No previous chat messages'}

Full ticket data:
{ticket_data}
{history_context}

Available commands:
1. fetch_ticket - Fetch specific ticket
   Format: {{"type": "fetch_ticket", "ticket_id": "TICKET-123"}}

2. add_comment - Add a comment to a ticket (requires confirmation)
   Format: {{"type": "add_comment", "ticket_id": "TICKET-123", "comment": "Your comment text"}}

3. comments - Show comments from the last fetched/searched ticket
   Format: {{"type": "comments"}}

User query: {query}

If the user's query can be answered using one of these commands, respond with the appropriate command in JSON format.
Otherwise, provide a normal response based on the available context.
"""
        else:
            return None  # Let other handlers provide context