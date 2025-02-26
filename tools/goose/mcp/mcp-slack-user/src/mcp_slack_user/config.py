from pydantic import BaseModel, Field

class SlackConfig(BaseModel):
    """Configuration for Slack client."""
    token: str = Field(..., description="Slack user token")
    default_channel: str = Field(None, description="Default channel for operations")
    workspace_id: str = Field(None, description="Workspace identifier")

    class Config:
        frozen = True  # Make config immutable