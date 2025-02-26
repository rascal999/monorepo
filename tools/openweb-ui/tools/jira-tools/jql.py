"""
title: Jira JQL Tool
description: Tool to execute JQL queries against Jira instances with a web UI
author: Roo
version: 0.1.0
"""

import aiohttp
import os
from typing import Any, Optional, Callable, Awaitable, Dict
from pydantic import BaseModel, Field

class Tools:
    class Valves(BaseModel):
        jira_url: str = Field(
            default="https://mangopay.atlassian.net",
            description="Jira instance URL"
        )
        jira_username: str = Field(
            default=None,
            description="Jira username/email for authentication"
        )
        jira_api_token: str = Field(
            default=None,
            description="Jira API token for authentication",
            secret=True
        )
        jira_project: Optional[str] = Field(
            default=None,
            description="Default Jira project key to scope queries"
        )

    def __init__(self):
        self.valves = self.Valves()

    async def execute_jql(
        self,
        query: str,
        __user__: Dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None
    ) -> str:
        """
        Execute JQL query against Jira instance and return formatted results.

        Args:
            query: JQL query string
            __user__: User configuration containing Jira credentials
            __event_emitter__: Optional event emitter for status updates

        Returns:
            Formatted string containing issue details
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "Executing JQL query...",
                        "done": False,
                    },
                }
            )

        try:
            if not all([self.valves.jira_username, self.valves.jira_api_token]):
                error_msg = "Missing Jira credentials. Please configure jira_username and jira_api_token in the tool settings."
                if __event_emitter__:
                    await __event_emitter__(
                        {"type": "status", "data": {"description": error_msg, "done": True}}
                    )
                return error_msg

            # Construct API endpoint
            search_url = f"{self.valves.jira_url.rstrip('/')}/rest/api/2/search"
            
            # Prepare request payload
            payload = {
                "jql": query,
                "maxResults": 50,  # Fixed limit
                "fields": [
                    "summary",
                    "status",
                    "assignee",
                    "priority",
                    "created",
                    "updated",
                    "reporter",
                    "project"
                ]
            }

            # Set up auth and headers
            auth = aiohttp.BasicAuth(self.valves.jira_username, self.valves.jira_api_token)
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    search_url,
                    json=payload,
                    headers=headers,
                    auth=auth,
                    timeout=30
                ) as response:
                    if response.status == 400:
                        error_text = await response.text()
                        error_msg = f"Invalid JQL query: {error_text}"
                        if __event_emitter__:
                            await __event_emitter__(
                                {"type": "status", "data": {"description": error_msg, "done": True}}
                            )
                        return error_msg
                    response.raise_for_status()
                    data = await response.json()

            if not data:
                error_msg = "No response data received from Jira API"
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": error_msg, "done": True},
                        }
                    )
                return error_msg

            issues = data.get("issues") or []
            total = data.get("total", 0)
            
            if not issues:
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": "No issues found", "done": True},
                        }
                    )
                return f"No issues found for query: '{query}'"

            # Create table header with total count
            results = f"Found {total} issues (showing {len(issues)})\n\n"
            results += "| Key | Summary | Status | Assignee | Priority | Created |\n"
            results += "|-----|---------|---------|-----------|-----------|----------|\n"

            for issue in issues:
                key = issue.get("key") or "Unknown"
                fields = issue.get("fields") or {}
                
                summary = (fields.get("summary") or "No summary")[:50] + "..." if (fields.get("summary") or "No summary") else "No summary"
                status = (fields.get("status") or {}).get("name") or "Unknown"
                assignee = (fields.get("assignee") or {}).get("displayName") or "Unassigned"
                priority = (fields.get("priority") or {}).get("name") or "None"
                created = fields.get("created") or "Unknown"
                
                # Create issue URL and linked key
                issue_url = f"{self.valves.jira_url}/browse/{key}"
                linked_key = f"[{key}]({issue_url})"
                
                # Format issue details as table row
                results += f"| {linked_key} | {summary} | {status} | {assignee} | {priority} | {created} |\n"

                # Emit citation data
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "citation",
                            "data": {
                                "document": [summary],
                                "metadata": [{"source": issue_url}],
                                "source": {"name": key},
                            },
                        }
                    )

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Query completed", "done": True},
                    }
                )

            return results

        except aiohttp.ClientError as e:
            error_msg = f"Error querying Jira: {str(e)}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error during query: {str(e)}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
