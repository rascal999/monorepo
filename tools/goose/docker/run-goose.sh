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

# Ensure workspace directory exists and get absolute path
WORKSPACE_DIR="$(cd "$(dirname "$0")/../workspace" 2>/dev/null && pwd -P)"
if [ ! -d "$WORKSPACE_DIR" ]; then
    mkdir -p "$WORKSPACE_DIR"
fi

# Ensure memory directory exists and get absolute path
MEMORY_DIR="$(cd "$(dirname "$0")/memory" 2>/dev/null && pwd -P)"
if [ ! -d "$MEMORY_DIR" ]; then
    mkdir -p "$MEMORY_DIR"
fi

# Run bash which launches goose, keeping goose in command history
docker run --rm -it \
  -p 5173:5173 \
  -p 3000:3000 \
  $MCP_MOUNTS \
  -v "${WORKSPACE_DIR}:/workspace" \
  -v "${MEMORY_DIR}:/root/.config/goose/memory" \
  -e GOOSE_PROVIDER="${GOOSE_PROVIDER:-openrouter}" \
  -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-}" \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
  -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
  -e DATABRICKS_HOST="${DATABRICKS_HOST:-}" \
  -e JIRA_URL="${JIRA_URL}" \
  -e JIRA_USERNAME="${JIRA_USERNAME}" \
  -e JIRA_API_TOKEN="${JIRA_API_TOKEN}" \
  -e GITLAB_PERSONAL_ACCESS_TOKEN="${GITLAB_PERSONAL_ACCESS_TOKEN}" \
  -e GITLAB_API_URL="${GITLAB_API_URL}" \
  -e SLACK_BOT_TOKEN="${SLACK_BOT_TOKEN}" \
  -e SLACK_TEAM_ID="${SLACK_TEAM_ID}" \
  --entrypoint bash \
  goose -c 'cmd="goose $*"; echo "$cmd" >> ~/.bash_history; HISTFILE=~/.bash_history; history -r; eval "$cmd"; exec bash --init-file <(echo "history -r")' _ "$@"
