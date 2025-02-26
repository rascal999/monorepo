import re
from typing import Optional
from markdownify import markdownify as md

class TextPreprocessor:
    """Handles text preprocessing for Slack content."""

    def __init__(self, workspace_url: Optional[str] = None):
        self.workspace_url = workspace_url

    def clean_slack_text(self, text: str) -> str:
        """
        Clean and format Slack text content:
        1. Convert user mentions to readable format
        2. Convert channel mentions to readable format
        3. Process links and URLs
        4. Handle special characters and formatting
        """
        if not text:
            return ""

        # Process user mentions (<@U123ABC>)
        text = re.sub(
            r"<@([A-Z0-9]+)>",
            lambda m: f"@user_{m.group(1)}",
            text
        )

        # Process channel mentions (<#C123ABC>)
        text = re.sub(
            r"<#([A-Z0-9]+)(?:\|([^>]+))?>",
            lambda m: f"#{m.group(2) if m.group(2) else f'channel_{m.group(1)}'}",
            text
        )

        # Process links (<http://example.com|text>)
        text = re.sub(
            r"<((?:http|https)://[^|>]+)\|([^>]+)>",
            lambda m: f"[{m.group(2)}]({m.group(1)})",
            text
        )

        # Process plain URLs (<http://example.com>)
        text = re.sub(
            r"<((?:http|https)://[^>]+)>",
            lambda m: m.group(1),
            text
        )

        # Convert HTML to markdown if present
        if re.search(r"<[^>]+>", text):
            text = md(text)

        # Handle special characters
        text = text.replace("&lt;", "<") \
                   .replace("&gt;", ">") \
                   .replace("&amp;", "&")

        # Process emoji
        text = re.sub(
            r":([a-z0-9_+-]+):",
            lambda m: f":{m.group(1)}:",
            text
        )

        return text.strip()

    def format_for_slack(self, text: str) -> str:
        """
        Format text for sending to Slack:
        1. Escape special characters
        2. Format links properly
        3. Handle markdown conversion
        """
        if not text:
            return ""

        # Escape special characters
        text = text.replace("&", "&amp;") \
                   .replace("<", "&lt;") \
                   .replace(">", "&gt;")

        # Format markdown links
        text = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            lambda m: f"<{m.group(2)}|{m.group(1)}>",
            text
        )

        # Format plain URLs
        text = re.sub(
            r"(?<!<)(https?://\S+)(?!>)",
            lambda m: f"<{m.group(1)}>",
            text
        )

        return text.strip()