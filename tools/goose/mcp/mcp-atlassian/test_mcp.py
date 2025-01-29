from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import json
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def main():
    try:
        # Load environment variables from .env file if it exists
        load_dotenv()
        logger.debug("Environment variables loaded")

        # Use the correct path in the container
        mcp_atlassian_path = "/opt/mcp-servers/.venv/bin/python"
        logger.debug(f"Using Python at: {mcp_atlassian_path}")

        # Configure server parameters
        server_params = StdioServerParameters(
            command=mcp_atlassian_path,
            args=["-m", "mcp_atlassian"],
            env={
                "JIRA_URL": os.getenv("JIRA_URL"),
                "JIRA_USERNAME": os.getenv("JIRA_USERNAME"),
                "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN")
            }
        )

        # Connect to the server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize connection
                await session.initialize()
                logger.debug("Session initialized")

                # Get specific Jira issue
                print("\nGetting Jira issue SRE-802:")
                result = await session.call_tool(
                    "jira_get_issue",
                    arguments={
                        "issue_key": "SRE-802",
                        "expand": "description,comments"
                    }
                )
                
                # Print the results
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())