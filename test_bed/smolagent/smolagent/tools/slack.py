import os
from smolagents import tool
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def _get_slack_client() -> WebClient:
    """Get authenticated Slack client."""
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        raise ValueError(
            "SLACK_BOT_TOKEN environment variable is not set. "
            "Please set it to a valid Slack Bot User OAuth Token (starts with xoxb-) "
            "with the following scopes: channels:history, channels:read, users:read"
        )
    return WebClient(token=token)

@tool
def slack_search(query: str) -> str:
    """
    Search messages in Slack.
    NOTE: Search functionality is currently disabled as it requires additional permissions.
    Please use channel history to find messages instead.

    Args:
        query: The search query for Slack messages.
        Examples:
        - "deployment in #engineering" -> use get_slack_channel_history("engineering") instead
        - "from:@john security" -> use get_slack_channel_history() for specific channels
        - "in:#general after:2025-02-01" -> use get_slack_channel_history("general")

    Returns:
        A string containing search results.
    """
    return (
        "Search functionality is currently disabled as it requires Enterprise Grid permissions. "
        "Please use get_slack_channel_history() to view messages in specific channels instead.\n\n"
        "Example: Instead of searching 'test in #general', use:\n"
        "get_slack_channel_history('general')"
    )

@tool
def list_slack_channels() -> str:
    """
    List public Slack channels.

    Returns:
        A string containing a list of public channels.
    """
    try:
        client = _get_slack_client()
        
        response = client.conversations_list(
            types="public_channel",
            limit=10
        )
        
        channels = response['channels']
        if not channels:
            return "No public channels found."
            
        results = []
        for channel in channels:
            name = channel.get('name', 'Unknown')
            topic = channel.get('topic', {}).get('value', 'No topic')
            member_count = channel.get('num_members', 0)
            
            results.append(f"#{name}")
            results.append(f"Topic: {topic}")
            results.append(f"Members: {member_count}\n")
            
        return "Public Slack channels:\n\n" + "\n".join(results)
        
    except ValueError as e:
        return str(e)
    except SlackApiError as e:
        error = str(e.response['error'])
        if error == 'not_authed':
            return (
                "Slack authentication failed. Please check that SLACK_BOT_TOKEN is set to "
                "a valid Slack Bot User OAuth Token (starts with xoxb-)"
            )
        elif error == 'invalid_auth':
            return (
                "Invalid Slack authentication token. Please check that SLACK_BOT_TOKEN is "
                "correct and has the necessary permissions"
            )
        elif error == 'not_allowed_token_type':
            return (
                "Invalid token type. Please ensure SLACK_BOT_TOKEN is a Bot User OAuth Token "
                "(starts with xoxb-) with the following required scopes:\n"
                "- channels:read\n"
                "- channels:history\n"
                "- users:read"
            )
        return f"Error listing channels: {error}"
    except Exception as e:
        return f"Error listing channels: {str(e)}"

@tool
def get_slack_channel_history(channel: str) -> str:
    """
    Get recent messages from a Slack channel.

    Args:
        channel: The channel name (without #)
        Example: "general" for #general

    Returns:
        A string containing recent messages from the channel.
    """
    try:
        client = _get_slack_client()
        
        # First get the channel ID
        channel_id = None
        channels_response = client.conversations_list(types="public_channel")
        for ch in channels_response['channels']:
            if ch['name'] == channel:
                channel_id = ch['id']
                break
                
        if not channel_id:
            return f"Channel #{channel} not found."
        
        # Get channel history
        history_response = client.conversations_history(
            channel=channel_id,
            limit=5
        )
        
        messages = history_response['messages']
        if not messages:
            return f"No messages found in #{channel}."
            
        results = []
        for msg in messages:
            user = msg.get('user', 'Unknown')
            text = msg.get('text', 'No text')
            ts = msg.get('ts', 'Unknown time')
            
            # Get user info
            try:
                user_info = client.users_info(user=user)
                user_name = user_info['user']['real_name']
            except:
                user_name = user
            
            results.append(f"From: {user_name}")
            results.append(f"Time: {ts}")
            results.append(f"Message: {text}\n")
            
        return f"Recent messages in #{channel}:\n\n" + "\n".join(results)
        
    except ValueError as e:
        return str(e)
    except SlackApiError as e:
        error = str(e.response['error'])
        if error == 'not_authed':
            return (
                "Slack authentication failed. Please check that SLACK_BOT_TOKEN is set to "
                "a valid Slack Bot User OAuth Token (starts with xoxb-)"
            )
        elif error == 'invalid_auth':
            return (
                "Invalid Slack authentication token. Please check that SLACK_BOT_TOKEN is "
                "correct and has the necessary permissions"
            )
        elif error == 'not_allowed_token_type':
            return (
                "Invalid token type. Please ensure SLACK_BOT_TOKEN is a Bot User OAuth Token "
                "(starts with xoxb-) with the following required scopes:\n"
                "- channels:read\n"
                "- channels:history\n"
                "- users:read"
            )
        return f"Error getting channel history: {error}"
    except Exception as e:
        return f"Error getting channel history: {str(e)}"