"""Main entry point for the package."""
import asyncio

from . import server

if __name__ == "__main__":
    asyncio.run(server.main())