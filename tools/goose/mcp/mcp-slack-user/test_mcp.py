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

                # Read DMs from Jeremy Antkowiak by email
                print("\nReading DMs from jeremy.antkowiak@mangopay.com:")
                result = await session.read_resource("slack://user/jeremy.antkowiak@mangopay.com")
                for content in result.contents:
                    print(content.text)

                # Then read latest message from #general-mangopay
                print("\nReading latest message from #general-mangopay:")
                result = await session.read_resource("slack://channel/general-mangopay")
                for content in result.contents:
                    print(content.text)

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())