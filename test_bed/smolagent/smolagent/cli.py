#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from smolagents import CodeAgent, LiteLLMModel
from .tools import (
    get_weather,
    gitlab_search,
    get_gitlab_file,
    list_gitlab_branches,
    get_gitlab_commits,
    jira_search,
    get_jira_ticket,
    web_search,
    visit_webpage,
    slack_search,
    list_slack_channels,
    get_slack_channel_history,
)

# Load environment variables
load_dotenv()

# Initialize the model using OpenRouter if configured, otherwise fallback to Ollama
if os.getenv("OPENROUTER_API_KEY"):
    model = LiteLLMModel(
        model_id=os.getenv("OPENROUTER_MODEL", "deepseek-ai/deepseek-coder-33b-instruct"),
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
else:
    model = LiteLLMModel(
        model_id=f"ollama/{os.getenv('OLLAMA_MODEL', 'qwen2.5-7b-128k-instruct')}",
        api_base=os.getenv("OLLAMA_BASE_URL", "http://192.168.0.100:11434")
    )

# Create agent with all available tools
agent = CodeAgent(
    tools=[
        get_weather,
        gitlab_search,
        get_gitlab_file,
        list_gitlab_branches,
        get_gitlab_commits,
        jira_search,
        get_jira_ticket,
        web_search,
        visit_webpage,
        slack_search,
        list_slack_channels,
        get_slack_channel_history,
    ],
    model=model,
)

def get_help_text():
    return """
Available tools:
- Weather information
  * 'get weather in London'
  * 'what's the weather in Paris'

- GitLab:
  * Search: 'search GitLab for security'
  * Get file: 'show file README.md from mygroup/myproject'
  * List branches: 'list branches in mygroup/myproject'
  * Recent commits: 'show commits in mygroup/myproject'

- Jira tickets:
  * Get ticket: 'show ticket PROJ-123'
  * Search tickets:
    - By project: 'find tickets in SECOPS'
    - By status: 'show open tickets in SECOPS'
    - By priority: 'find high priority SECOPS tickets'
    - By date: 'find SECOPS tickets created today'
    - Specific date: 'project = SECOPS AND created >= "2025-02-04" AND created < "2025-02-05"'

- Web search
  * 'search web for latest tech news'
  * 'get content from https://example.com'

- Slack (read-only):
  * Search messages: 'search Slack for deployment in #engineering'
  * List channels: 'show Slack channels'
  * View history: 'show recent messages in #general'

Commands:
- help: Show this help message
- quit/exit: Exit the application
- clear: Clear the screen

Shell features:
- Up/Down arrows: Navigate command history
- Tab: Auto-complete from history
- Ctrl+R: Search command history
- Ctrl+A/E: Move to start/end of line
- Ctrl+K: Clear line after cursor
- Ctrl+U: Clear line before cursor
- Ctrl+L: Clear screen
"""

def main():
    # Create history file in user's home directory
    history_file = os.path.expanduser('~/.smolagent_history')
    
    # Initialize prompt session with history and auto-suggest
    session = PromptSession(
        history=FileHistory(history_file),
        auto_suggest=AutoSuggestFromHistory(),
        enable_history_search=True,
    )
    
    print("Welcome to the Multi-Tool Agent!")
    print("Type 'help' for available commands and features")
    print("Type 'quit' to exit")
    
    while True:
        try:
            # Get input with prompt toolkit
            query = session.prompt("\nWhat would you like to do? => ")
            
            # Handle special commands
            query = query.strip()
            if query.lower() in ['quit', 'exit']:
                break
            elif query.lower() == 'help':
                print(get_help_text())
                continue
            elif query.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                continue
            elif not query:
                continue
                
            result = agent.run(query)
            print("\nResult:", result)
            
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
    
    print("\nThank you for using the Multi-Tool Agent!")

if __name__ == "__main__":
    main()
