from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import json
import logging
import sys
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_get_dms(session: ClientSession):
    """Test getting DMs with a user."""
    print("\nTesting DM access:")
    print("----------------------------------------")

    # Get DMs by email (preferred method)
    print("\n1. Getting DMs by email:")
    result = await session.call_tool(
        "slack_get_user",
        {"email": "jeremy.antkowiak@mangopay.com"}
    )
    print(result.content[0].text)

    # Get DMs by name (alternative method)
    print("\n2. Getting DMs by name:")
    result = await session.call_tool(
        "slack_get_user",
        {"name": "Jeremy Antkowiak"}
    )
    print(result.content[0].text)

async def test_get_channel_messages(session: ClientSession):
    """Test getting channel messages."""
    print("\nTesting channel access:")
    print("----------------------------------------")

    # Get messages by channel name
    print("\n1. Getting messages by channel name:")
    result = await session.call_tool(
        "slack_get_channel",
        {"name": "general-mangopay"}
    )
    print(result.content[0].text)

    # Get messages by channel ID
    print("\n2. Getting messages by channel ID:")
    result = await session.call_tool(
        "slack_get_channel",
        {"id": "C1234567890"}  # Replace with actual channel ID
    )
    print(result.content[0].text)

async def main():
    try:
        # Load environment variables from .env file if it exists
        load_dotenv()
        logger.debug("Environment variables loaded")

        # Use the current Python interpreter
        python_path = sys.executable
        logger.debug(f"Using Python at: {python_path}")

        # Configure server parameters
        server_params = StdioServerParameters(
            command=python_path,
            args=["-m", "mcp_slack_user"],
            env={
                "SLACK_USER_TOKEN": os.getenv("SLACK_USER_TOKEN"),
            }
        )

        # Connect to the server and test Slack access
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                logger.debug("Session initialized")

                # Run tests
                await test_get_dms(session)
                await test_get_channel_messages(session)

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())