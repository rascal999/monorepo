"""MCP server for Slack user token operations."""

import logging
from .server import main
from .client import SlackClient
from .messages import SlackMessages
from .channels import SlackChannels
from .users import SlackUsers
from .files import SlackFiles
from .config import SlackConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-slack")

__all__ = [
    "main",
    "SlackClient",
    "SlackMessages",
    "SlackChannels",
    "SlackUsers",
    "SlackFiles",
    "SlackConfig",
]