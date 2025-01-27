"""Command handling package."""
from .base import CommandHandler
from .browser import BrowserMixin
from .execute import ExecuteMixin
from .gitlab import GitLabMixin
from .jira import JIRAMixin


class CompleteCommandHandler(
    BrowserMixin,
    ExecuteMixin,
    GitLabMixin,
    JIRAMixin,
    CommandHandler
):
    """Complete command handler with all functionality."""
    pass


__all__ = ['CompleteCommandHandler']