from typing import Optional, List
import logging
import time
from slack_sdk.errors import SlackApiError
from .client import SlackClient

# Configure logging
logger = logging.getLogger("mcp-slack")

class SlackMessages(SlackClient):
    """Handles Slack message operations."""

    def get_channel_messages(self, channel_id: str, limit: int = 10) -> List[dict]:
        """Get messages from a channel using pagination."""
        try:
            all_messages = []
            cursor = None
            
            while len(all_messages) < limit:
                # Get a page of messages
                response = self.client.conversations_history(
                    channel=channel_id,
                    cursor=cursor,
                    limit=min(limit - len(all_messages), 50)  # More conservative limit
                )
                self._handle_response(response)
                
                # Add messages from this page
                all_messages.extend(response["messages"])
                
                # Check if there are more pages
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor or len(all_messages) >= limit:
                    break
                
                logger.debug(f"Fetched {len(all_messages)} messages, getting next page...")
                # Add delay between requests to avoid rate limiting
                time.sleep(1)
            
            logger.info(f"Total messages fetched: {len(all_messages)}")
            return all_messages[:limit]  # Ensure we don't return more than requested
        except SlackApiError as e:
            logger.error(f"Error fetching messages: {str(e)}")
            raise

    def get_dm_messages(self, user_id: str, limit: int = 10) -> List[dict]:
        """Get direct messages with a user using pagination."""
        try:
            # List all DM channels with pagination
            all_channels = []
            cursor = None
            
            while True:
                # Get a page of DM channels
                response = self.client.conversations_list(
                    types="im",
                    cursor=cursor,
                    limit=200  # Conservative limit
                )
                self._handle_response(response)
                
                # Add channels from this page
                all_channels.extend(response["channels"])
                
                # Check if there are more pages
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break
                
                logger.debug(f"Fetched {len(all_channels)} DM channels, getting next page...")
                # Add delay between requests to avoid rate limiting
                time.sleep(1)
            
            # Find the DM channel with this user
            dm_channel = None
            for channel in all_channels:
                if channel["user"] == user_id:
                    dm_channel = channel
                    break
            
            if not dm_channel:
                logger.error(f"No DM channel found in {len(all_channels)} channels for user {user_id}")
                raise ValueError(f"No DM channel found with user {user_id}")

            # Then get messages from that channel
            return self.get_channel_messages(dm_channel["id"], limit)
        except SlackApiError as e:
            logger.error(f"Error fetching DMs: {str(e)}")
            raise

    def send_message(
        self,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None,
        reply_broadcast: bool = False
    ) -> dict:
        """Send a message to a channel or thread."""
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                thread_ts=thread_ts,
                reply_broadcast=reply_broadcast
            )
            self._handle_response(response)
            return response
        except SlackApiError as e:
            logger.error(f"Error sending message: {str(e)}")
            raise

    def update_message(
        self,
        channel: str,
        ts: str,
        text: str
    ) -> dict:
        """Update an existing message."""
        try:
            response = self.client.chat_update(
                channel=channel,
                ts=ts,
                text=text
            )
            self._handle_response(response)
            return response
        except SlackApiError as e:
            logger.error(f"Error updating message: {str(e)}")
            raise

    def delete_message(
        self,
        channel: str,
        ts: str
    ) -> dict:
        """Delete a message."""
        try:
            response = self.client.chat_delete(
                channel=channel,
                ts=ts
            )
            self._handle_response(response)
            return response
        except SlackApiError as e:
            logger.error(f"Error deleting message: {str(e)}")
            raise

    def get_message_replies(
        self,
        channel: str,
        thread_ts: str,
        limit: int = 10
    ) -> List[dict]:
        """Get replies in a message thread using pagination."""
        try:
            all_replies = []
            cursor = None
            
            while len(all_replies) < limit:
                # Get a page of replies
                response = self.client.conversations_replies(
                    channel=channel,
                    ts=thread_ts,
                    cursor=cursor,
                    limit=min(limit - len(all_replies), 50)  # More conservative limit
                )
                self._handle_response(response)
                
                # Add replies from this page
                all_replies.extend(response["messages"])
                
                # Check if there are more pages
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor or len(all_replies) >= limit:
                    break
                
                logger.debug(f"Fetched {len(all_replies)} replies, getting next page...")
                # Add delay between requests to avoid rate limiting
                time.sleep(1)
            
            logger.info(f"Total replies fetched: {len(all_replies)}")
            return all_replies[:limit]  # Ensure we don't return more than requested
        except SlackApiError as e:
            logger.error(f"Error fetching replies: {str(e)}")
            raise

    def search_messages(
        self,
        query: str,
        channel: Optional[str] = None,
        limit: int = 10
    ) -> List[dict]:
        """Search messages using pagination."""
        try:
            all_results = []
            page = 1
            
            while len(all_results) < limit:
                # Get a page of search results
                response = self.client.search_messages(
                    query=query,
                    page=page,
                    count=min(limit - len(all_results), 50)  # More conservative limit
                )
                self._handle_response(response)
                
                # Add messages from this page
                matches = response["messages"]["matches"]
                if channel:
                    matches = [m for m in matches if m.get("channel", {}).get("id") == channel]
                all_results.extend(matches)
                
                # Check if there are more pages
                if not response["messages"]["paging"].get("pages", 0) > page or len(all_results) >= limit:
                    break
                
                page += 1
                logger.debug(f"Fetched {len(all_results)} search results, getting next page...")
                # Add delay between requests to avoid rate limiting
                time.sleep(1)
            
            logger.info(f"Total search results fetched: {len(all_results)}")
            return all_results[:limit]  # Ensure we don't return more than requested
        except SlackApiError as e:
            logger.error(f"Error searching messages: {str(e)}")
            raise