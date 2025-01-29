#!/bin/bash

# Activate virtual environment
source /opt/mcp-servers/.venv/bin/activate

# Add virtual environment to PATH
export PATH="/opt/mcp-servers/.venv/bin:$PATH"

# Wait for MCP server to start
sleep 2

# Execute the passed command (which will be bash with goose)
exec "$@"