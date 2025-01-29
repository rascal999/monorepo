# Goose CLI

A powerful CLI tool for AI-assisted development and system operations.

## Quick Start

1. Build the Docker container:
```bash
docker build -t goose -f docker/Dockerfile.prebuilt .
```

2. Start a Goose session:
```bash
docker/run-goose.sh session
```

## Features

- Multiple AI provider support (OpenRouter, Anthropic, OpenAI)
- Configuration persistence between sessions
- Extension system for enhanced functionality
- Built-in package management with UV tool

## Configuration

The tool stores configuration in `~/.config/goose`. This directory is automatically created and mounted when using the provided run script.

### Environment Variables

Configure your AI provider:
```bash
# OpenRouter (default)
OPENROUTER_API_KEY=your_key ./docker/run-goose.sh session

# Other providers
GOOSE_PROVIDER=anthropic ANTHROPIC_API_KEY=your_key ./docker/run-goose.sh session
GOOSE_PROVIDER=openai OPENAI_API_KEY=your_key ./docker/run-goose.sh session
```

### Jira Integration

Configure Jira access:
```bash
JIRA_URL=https://your-instance.atlassian.net \
JIRA_USERNAME=your_username \
JIRA_API_TOKEN=your_token \
./docker/run-goose.sh session
```

## Extensions

Run Goose with extensions:
```bash
./docker/run-goose.sh session --with-extension "uvx mcp-server-fetch"
```

## Documentation

For detailed information about:
- Docker configuration options
- Available extensions
- Troubleshooting
- System requirements

See [Docker Setup Documentation](docker/README.md)

## Note

This package contains the CLI component. For the full Goose experience including the GUI, please follow the local development setup instructions.