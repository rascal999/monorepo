#!/usr/bin/env bash

# Load environment variables from .env file
if [ -f "$(dirname "$0")/../.env" ]; then
    set -a
    source "$(dirname "$0")/../.env"
    set +a
fi

# Build mount arguments for MCP server .env files
MCP_MOUNTS=""
if [ -d "mcp" ]; then
    for server in mcp/*; do
        if [ -d "$server" ] && [ -f "$server/.env" ]; then
            server_name=$(basename "$server")
            MCP_MOUNTS="$MCP_MOUNTS -v $(pwd)/$server/.env:/opt/mcp-servers/$server_name/.env:ro"
        fi
    done
fi

# Run bash which launches goose, keeping goose in command history
docker run --rm -it \
  -p 5173:5173 \
  $MCP_MOUNTS \
  -e GOOSE_PROVIDER="${GOOSE_PROVIDER:-openrouter}" \
  -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-}" \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
  -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
  -e DATABRICKS_HOST="${DATABRICKS_HOST:-}" \
  -e JIRA_URL="${JIRA_URL:-https://mangopay.atlassian.net}" \
  -e JIRA_USERNAME="${JIRA_USERNAME}" \
  -e JIRA_API_TOKEN="${JIRA_API_TOKEN}" \
  --entrypoint bash \
  goose -c 'cmd="goose $*"; echo "$cmd" >> ~/.bash_history; HISTFILE=~/.bash_history; history -r; eval "$cmd"; exec bash --init-file <(echo "history -r")' _ "$@"