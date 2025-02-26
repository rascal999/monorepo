import logging
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .config import SlackConfig

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("mcp-slack")

class SlackClient:
    """Base client for Slack operations."""

    def __init__(self):
        token = os.getenv("SLACK_USER_TOKEN")
        default_channel = os.getenv("SLACK_DEFAULT_CHANNEL")
        workspace_id = os.getenv("SLACK_WORKSPACE_ID")

        if not token:
            raise ValueError("Missing required SLACK_USER_TOKEN environment variable")

        self.config = SlackConfig(
            token=token,
            default_channel=default_channel,
            workspace_id=workspace_id
        )
        
        self.client = WebClient(token=self.config.token)
        
        # Test connection
        try:
            self.client.auth_test()
            logger.info("Successfully connected to Slack")
        except SlackApiError as e:
            logger.error(f"Failed to connect to Slack: {str(e)}")
            raise

    def _handle_response(self, response: dict) -> dict:
        """Process Slack API response and handle errors."""
        if not response["ok"]:
            error_msg = response.get("error", "Unknown error")
            logger.error(f"Slack API error: {error_msg}")
            raise SlackApiError(f"API call failed: {error_msg}", response)
        return response