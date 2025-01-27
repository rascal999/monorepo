# summAIry

A tool to fetch Jira tickets and their relationships, then generate an AI summary using Ollama.

## Requirements

- Python 3.8+
- Ollama running locally or remotely
- Jira API access (token + account email)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

You can configure the tool using either environment variables or command-line arguments.

### Using .env file (recommended)

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit .env with your credentials:
   ```
   JIRA_URL=https://your-instance.atlassian.net
   JIRA_EMAIL=your_email@company.com
   JIRA_TOKEN=your_api_token
   OLLAMA_URL=http://localhost:11434  # Optional, defaults to http://localhost:11434
   OLLAMA_MODEL=mistral              # Optional, defaults to mistral
   ```

### Using command-line arguments

All configuration can also be provided via command-line arguments:

```bash
./main.py TICKET-123 \
  --jira-url https://your-instance.atlassian.net \
  --jira-token your_api_token \
  --jira-email your_email@company.com \
  --ollama-url http://localhost:11434  # Optional
  --ollama-model mistral               # Optional
  --summary                            # Optional, for detailed summary
```

Command-line arguments take precedence over environment variables.

## Usage

Basic usage (key points only):
```bash
./main.py TICKET-123
```

Detailed summary:
```bash
./main.py TICKET-123 --summary
```

## Features

- Fetches main ticket and related tickets:
  - Parent epic
  - Child tickets/subtasks
  - Comments and discussions
- Two output formats:
  - Default: TL;DR and key bullet points
  - Detailed (--summary): Includes full analysis with context from comments
- Configurable:
  - Supports any Ollama model
  - Works with remote Ollama instances
  - Flexible authentication options

## Getting Started

1. Ensure Ollama is installed and running
2. Load your preferred model (e.g., mistral):
   ```bash
   ollama pull mistral
   ```
3. Get your Jira API token:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Create an API token
4. Configure your credentials (see Configuration section)
5. Make the script executable:
   ```bash
   chmod +x main.py
   ```
6. Run the script with your Jira ticket ID

## Error Handling

The tool provides clear error messages for common issues:
- Invalid ticket IDs
- Missing/inaccessible tickets
- Authentication failures
- Connection problems (Jira or Ollama)
- Missing configuration
- Model availability issues

If you encounter connection issues with Ollama:
1. Verify Ollama is running
2. Check the OLLAMA_URL is correct
3. Ensure the specified model is installed:
   ```bash
   ollama pull your_model_name