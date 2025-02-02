"""Interactive shell for darkquery."""
import logging
from pathlib import Path
from typing import Dict

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console

from .commands import CompleteCommandHandler
from .display import console
from .ollama import OllamaClient


class DarkQueryShell:
    """Interactive shell for darkquery."""
    
    def __init__(
        self,
        data_sources: Dict,
        ollama_url: str,
        ollama_model: str,
        verbose: bool = False
    ):
        """Initialize the interactive shell.
        
        Args:
            data_sources: Dictionary of available data sources
            ollama_url: URL of Ollama instance
            ollama_model: Name of Ollama model to use
            verbose: Enable verbose output
        """
        # Initialize Ollama client
        ollama = OllamaClient(ollama_url, ollama_model, verbose)
        
        # Initialize command handler
        self.handler = CompleteCommandHandler(data_sources, ollama, verbose)
        
        # Set up command history
        history_file = Path.home() / ".darkquery_history"
        self.session = PromptSession(history=FileHistory(str(history_file)))
        
        # Set up logging
        self.logger = logging.getLogger("darkquery")
    
    def start(self) -> None:
        """Start the interactive shell."""
        console.print("[bold blue]Welcome to darkquery![/bold blue]")
        console.print("Type your queries in natural language or 'exit' to quit.\n")
        console.print("Commands:")
        console.print("  open - Open last viewed ticket in browser")
        console.print("  exit - Exit the shell\n")
        
        while True:
            try:
                # Build prompt with context
                prompt = "> "
                if self.handler.context:
                    # Show ticket ID and summary for JIRA
                    if self.handler.context.get('type') == 'jira':
                        ticket = self.handler.context.get('ticket', '')
                        summary = self.handler.context.get('summary', '')
                        if summary:
                            prompt = f"[{ticket}: {summary}] > "
                        else:
                            prompt = f"[{ticket}] > "
                    # Show project path for GitLab
                    elif self.handler.context.get('type') == 'gitlab':
                        project = self.handler.context.get('project', '')
                        if project:
                            prompt = f"[{project}] > "
                
                # Get input with prompt and history support
                query = self.session.prompt(prompt)
                
                if query.lower() in ("exit", "quit"):
                    break
                    
                # Handle direct commands
                if query.lower() == "open":
                    self.handler.handle_open()
                    continue
                    
                # Process query through command handler
                result = self.handler.process_query(query)
                if result is None:  # Command was handled and completed
                    continue
                
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                self.logger.exception("Error in shell")
                console.print(f"[red]Error:[/red] {str(e)}")
        
        console.print("\nGoodbye!")