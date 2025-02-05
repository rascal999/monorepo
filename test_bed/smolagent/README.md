# Multi-Tool Agent

A versatile agent that can handle various tasks using multiple tools, powered by smolagents and either Ollama or OpenRouter.

## Features

- Weather information lookup
- GitLab project and issue search
- Jira issue tracking and ticket management
- Web search and webpage content extraction
- Slack messaging and search

## Quick Start

1. Copy the environment file and configure your settings:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your actual credentials and settings.

2. Run the application:
   ```bash
   ./run.sh
   ```

   The script will:
   - Check for the presence of .env file
   - Build the Docker image
   - Run the container with proper environment variables
   - Handle errors and provide clear feedback

## Usage

The agent automatically selects the appropriate tool based on your request. Here are some example commands:

### Weather
- "What's the weather in London?"
- "Get weather forecast for New York"

### GitLab
- "Search GitLab for project X"
- "Find issues about feature Y"

### Jira
- "Get ticket SRE-802" (fetches detailed ticket information including description and recent comments)
- "Search Jira for open bugs"
- "Find Jira tickets assigned to me"
- "Search Jira tickets with high priority"
- Example JQL queries:
  - "project = SRE AND status = Open"
  - "assignee = currentUser() AND priority = High"

### Web Search
- "Search the web for latest tech news"
- "Get content from https://example.com"

### Slack
- "Send message 'Hello team' to #general"
- "Search Slack for messages about deployment"

Type 'quit' to exit the application.

## Environment Variables

See `.env.example` for a complete list of required environment variables:

- LLM Configuration (choose one):
  - Ollama:
    - `OLLAMA_BASE_URL`: URL of your Ollama instance
    - `OLLAMA_MODEL`: Name of the Ollama model to use
  - OpenRouter:
    - `OPENROUTER_API_KEY`: Your OpenRouter API key
    - `OPENROUTER_MODEL`: Model to use (e.g., "openai/gpt-3.5-turbo")

- Sensitive variables (provided at runtime):
  - `JIRA_URL`: Your Jira instance URL
  - `JIRA_USERNAME`: Your Jira email
  - `JIRA_TOKEN`: Your Jira API token
  - `GITLAB_URL`: GitLab instance URL
  - `GITLAB_TOKEN`: Your GitLab personal access token
  - `SLACK_BOT_TOKEN`: Your Slack bot token

## Security Notes

- Sensitive credentials are passed at runtime using Docker's --env-file option
- No sensitive data is built into the Docker image
- Environment variables are isolated to the container

## Manual Docker Commands

If you prefer to run Docker commands manually:

1. Build the image:
   ```bash
   docker build -t smolagent .
   ```

2. Run the container:
   ```bash
   docker run \
     --network host \
     --env-file .env \
     -it smolagent
   ```

## Requirements

- Docker
- Either:
  - Ollama running locally or accessible via network, or
  - OpenRouter API key
- Access to the required services (Jira, GitLab, Slack)