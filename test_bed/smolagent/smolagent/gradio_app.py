#!/usr/bin/env python3

import os
import gradio as gr
from dotenv import load_dotenv
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

# Initialize the model using Ollama
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
"""

def process_query(query: str, history: list) -> tuple[str, list]:
    """Process a query and update chat history."""
    if not query:
        return "", history
        
    if query.lower() == 'help':
        return "", history + [[query, get_help_text()]]
        
    try:
        result = agent.run(query)
        history.append([query, result])
        return "", history  # Empty the query box after submission
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        history.append([query, error_msg])
        return "", history  # Empty the query box even on error

def clear_history():
    """Clear the chat history."""
    return "", []  # Clear both query and history

def create_ui():
    """Create and configure the Gradio interface."""
    # Add custom CSS for better page fitting and fonts
    css = """
    .gradio-container {
        max-width: 100% !important;
        padding: 0 !important;
    }
    .main-div {
        gap: 0 !important;
    }
    .contain {
        padding: 0 !important;
    }
    * {
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    pre, code {
        font-family: "JetBrains Mono", "Fira Code", Consolas, Monaco, "Andale Mono", monospace !important;
    }
    """

    with gr.Blocks(title="Multi-Tool Agent", theme=gr.themes.Soft(), css=css) as app:
        with gr.Column(elem_classes="contain"):
            gr.Markdown("# Multi-Tool Agent")
            gr.Markdown("Type 'help' to see available commands and examples")
            gr.Markdown("Press Enter to submit, Ctrl/Cmd+Enter for new lines")
            
            chatbot = gr.Chatbot(
                label="Chat History",
                height="65vh",  # Make chat take up most of viewport height
                show_copy_button=True,
                container=True,
            )
            
            with gr.Row():
                with gr.Column(scale=8):
                    query = gr.Textbox(
                        label="Your Query",
                        placeholder="Type your query here... (Enter to submit, Ctrl/Cmd+Enter for new line)",
                        lines=2,
                        show_copy_button=True,
                        container=True,
                    )
                with gr.Column(scale=1):
                    submit = gr.Button("Submit", variant="primary")
                    clear = gr.Button("Clear History")
                    
            # Event handlers
            submit.click(
                process_query,
                inputs=[query, chatbot],
                outputs=[query, chatbot],
            )
            query.submit(
                process_query,
                inputs=[query, chatbot],
                outputs=[query, chatbot],
            )
            clear.click(
                clear_history,
                outputs=[query, chatbot],
            )
            
            # Examples
            gr.Examples(
                examples=[
                    ["get weather in London"],
                    ["show file README.md from mygroup/myproject"],
                    ["find high priority SECOPS tickets"],
                    ["search Slack for deployment in #engineering"],
                ],
                inputs=query,
            )
            
    return app

def main():
    app = create_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_api=False,
    )

if __name__ == "__main__":
    main()