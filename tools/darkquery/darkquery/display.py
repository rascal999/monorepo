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


def display_gitlab_result(result) -> None:
    """Display GitLab query result.
    
    Args:
        result: QueryResult to display
    """
    if not isinstance(result.data, list):
        console.print(result.data)
        return

    # Handle file listing
    if result.metadata and 'project' in result.metadata:
        console.print(f"\nFiles in project [bold]{result.metadata['project']}[/bold]:")
        for item in result.data:
            # Use different icons for files and directories
            icon = "📁" if item['type'] == 'tree' else "📄"
            console.print(f"{icon} {item['path']}")
        return

    # Handle project listing
    if result.metadata and 'group' in result.metadata:
        console.print(f"\nProjects in group [bold]{result.metadata['group']}[/bold]:")
        for project in result.data:
            console.print(f"\n[bold]{project['name']}[/bold]")
            if project['description']:
                console.print(f"Description: {project['description']}")
            console.print(f"Path: {project['path']}")
            console.print(f"URL: {project['web_url']}")
            if project['last_activity']:
                console.print(f"Last activity: {project['last_activity']}")
        return

    # Handle issues and merge requests
    console.print("Found items:")
    for item in result.data:
        # Format based on item type
        item_type = item.get('type', 'unknown')
        if item_type == 'issue':
            prefix = f"#{item['id']}"
        elif item_type == 'merge_request':
            prefix = f"!{item['id']}"
        else:
            prefix = str(item['id'])
                
            # Show title and state with type-specific formatting
            if item_type == 'merge_request':
                state_color = {
                    'opened': 'green',
                    'closed': 'red',
                    'merged': 'blue'
                }.get(item['state'], 'white')
                console.print(
                    f"{prefix}: {item['title']} "
                    f"([{state_color}]{item['state']}[/{state_color}])"
                )
            else:  # issue
                state_color = 'green' if item['state'] == 'opened' else 'red'
                console.print(
                    f"{prefix}: {item['title']} "
                    f"([{state_color}]{item['state']}[/{state_color}])"
                )
            
            # Show additional details for single item view
            if result.metadata.get('limit', 5) == 1:
                if 'description' in item:
                    console.print("\nDescription:")
                    console.print(Markdown(item['description']))
                
                if 'labels' in item and item['labels']:
                    console.print("\nLabels:", ", ".join(item['labels']))
                
                if 'assignees' in item:
                    console.print("\nAssignees:", ", ".join(item['assignees']))
                
                if item_type == 'merge_request':
                    console.print(f"\nSource: {item['source_branch']}")
                    console.print(f"Target: {item['target_branch']}")
                    console.print(f"Merge status: {item['merge_status']}")
                
                if 'comments' in item and item['comments']:
                    console.print("\nComments:")
                    for comment in item['comments']:
                        console.print(
                            f"\n[bold]{comment['author']}[/bold] "
                            f"at {comment['created_at']}:"
                        )
                        console.print(Markdown(comment['body']))
    else:
        console.print(result.data)