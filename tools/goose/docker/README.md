# Docker Setup for Goose CLI

This directory contains Docker configurations for building and running the [Goose](https://github.com/block/goose) CLI component.

## Dockerfile Options

### 1. Building from Source (Dockerfile)

Uses a multi-stage build to compile Goose from source:

```bash
docker build -t goose .
```

- Base: debian:bookworm-slim
- Builds latest version from source
- Optimized for current system
- Uses modern SSL libraries

### 2. Using Pre-built Binary (Dockerfile.prebuilt)

Uses the official pre-built binary:

```bash
docker build -t goose -f docker/Dockerfile.prebuilt .
```

- Base: ubuntu:20.04 (for libssl1.1 compatibility)
- Downloads official stable release
- Includes uv tool for package management
- Faster build time

## Running Goose

### Using the Run Script (Recommended)

We provide a run script that handles configuration persistence:

```bash
# Make the script executable
chmod +x docker/run-goose.sh

# Basic usage
./docker/run-goose.sh --help
./docker/run-goose.sh configure
./docker/run-goose.sh session

# Using with extensions
./docker/run-goose.sh session --with-extension "uvx mcp-server-fetch"
```

The script:
- Creates a configuration directory at `~/.config/goose`
- Mounts this directory into the container
- Passes through environment variables for AI providers
- Preserves your configuration between runs

### Manual Running

If you prefer to run the container directly:

```bash
# Create config directory
mkdir -p ~/.config/goose

# Run with config mounted
docker run --rm -it \
  -v ~/.config/goose:/root/.config/goose \
  goose [command]

# Run with extensions
docker run --rm -it \
  -v ~/.config/goose:/root/.config/goose \
  goose session --with-extension "uvx mcp-server-fetch"
```

## Extensions and Tools

### UV Tool and UVX

The container includes the [uv](https://github.com/astral-sh/uv) tool, a fast Python package installer. The `uvx` extension is an alias that provides convenient access to uv:

```bash
# Use uvx with mcp-server-fetch
./docker/run-goose.sh session --with-extension "uvx mcp-server-fetch"
```

### MCP Server Fetch

The `mcp-server-fetch` extension allows interaction with MCP servers. It's typically used in combination with uvx:

```bash
# Start a session with both extensions
./docker/run-goose.sh session --with-extension "uvx mcp-server-fetch"
```

## Default Configuration

Both Dockerfile variants come with these defaults:
- `GOOSE_PROVIDER=openrouter`: Set to use OpenRouter as the AI provider
- `RUST_BACKTRACE=1`: Enable detailed error reporting

## Environment Variables

You can configure Goose using environment variables:

```bash
# Using the run script with OpenRouter
OPENROUTER_API_KEY=your_key ./docker/run-goose.sh session

# Other providers
GOOSE_PROVIDER=anthropic ANTHROPIC_API_KEY=your_key ./docker/run-goose.sh session
GOOSE_PROVIDER=openai OPENAI_API_KEY=your_key ./docker/run-goose.sh session
```

## System Requirements

Both containers include necessary system libraries:
- SSL libraries (version differs by container)
- XCB libraries for system integration
- D-Bus for system communication
- CA certificates for HTTPS support
- UV tool for Python package management

## Configuration Persistence

The run script mounts `~/.config/goose` into the container, ensuring that:
- Your configuration persists between container runs
- API keys and provider settings are preserved
- Any other goose configuration files are maintained

## Troubleshooting

### Error Messages

The container enables RUST_BACKTRACE=1 by default for detailed error messages. If you encounter issues:
1. Check the error message for specific details about what went wrong
2. Verify your provider configuration is correct
3. Ensure any required API keys are properly set

### API Key Issues

If you get authentication errors:
1. Verify you've set the correct API key for your chosen provider
2. Check that the API key is being passed correctly to the container
3. Try running `goose configure` to set up your credentials

### Extension Issues

If you encounter problems with extensions:
1. Verify the extension names are correct
2. For uvx issues, check that uv tool is working: `docker run --rm -it goose uv --version`
3. Look for specific extension-related error messages in the output

## Note

This Docker setup only includes the CLI component. For the full Goose experience including the GUI, please follow the local development setup in the main README.md.