"""
title: Jira Ticket Creation Tool
description: Tool to create Jira tickets with user confirmation
author: Roo
version: 0.1.0
"""

import aiohttp
import os
from typing import Any, Optional, Callable, Awaitable, Dict, Tuple
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
        jira_project: str = Field(
            default=None,
            description="Default Jira project key"
        )

    def __init__(self):
        self.valves = self.Valves()

    async def create_ticket(
        self,
        summary: str,
        description: str,
        issue_type: str = "Task",
        priority: str = "Medium",
        labels: Optional[list[str]] = None,
        __user__: Dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Create a new Jira ticket with user confirmation.

        Args:
            summary: Ticket summary/title
            description: Ticket description in markdown format
            issue_type: Type of issue (Task, Bug, etc.)
            priority: Ticket priority (Low, Medium, High)
            labels: Optional list of labels to add to the ticket
            __user__: User configuration containing Jira credentials
            __event_emitter__: Optional event emitter for status updates

        Returns:
            Tuple of (message, ticket_key). ticket_key is None if ticket wasn't created.
        """
        try:
            if not all([self.valves.jira_username, self.valves.jira_api_token, self.valves.jira_project]):
                error_msg = "Missing Jira credentials or project. Please configure jira_username, jira_api_token, and jira_project in the tool settings."
                if __event_emitter__:
                    await __event_emitter__(
                        {"type": "status", "data": {"description": error_msg, "done": True}}
                    )
                return error_msg, None

            # If confirmed, create the ticket
            if __user__.get("confirmed"):
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {
                                "description": "Creating ticket...",
                                "done": False,
                            },
                        }
                    )

                # Construct API endpoint
                create_url = f"{self.valves.jira_url.rstrip('/')}/rest/api/2/issue"
                
                # Prepare request payload
                payload = {
                    "fields": {
                        "project": {
                            "key": self.valves.jira_project
                        },
                        "summary": summary,
                        "description": description,
                        "issuetype": {
                            "name": issue_type
                        },
                        "priority": {
                            "name": priority
                        }
                    }
                }

                # Add labels if provided
                if labels:
                    payload["fields"]["labels"] = labels

                # Set up auth and headers
                auth = aiohttp.BasicAuth(self.valves.jira_username, self.valves.jira_api_token)
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        create_url,
                        json=payload,
                        headers=headers,
                        auth=auth,
                        timeout=30
                    ) as response:
                        if response.status == 400:
                            error_text = await response.text()
                            error_msg = f"Invalid ticket data: {error_text}"
                            if __event_emitter__:
                                await __event_emitter__(
                                    {"type": "status", "data": {"description": error_msg, "done": True}}
                                )
                            return error_msg, None
                        response.raise_for_status()
                        data = await response.json()

                # Get new ticket key and URL
                ticket_key = data.get("key")
                if not ticket_key:
                    error_msg = "No ticket key received from Jira API"
                    if __event_emitter__:
                        await __event_emitter__(
                            {"type": "status", "data": {"description": error_msg, "done": True}}
                        )
                    return error_msg, None

                ticket_url = f"{self.valves.jira_url}/browse/{ticket_key}"

                success_msg = f"Created ticket [{ticket_key}]({ticket_url})"
                
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": success_msg, "done": True},
                        }
                    )
                    await __event_emitter__(
                        {
                            "type": "citation",
                            "data": {
                                "document": [summary, description],
                                "metadata": [{"source": ticket_url}],
                                "source": {"name": ticket_key},
                            },
                        }
                    )

                return success_msg, ticket_key

            # Show preview
            preview_details = [
                f"Project: {self.valves.jira_project}",
                f"Summary: {summary}",
                f"Description: {description}",
                f"Priority: {priority}",
                f"Issue Type: {issue_type}"
            ]
            
            if labels:
                preview_details.append(f"Labels: {', '.join(labels)}")

            preview = "\n".join(preview_details)

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "Review ticket details and confirm",
                            "done": False,
                        },
                    }
                )

            return preview, None

        except aiohttp.ClientError as e:
            error_msg = f"Error creating ticket: {str(e)}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg, None
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg, None