"""Display formatting for query results."""
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax

console = Console()


def display_jira_result(result) -> None:
    """Display JIRA query result.
    
    Args:
        result: QueryResult to display
    """
    # Always show JQL query if present in metadata
    if result.metadata and 'jql' in result.metadata:
        console.print(f"JQL: {result.metadata['jql']}\n")
    
    if isinstance(result.data, list):
        console.print("Found tickets:")
        for ticket in result.data:
            console.print(
                f"{ticket['key']}: {ticket['summary']} ({ticket['status']})"
            )
    else:
        console.print(result.data)


def display_file_result(result) -> None:
    """Display file query result.
    
    Args:
        result: QueryResult to display
    """
    if result.metadata and result.metadata.get('path', '').endswith(('.md', '.txt')):
        console.print(Markdown(result.data))
    else:
        # Try to detect language from file extension
        path = result.metadata.get('path', '') if result.metadata else ''
        if path.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.h', '.c')):
            ext = path.split('.')[-1]
            console.print(Syntax(result.data, ext))
        else:
            console.print(result.data)


def display_error(message: str) -> None:
    """Display error message.
    
    Args:
        message: Error message to display
    """
    console.print(f"[red]Error:[/red] {message}")


def display_warning(message: str) -> None:
    """Display warning message.
    
    Args:
        message: Warning message to display
    """
    console.print(f"[yellow]Warning:[/yellow] {message}")