# MCP Slack User Tokens Server

An MCP server implementation for interacting with Slack using user tokens. This server provides access to Slack workspace resources and operations through the MCP protocol.

## Features

- Channel operations (list, create, archive, rename)
- Message operations (send, read, update, delete)
- User operations (list, info, presence)
- File operations (upload, list, delete)
- Resource listing for channels and users
- Text preprocessing for Slack markdown

## Installation

```bash
# Install using pip
pip install .
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example` with your Slack credentials:

```env
SLACK_USER_TOKEN=xoxp-your-token-here
SLACK_DEFAULT_CHANNEL=general-mangopay
```

### Required Slack Scopes

Your Slack user token must have these scopes:
- `identify` - Verify identity
- `channels:history` - View messages in public channels
- `groups:history` - View messages in private channels
- `im:history` - View direct messages
- `channels:read` - View public channels
- `groups:read` - View private channels
- `im:read` - View direct messages
- `search:read` - Search messages
- `users:read` - View basic user info
- `users:read.email` - View user email addresses

## Usage

### As an MCP Server

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "mcp-slack-user": {
      "command": "uvx",
      "args": ["mcp-slack-user"],
      "env": {
        "SLACK_USER_TOKEN": "xoxp-your-token-here"
      }
    }
  }
}
```

### Available Tools

1. `slack_send_message`: Send messages to channels
2. `slack_create_channel`: Create new channels
3. `slack_upload_file`: Upload files to channels
4. `slack_search_messages`: Search messages in channels

### Available Resources

- Channels: `slack://channel/{channel_id}`
- Users: `slack://user/{user_id}` or `slack://user/{email}`

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
python test_mcp.py
```

## Testing Channel Pagination

The `test_pagination.sh` script helps determine optimal pagination settings to avoid rate limiting:

```bash
# Make script executable
chmod +x test_pagination.sh

# Run pagination tests
./test_pagination.sh
```

The script tests different combinations of:
- Page sizes (200, 100, 50 channels per request)
- Delays between requests (1, 2, 3 seconds)

For each combination, it reports:
- Total channels found
- Number of pages needed
- Total time taken
- Any rate limiting encountered

Use these results to tune the pagination settings in `channels.py`:
```python
# Example settings based on test results
CHANNELS_PER_PAGE = 50  # Conservative page size
DELAY_BETWEEN_PAGES = 2  # 2 second delay
```

## License

MIT License