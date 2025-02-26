"""
title: Jira Ticket Content Tool
description: Tool to fetch detailed content of Jira tickets
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
            default="https://mgp.atlassian.net",
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

    def __init__(self):
        self.valves = self.Valves()

    async def get_ticket_content(
        self,
        ticket_key: str,
        __user__: Dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None
    ) -> str:
        """
        Fetch detailed content of a Jira ticket including description, comments, and attachments.

        Args:
            ticket_key: Jira ticket key (e.g., PROJ-123)
            __user__: User configuration containing Jira credentials
            __event_emitter__: Optional event emitter for status updates

        Returns:
            Formatted string containing ticket details
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Fetching content for ticket {ticket_key}...",
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
            issue_url = f"{self.valves.jira_url.rstrip('/')}/rest/api/2/issue/{ticket_key}"
            
            # Set up auth and headers
            auth = aiohttp.BasicAuth(self.valves.jira_username, self.valves.jira_api_token)
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            # Fetch issue details
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    issue_url,
                    headers=headers,
                    auth=auth,
                    timeout=30,
                    params={"expand": "renderedFields,changelog,comments,attachments"}
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

            if not data:
                error_msg = f"Ticket {ticket_key} not found"
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": error_msg, "done": True},
                        }
                    )
                return error_msg

            # Extract fields with safe access
            fields = data.get("fields", {}) or {}
            rendered_fields = data.get("renderedFields", {}) or {}
            
            # Get field values with safe fallbacks
            summary = fields.get("summary") or "No summary"
            status = (fields.get("status") or {}).get("name") or "Unknown"
            assignee = (fields.get("assignee") or {}).get("displayName") or "Unassigned"
            reporter = (fields.get("reporter") or {}).get("displayName") or "Unknown"
            priority = (fields.get("priority") or {}).get("name") or "None"
            created = fields.get("created") or "Unknown"
            updated = fields.get("updated") or "Unknown"
            description = rendered_fields.get("description") or fields.get("description") or "No description"
            
            # Format ticket details
            results = f"# {ticket_key}: {summary}\n\n"
            results += f"Status: {status}\n"
            results += f"Assignee: {assignee}\n"
            results += f"Reporter: {reporter}\n"
            results += f"Priority: {priority}\n"
            results += f"Created: {created}\n"
            results += f"Updated: {updated}\n"
            results += f"\n## Description\n\n{description}\n\n"

            # Add comments with safe access
            comments = (data.get("comments") or {}).get("comments") or []
            if comments:
                results += "## Comments\n\n"
                for comment in comments:
                    author = (comment.get("author") or {}).get("displayName") or "Unknown"
                    created = comment.get("created") or "Unknown"
                    body = comment.get("renderedBody") or comment.get("body") or "No content"
                    results += f"### {author} - {created}\n\n{body}\n\n"

            # Add attachments with safe access
            attachments = fields.get("attachment") or []
            if attachments:
                results += "## Attachments\n\n"
                for attachment in attachments:
                    filename = attachment.get("filename") or "Unknown"
                    url = attachment.get("content") or "No URL"
                    created = attachment.get("created") or "Unknown"
                    results += f"- [{filename}]({url}) (added {created})\n"

            # Add ticket URL
            ticket_url = f"{self.valves.jira_url}/browse/{ticket_key}"
            results += f"\n[View in Jira]({ticket_url})\n"

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Content fetched successfully", "done": True},
                    }
                )

                # Emit citation data
                await __event_emitter__(
                    {
                        "type": "citation",
                        "data": {
                            "document": [description],
                            "metadata": [{"source": ticket_url}],
                            "source": {"name": f"{ticket_key}: {summary}"},
                        },
                    }
                )

            return results

        except aiohttp.ClientError as e:
            error_msg = f"Error fetching ticket content: {str(e)}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg