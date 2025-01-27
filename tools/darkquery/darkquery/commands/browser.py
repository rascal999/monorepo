"""Browser interaction functionality."""
import webbrowser

from ..display import display_error, display_warning, console


class BrowserMixin:
    """Mixin for browser operations."""

    def handle_open(self) -> None:
        """Handle the open command."""
        if not self.last_viewed:
            display_warning("No item has been viewed yet")
            return
            
        # Parse last viewed item
        if self.last_viewed.startswith("gitlab:"):
            if not self.gitlab_url:
                display_error("GitLab URL not configured")
                return
                
            # Parse item type and ID
            _, item_type, item_id = self.last_viewed.split(":")
            
            # Construct GitLab URL
            if item_type == "merge_request":
                item_url = f"{self.gitlab_url.rstrip('/')}/-/merge_requests/{item_id}"
            else:  # issue
                item_url = f"{self.gitlab_url.rstrip('/')}/-/issues/{item_id}"
                
            try:
                webbrowser.open(item_url)
                console.print(f"Opening GitLab {item_type} {item_id} in browser...")
            except Exception as e:
                display_error(f"Failed to open browser: {str(e)}")
                
        else:  # JIRA ticket
            if not self.jira_url:
                display_error("JIRA URL not configured")
                return
                
            # Construct ticket URL
            ticket_url = f"{self.jira_url.rstrip('/')}/browse/{self.last_viewed}"
            
            try:
                # Open URL in default browser
                webbrowser.open(ticket_url)
                console.print(f"Opening {self.last_viewed} in browser...")
            except Exception as e:
                display_error(f"Failed to open browser: {str(e)}")