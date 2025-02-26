import argparse
import asyncio
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.stdio import stdio_server
from .server import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-slack")

def parse_args():
    parser = argparse.ArgumentParser(description='MCP Slack User Server')
    parser.add_argument('-e', '--env', help='Path to .env file')
    args = parser.parse_args()
    logger.info(f"Command line args: {args}")
    return args

async def main():
    args = parse_args()
    
    # Load environment variables
    if args.env:
        env_path = Path(args.env)
        logger.info(f"Loading .env from: {env_path.absolute()}")
        if not env_path.exists():
            raise ValueError(f"Environment file not found: {env_path}")
        load_dotenv(env_path)
    else:
        logger.info("No .env path specified, trying default locations")
        load_dotenv()

    # Log loaded environment
    token = os.getenv("SLACK_USER_TOKEN")
    if token:
        logger.info("SLACK_USER_TOKEN loaded successfully")
        logger.debug(f"Token starts with: {token[:10]}...")
    else:
        raise ValueError("SLACK_USER_TOKEN environment variable is required")

    # Run server
    logger.info("Starting MCP Slack server...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        raise