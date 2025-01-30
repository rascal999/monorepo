import json
import logging
from collections.abc import Sequence
from typing import Any

from mcp.server import Server
from mcp.types import Resource, TextContent, Tool
from pydantic import AnyUrl

from .jira import JiraFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-atlassian")

# Initialize the content fetchers
try:
    jira_fetcher = JiraFetcher()
except ValueError as e:
    logger.error(f"Jira initialization failed: {str(e)}")
    raise

app = Server("mcp-atlassian")


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available Jira projects as resources."""
    resources = []

    # Add Jira projects
    try:
        projects = jira_fetcher.jira.projects()
        resources.extend(
            [
                Resource(
                    uri=AnyUrl(f"jira://{project['key']}"),
                    name=f"Jira Project: {project['name']}",
                    mimeType="text/plain",
                    description=project.get("description", ""),
                )
                for project in projects
            ]
        )
    except Exception as e:
        logger.error(f"Error fetching Jira projects: {str(e)}")

    return resources


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read content from Jira."""
    uri_str = str(uri)

    # Handle Jira resources
    if uri_str.startswith("jira://"):
        parts = uri_str.replace("jira://", "").split("/")

        # Handle project listing
        if len(parts) == 1:
            project_key = parts[0]
            issues = jira_fetcher.get_project_issues(project_key)
            content = []
            for issue in issues:
                content.append(f"# {issue.metadata['key']}: {issue.metadata['title']}\n\n{issue.page_content}\n---")
            return "\n\n".join(content)

        # Handle specific issue
        elif len(parts) >= 3 and parts[1] == "issues":
            issue_key = parts[2]
            issue = jira_fetcher.get_issue(issue_key)
            return issue.page_content

    raise ValueError(f"Invalid resource URI: {uri}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Jira tools."""
    return [
        Tool(
            name="jira_get_issue",
            description="Get details of a specific Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Jira issue key (e.g., 'PROJ-123')"},
                    "expand": {"type": "string", "description": "Optional fields to expand", "default": None},
                },
                "required": ["issue_key"],
            },
        ),
        Tool(
            name="jira_search",
            description="Search Jira issues using JQL",
            inputSchema={
                "type": "object",
                "properties": {
                    "jql": {"type": "string", "description": "JQL query string"},
                    "fields": {"type": "string", "description": "Comma-separated fields to return", "default": "*all"},
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results (1-50)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50,
                    },
                },
                "required": ["jql"],
            },
        ),
        Tool(
            name="jira_get_project_issues",
            description="Get all issues for a specific Jira project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {"type": "string", "description": "The project key"},
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results (1-50)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50,
                    },
                },
                "required": ["project_key"],
            },
        ),
        Tool(
            name="jira_create_issue",
            description="Create a new Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {"type": "string", "description": "The project key where the issue will be created"},
                    "summary": {"type": "string", "description": "Issue title/summary"},
                    "description": {"type": "string", "description": "Detailed description of the issue"},
                    "issue_type": {"type": "string", "description": "Type of issue (e.g., 'Task', 'Bug', 'Story')", "default": "Task"},
                    "priority": {"type": "string", "description": "Priority level (e.g., 'High', 'Medium', 'Low')", "default": None},
                    "assignee": {"type": "string", "description": "Username of the assignee", "default": None},
                    "labels": {"type": "array", "items": {"type": "string"}, "description": "List of labels", "default": None},
                },
                "required": ["project_key", "summary", "description"],
            },
        ),
        Tool(
            name="jira_update_issue",
            description="Update an existing Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "The issue key to update (e.g., 'PROJ-123')"},
                    "summary": {"type": "string", "description": "New summary/title"},
                    "description": {"type": "string", "description": "New description"},
                    "status": {"type": "string", "description": "New status"},
                    "priority": {"type": "string", "description": "New priority level"},
                    "assignee": {"type": "string", "description": "New assignee username"},
                    "labels": {"type": "array", "items": {"type": "string"}, "description": "New list of labels"},
                },
                "required": ["issue_key"],
            },
        ),
        Tool(
            name="jira_add_comment",
            description="Add a comment to a Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "The issue key to comment on (e.g., 'PROJ-123')"},
                    "comment": {"type": "string", "description": "The comment text to add"},
                },
                "required": ["issue_key", "comment"],
            },
        ),
        Tool(
            name="jira_link_issues",
            description="Create a link between two Jira issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "inward_issue": {"type": "string", "description": "Key of the source issue (e.g., 'PROJ-123')"},
                    "outward_issue": {"type": "string", "description": "Key of the target issue (e.g., 'PROJ-124')"},
                    "link_type": {"type": "string", "description": "Type of link (e.g., 'Relates', 'Blocks', 'Depends')", "default": "Relates"},
                    "comment": {"type": "string", "description": "Optional comment to add to the link", "default": None},
                },
                "required": ["inward_issue", "outward_issue"],
            },
        ),
        Tool(
            name="jira_get_links",
            description="Get all links for a Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "The issue key to get links for (e.g., 'PROJ-123')"},
                },
                "required": ["issue_key"],
            },
        ),
        Tool(
            name="jira_remove_link",
            description="Remove a link between Jira issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "The issue key to return after removing the link (e.g., 'PROJ-123')"},
                    "link_id": {"type": "string", "description": "ID of the link to remove (get this from jira_get_links)"},
                },
                "required": ["issue_key", "link_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls for Jira operations."""
    try:
        if name == "jira_get_issue":
            doc = jira_fetcher.get_issue(arguments["issue_key"], expand=arguments.get("expand"))
            result = {"content": doc.page_content, "metadata": doc.metadata}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "jira_search":
            limit = min(int(arguments.get("limit", 10)), 50)
            documents = jira_fetcher.search_issues(
                arguments["jql"], fields=arguments.get("fields", "*all"), limit=limit
            )
            search_results = [
                {
                    "key": doc.metadata["key"],
                    "title": doc.metadata["title"],
                    "type": doc.metadata["type"],
                    "status": doc.metadata["status"],
                    "created_date": doc.metadata["created_date"],
                    "priority": doc.metadata["priority"],
                    "link": doc.metadata["link"],
                    "excerpt": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                }
                for doc in documents
            ]
            return [TextContent(type="text", text=json.dumps(search_results, indent=2))]

        elif name == "jira_get_project_issues":
            limit = min(int(arguments.get("limit", 10)), 50)
            documents = jira_fetcher.get_project_issues(arguments["project_key"], limit=limit)
            project_issues = [
                {
                    "key": doc.metadata["key"],
                    "title": doc.metadata["title"],
                    "type": doc.metadata["type"],
                    "status": doc.metadata["status"],
                    "created_date": doc.metadata["created_date"],
                    "link": doc.metadata["link"],
                }
                for doc in documents
            ]
            return [TextContent(type="text", text=json.dumps(project_issues, indent=2))]

        elif name == "jira_create_issue":
            doc = jira_fetcher.create_issue(
                project_key=arguments["project_key"],
                summary=arguments["summary"],
                description=arguments["description"],
                issue_type=arguments.get("issue_type", "Task"),
                priority=arguments.get("priority"),
                assignee=arguments.get("assignee"),
                labels=arguments.get("labels"),
            )
            result = {"content": doc.page_content, "metadata": doc.metadata}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "jira_update_issue":
            doc = jira_fetcher.update_issue(
                issue_key=arguments["issue_key"],
                summary=arguments.get("summary"),
                description=arguments.get("description"),
                status=arguments.get("status"),
                priority=arguments.get("priority"),
                assignee=arguments.get("assignee"),
                labels=arguments.get("labels"),
            )
            result = {"content": doc.page_content, "metadata": doc.metadata}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "jira_add_comment":
            doc = jira_fetcher.add_comment(
                issue_key=arguments["issue_key"],
                comment=arguments["comment"],
            )
            result = {"content": doc.page_content, "metadata": doc.metadata}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "jira_link_issues":
            doc = jira_fetcher.link_issues(
                inward_issue=arguments["inward_issue"],
                outward_issue=arguments["outward_issue"],
                link_type=arguments.get("link_type", "Relates"),
                comment=arguments.get("comment"),
            )
            result = {"content": doc.page_content, "metadata": doc.metadata}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "jira_get_links":
            links = jira_fetcher.get_issue_links(arguments["issue_key"])
            return [TextContent(type="text", text=json.dumps(links, indent=2))]

        elif name == "jira_remove_link":
            doc = jira_fetcher.remove_link(
                issue_key=arguments["issue_key"],
                link_id=arguments["link_id"],
            )
            result = {"content": doc.page_content, "metadata": doc.metadata}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        raise RuntimeError(f"Tool execution failed: {str(e)}")


async def main():
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
