from typing import List, Optional, BinaryIO
from slack_sdk.errors import SlackApiError
from .client import SlackClient

class SlackFiles(SlackClient):
    """Handles Slack file operations."""

    def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        channels: Optional[List[str]] = None,
        initial_comment: Optional[str] = None,
        thread_ts: Optional[str] = None
    ) -> dict:
        """Upload a file to Slack."""
        try:
            response = self.client.files_upload_v2(
                file=file,
                filename=filename,
                channel_ids=channels,
                initial_comment=initial_comment,
                thread_ts=thread_ts
            )
            self._handle_response(response)
            return response["file"]
        except SlackApiError as e:
            self.logger.error(f"Error uploading file: {str(e)}")
            raise

    def list_files(
        self,
        channel: Optional[str] = None,
        user: Optional[str] = None,
        types: Optional[str] = None,
        count: int = 100
    ) -> List[dict]:
        """List files in a channel or by a user."""
        try:
            response = self.client.files_list(
                channel=channel,
                user=user,
                types=types,
                count=count
            )
            self._handle_response(response)
            return response["files"]
        except SlackApiError as e:
            self.logger.error(f"Error listing files: {str(e)}")
            raise

    def get_file_info(self, file_id: str) -> dict:
        """Get information about a file."""
        try:
            response = self.client.files_info(file=file_id)
            self._handle_response(response)
            return response["file"]
        except SlackApiError as e:
            self.logger.error(f"Error getting file info: {str(e)}")
            raise

    def delete_file(self, file_id: str) -> dict:
        """Delete a file."""
        try:
            response = self.client.files_delete(file=file_id)
            self._handle_response(response)
            return response
        except SlackApiError as e:
            self.logger.error(f"Error deleting file: {str(e)}")
            raise

    def add_file_comment(self, file_id: str, comment: str) -> dict:
        """Add a comment to a file."""
        try:
            response = self.client.files_comments_add(
                file=file_id,
                comment=comment
            )
            self._handle_response(response)
            return response
        except SlackApiError as e:
            self.logger.error(f"Error adding file comment: {str(e)}")
            raise

    def delete_file_comment(self, file_id: str, comment_id: str) -> dict:
        """Delete a comment from a file."""
        try:
            response = self.client.files_comments_delete(
                file=file_id,
                id=comment_id
            )
            self._handle_response(response)
            return response
        except SlackApiError as e:
            self.logger.error(f"Error deleting file comment: {str(e)}")
            raise