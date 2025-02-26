import json
import logging
import urllib.parse
from typing import Any, List, Sequence
from difflib import get_close_matches
from mcp.server import Server
from mcp.types import Resource, TextContent, Tool
from pydantic import AnyUrl

from .messages import SlackMessages
from .channels import SlackChannels
from .users import SlackUsers
from .files import SlackFiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-slack")

# Create server instance
app = Server("mcp-slack-user")

class SlackHandlers:
    """Singleton to hold Slack handlers."""
    _instance = None
    messages: SlackMessages = None
    channels: SlackChannels = None
    users: SlackUsers = None
    files: SlackFiles = None

    @classmethod
    def initialize(cls):
        """Initialize Slack handlers if not already initialized."""
        if cls._instance is None:
            try:
                cls.messages = SlackMessages()
                cls.channels = SlackChannels()
                cls.users = SlackUsers()
                cls.files = SlackFiles()
                cls._instance = cls
                logger.info("Slack handlers initialized successfully")
            except ValueError as e:
                logger.error(f"Slack initialization failed: {str(e)}")
                raise
        return cls._instance

    @classmethod
    def get_instance(cls):
        """Get the singleton instance, initializing if needed."""
        if cls._instance is None:
            cls.initialize()
        return cls._instance

def _get_user_id(name: str) -> str:
    """Get user ID from name or email."""
    handlers = SlackHandlers.get_instance()
    
    # URL decode the name
    name = urllib.parse.unquote(name)
    logger.info(f"Looking up user: {name}")
    
    # If it's an email, try direct lookup
    if '@' in name:
        try:
            user = handlers.users.get_user_by_email(name)
            logger.info(f"Found user by email: {user.get('real_name', '')}")
            return user['id']
        except Exception as e:
            logger.error(f"Error looking up by email: {str(e)}")
            # Fall through to name-based lookup
    
    # Try name-based lookup
    users = handlers.users.list_users()
    # Create list of names (both real names and usernames)
    names = [(user['id'], user.get('real_name', ''), user.get('name', '')) for user in users]
    
    # Try exact match first
    for user_id, real_name, username in names:
        if name in (real_name, username):
            logger.info(f"Found exact match: {real_name} (@{username})")
            return user_id
    
    # Try fuzzy match on real names
    real_names = [real_name for _, real_name, _ in names if real_name]
    matches = get_close_matches(name, real_names, n=1, cutoff=0.6)
    if matches:
        matched_name = matches[0]
        logger.info(f"Found fuzzy match on real name: {matched_name}")
        for user_id, real_name, _ in names:
            if real_name == matched_name:
                return user_id
    
    # Try fuzzy match on usernames
    usernames = [username for _, _, username in names if username]
    matches = get_close_matches(name, usernames, n=1, cutoff=0.6)
    if matches:
        matched_name = matches[0]
        logger.info(f"Found fuzzy match on username: {matched_name}")
        for user_id, _, username in names:
            if username == matched_name:
                return user_id
    
    raise ValueError(f"User not found: {name}")

def _get_channel_id(channel_name_or_id: str) -> str:
    """Get channel ID from name or return the ID if already an ID."""
    handlers = SlackHandlers.get_instance()
    
    if channel_name_or_id.startswith('C'):  # It's already an ID
        return channel_name_or_id
    
    # URL decode the name
    channel_name_or_id = urllib.parse.unquote(channel_name_or_id)
    
    # Try to get channel directly
    try:
        channel = handlers.channels.get_channel_by_name(channel_name_or_id)
        return channel['id']
    except ValueError as e:
        logger.error(f"Error getting channel: {str(e)}")
        raise

@app.list_resources()
async def list_resources() -> List[Resource]:
    """List available Slack channels and users as resources."""
    handlers = SlackHandlers.get_instance()
    resources = []

    # Add channels
    try:
        channels = handlers.channels.list_channels()
        resources.extend([
            Resource(
                uri=AnyUrl(f"slack://channel/{channel['id']}"),
                name=f"Channel: {channel['name']}",
                mimeType="text/plain",
                description=channel.get("topic", {}).get("value", ""),
            )
            for channel in channels
        ])
    except Exception as e:
        logger.error(f"Error fetching channels: {str(e)}")

    # Add users
    try:
        users = handlers.users.list_users()
        resources.extend([
            Resource(
                uri=AnyUrl(f"slack://user/{user['id']}"),
                name=f"User: {user['real_name'] or user['name']}",
                mimeType="text/plain",
                description=user.get("profile", {}).get("status_text", ""),
            )
            for user in users
            if not user.get("is_bot", False) and not user.get("deleted", False)
        ])
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")

    return resources

@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read content from Slack."""
    handlers = SlackHandlers.get_instance()
    uri_str = str(uri)

    if uri_str.startswith("slack://channel/"):
        channel_name_or_id = uri_str.replace("slack://channel/", "")
        try:
            channel_id = _get_channel_id(channel_name_or_id)
            messages = handlers.messages.get_channel_messages(channel_id, limit=10)
            content = []
            for msg in messages:
                content.append(f"# {msg.get('user', 'Unknown')}: {msg.get('ts')}\n\n{msg.get('text', '')}\n---")
            return "\n\n".join(content)
        except ValueError as e:
            logger.error(f"Error reading channel: {str(e)}")
            raise

    elif uri_str.startswith("slack://user/"):
        user_name_or_id = uri_str.replace("slack://user/", "")
        try:
            # If it's a name or email, get the ID
            if not user_name_or_id.startswith('U'):
                user_name_or_id = _get_user_id(user_name_or_id)
            
            # Get DMs with user
            messages = handlers.messages.get_dm_messages(user_name_or_id, limit=10)
            content = []
            for msg in messages:
                content.append(f"# {msg.get('user', 'Unknown')}: {msg.get('ts')}\n\n{msg.get('text', '')}\n---")
            return "\n\n".join(content)
        except ValueError as e:
            logger.error(f"Error reading DMs: {str(e)}")
            raise

    raise ValueError(f"Invalid resource URI: {uri}")

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available Slack tools."""
    return [
        Tool(
            name="slack_get_user",
            description=(
                "Get direct messages (DMs) with a user in one step. No separate user lookup needed.\n\n"
                "Just provide either:\n"
                "1. User's email (preferred, most reliable)\n"
                "2. User's display name (supports fuzzy matching)\n\n"
                "Returns the last 10 DMs exchanged with the user, including messages sent and received.\n\n"
                "Example usage:\n"
                '- Get DMs by email: slack_get_user(email="jeremy.antkowiak@mangopay.com")\n'
                '- Get DMs by name: slack_get_user(name="Jeremy Antkowiak")'
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "User's email address (e.g., 'jeremy.antkowiak@mangopay.com')"},
                    "name": {"type": "string", "description": "User's display name (e.g., 'Jeremy Antkowiak')"},
                },
                "anyOf": [{"required": ["email"]}, {"required": ["name"]}],
                "examples": [
                    {"email": "jeremy.antkowiak@mangopay.com"},
                    {"name": "Jeremy Antkowiak"}
                ]
            },
        ),
        Tool(
            name="slack_get_channel",
            description=(
                "Get channel messages in one step. No separate channel lookup needed.\n\n"
                "Just provide either:\n"
                "1. Channel name (with or without #)\n"
                "2. Channel ID if known\n\n"
                "Returns the last 10 messages from the channel.\n\n"
                "Example usage:\n"
                '- Get by name: slack_get_channel(name="general-mangopay")\n'
                '- Get by ID: slack_get_channel(id="C1234567890")'
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Channel name with or without # (e.g., 'general-mangopay' or '#general-mangopay')"},
                    "id": {"type": "string", "description": "Channel ID if known"},
                },
                "anyOf": [{"required": ["name"]}, {"required": ["id"]}],
                "examples": [
                    {"name": "general-mangopay"},
                    {"id": "C1234567890"}
                ]
            },
        ),
        Tool(
            name="slack_send_message",
            description="Send a message to a Slack channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "Channel ID or name"},
                    "text": {"type": "string", "description": "Message text"},
                    "thread_ts": {"type": "string", "description": "Thread timestamp to reply to", "default": None},
                },
                "required": ["channel", "text"],
            },
        ),
        Tool(
            name="slack_create_channel",
            description="Create a new Slack channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Channel name"},
                    "is_private": {"type": "boolean", "description": "Whether the channel is private", "default": False},
                    "user_ids": {"type": "array", "items": {"type": "string"}, "description": "Users to invite", "default": None},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="slack_upload_file",
            description="Upload a file to Slack",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of the file"},
                    "content": {"type": "string", "description": "File content"},
                    "channels": {"type": "array", "items": {"type": "string"}, "description": "Channels to share in"},
                    "initial_comment": {"type": "string", "description": "Comment to add", "default": None},
                },
                "required": ["filename", "content"],
            },
        ),
        Tool(
            name="slack_search_messages",
            description="Search messages in channels",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "channel": {"type": "string", "description": "Channel to search in", "default": None},
                    "limit": {"type": "number", "description": "Max results to return", "default": 10},
                },
                "required": ["query"],
            },
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls for Slack operations."""
    handlers = SlackHandlers.get_instance()
    
    try:
        if name == "slack_get_user":
            # Get user ID from email or name
            if "email" in arguments:
                user_id = _get_user_id(arguments["email"])
            else:
                user_id = _get_user_id(arguments["name"])
            
            # Use read_resource to get DMs
            uri = AnyUrl(f"slack://user/{user_id}")
            content = await read_resource(uri)
            return [TextContent(type="text", text=content)]

        elif name == "slack_get_channel":
            # Get channel ID from name or use provided ID
            channel_id = arguments.get("id") or _get_channel_id(arguments["name"])
            
            # Use read_resource to get messages
            uri = AnyUrl(f"slack://channel/{channel_id}")
            content = await read_resource(uri)
            return [TextContent(type="text", text=content)]

        elif name == "slack_send_message":
            channel = _get_channel_id(arguments["channel"])
            response = handlers.messages.send_message(
                channel=channel,
                text=arguments["text"],
                thread_ts=arguments.get("thread_ts")
            )
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        elif name == "slack_create_channel":
            response = handlers.channels.create_channel(
                name=arguments["name"],
                is_private=arguments.get("is_private", False),
                user_ids=arguments.get("user_ids")
            )
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        elif name == "slack_upload_file":
            from io import BytesIO
            file_content = arguments["content"].encode()
            file_obj = BytesIO(file_content)
            channels = [_get_channel_id(c) for c in arguments.get("channels", [])] if arguments.get("channels") else None
            response = handlers.files.upload_file(
                file=file_obj,
                filename=arguments["filename"],
                channels=channels,
                initial_comment=arguments.get("initial_comment")
            )
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        elif name == "slack_search_messages":
            channel = _get_channel_id(arguments["channel"]) if arguments.get("channel") else None
            messages = handlers.messages.search_messages(
                query=arguments["query"],
                channel=channel,
                limit=arguments.get("limit", 10)
            )
            return [TextContent(type="text", text=json.dumps(messages, indent=2))]

        raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        raise RuntimeError(f"Tool execution failed: {str(e)}")

async def main():
    """Initialize Slack handlers and run server."""
    # Initialize handlers
    SlackHandlers.initialize()

    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())