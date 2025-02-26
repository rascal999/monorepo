"""
title: Jira Comments Tool
description: Tool to fetch comments from Jira tickets
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

    async def get_comments(
        self,
        ticket_key: str,
        __user__: Dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None
    ) -> str:
        """
        Fetch all comments from a Jira ticket.

        Args:
            ticket_key: Jira ticket key (e.g., PROJ-123)
            __user__: User configuration containing Jira credentials
            __event_emitter__: Optional event emitter for status updates

        Returns:
            Formatted string containing comments
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Fetching comments for ticket {ticket_key}...",
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
            comments_url = f"{self.valves.jira_url.rstrip('/')}/rest/api/2/issue/{ticket_key}/comment"
            
            # Set up auth and headers
            auth = aiohttp.BasicAuth(self.valves.jira_username, self.valves.jira_api_token)
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            # Fetch comments
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    comments_url,
                    headers=headers,
                    auth=auth,
                    timeout=30,
                    params={"expand": "renderedBody"}
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

            if not data:
                error_msg = f"No comment data received for ticket {ticket_key}"
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": error_msg, "done": True},
                        }
                    )
                return error_msg

            comments = data.get("comments") or []
            if not comments:
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": "No comments found", "done": True},
                        }
                    )
                return f"No comments found for ticket {ticket_key}"

            results = f"# Comments for {ticket_key}\n\n"
            for i, comment in enumerate(comments, 1):
                author = (comment.get("author") or {}).get("displayName") or "Unknown"
                created = comment.get("created") or "Unknown"
                updated = comment.get("updated") or created
                body = comment.get("renderedBody") or comment.get("body") or "No content"

                results += f"## Comment {i} - {author}\n"
                results += f"Created: {created}\n"
                if updated != created:
                    results += f"Updated: {updated}\n"
                results += f"\n{body}\n\n"

                # Emit citation data
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "citation",
                            "data": {
                                "document": [body],
                                "metadata": [{"source": f"{self.valves.jira_url}/browse/{ticket_key}"}],
                                "source": {"name": f"{ticket_key} - Comment by {author}"},
                            },
                        }
                    )

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Comments fetched successfully", "done": True},
                    }
                )

            return results

        except aiohttp.ClientError as e:
            error_msg = f"Error fetching comments: {str(e)}"
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