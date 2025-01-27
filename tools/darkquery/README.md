# darkquery

A natural language interface for querying tickets and analyzing code, powered by Ollama.

## Prerequisites

1. Python 3.8 or higher
2. Ollama installed and running locally
   ```bash
   # Install Ollama from https://ollama.ai
   # Pull the required model (default: deepseek-r1-14b-32k:latest)
   ollama pull deepseek-r1-14b-32k:latest
   ```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd darkquery
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

## Configuration

1. Create a `.env` file in the project root (same directory as pyproject.toml):
   ```env
   # Required for JIRA integration
   JIRA_URL=https://your-instance.atlassian.net
   JIRA_EMAIL=your_email@company.com
   JIRA_TOKEN=your_api_token

   # Required for GitLab integration
   GITLAB_URL=https://gitlab.com
   GITLAB_TOKEN=your_personal_access_token

   # Ollama settings (optional)
   OLLAMA_URL=http://localhost:11434
   OLLAMA_MODEL=deepseek-r1-14b-32k:latest
   ```

2. Ensure Ollama is running:
   ```bash
   # In a separate terminal
   ollama serve
   ```

## Running

Start the interactive shell using either command:
```bash
# Short alias
dq

# Full command
darkquery

# With verbose logging (shows model being used)
dq -v
```

Then start querying:
```
> Show my recent tickets
> Show tickets I created this week
> Read src/auth.js
> Show me the README
```

## Example Queries

### Ticket Queries
```
> Show my recent tickets
> Show tickets I created this week
> Show all open bugs
> Show critical bugs in progress
> Show tickets assigned to Bob
> Show unassigned tickets in current sprint
```

### Working with Tickets
```
> Show me BUG-101
> What's the impact of this bug?
> Who's working on it?
> Show comments for BUG-101
```

### File Operations
```
> Read src/auth.js
> Show me the implementation of login function
> Find all API endpoints in this project
> Show me the README
```

## Architecture

darkquery is a lightweight wrapper that:
1. Takes natural language queries from users
2. Sends them to Ollama for processing
3. Executes any commands returned by the model
4. Shows results or responses to the user

## Development

### Project Structure

```
darkquery/
├── darkquery/           # Main package
│   ├── __init__.py
│   ├── cli.py          # CLI entry point
│   ├── shell.py        # Interactive shell
│   └── datasources/    # Data source implementations
│       ├── base.py
│       ├── jira.py
│       └── files.py
├── docs/               # Documentation
├── prompts/           # Ollama prompts
├── tests/            # Test suite
├── .env              # Configuration file
├── pyproject.toml    # Project metadata
└── README.md
```

## Dependencies

- click: CLI interface
- prompt-toolkit: Interactive shell
- rich: Terminal formatting
- python-dotenv: Environment configuration
- requests: HTTP client for Ollama
- jira: JIRA API client
- pygments: Syntax highlighting

## License

[Add your license information here]