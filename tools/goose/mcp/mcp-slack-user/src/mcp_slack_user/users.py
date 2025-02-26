from typing import List, Optional
import logging
import time
from slack_sdk.errors import SlackApiError
from .client import SlackClient

# Configure logging
logger = logging.getLogger("mcp-slack")

class SlackUsers(SlackClient):
    """Handles Slack user operations."""

    def list_users(self, include_presence: bool = False) -> List[dict]:
        """List all users in the workspace using pagination."""
        try:
            all_users = []
            cursor = None
            
            while True:
                # Get a page of users
                response = self.client.users_list(
                    presence=include_presence,
                    cursor=cursor,
                    limit=200  # More conservative limit to avoid rate limiting
                )
                self._handle_response(response)
                
                # Add users from this page
                all_users.extend(response["members"])
                
                # Check if there are more pages
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break
                
                logger.debug(f"Fetched {len(all_users)} users, getting next page...")
                # Add delay between requests to avoid rate limiting
                time.sleep(1)
            
            logger.info(f"Total users fetched: {len(all_users)}")
            return all_users
        except SlackApiError as e:
            logger.error(f"Error listing users: {str(e)}")
            raise

    def get_user_info(self, user_id: str) -> dict:
        """Get information about a specific user."""
        try:
            response = self.client.users_info(user=user_id)
            self._handle_response(response)
            return response["user"]
        except SlackApiError as e:
            logger.error(f"Error getting user info: {str(e)}")
            raise

    def get_user_presence(self, user_id: str) -> dict:
        """Get a user's presence status."""
        try:
            response = self.client.users_getPresence(user=user_id)
            self._handle_response(response)
            return response
        except SlackApiError as e:
            logger.error(f"Error getting user presence: {str(e)}")
            raise

    def get_user_by_email(self, email: str) -> dict:
        """Look up a user by their email address."""
        try:
            response = self.client.users_lookupByEmail(email=email)
            self._handle_response(response)
            return response["user"]
        except SlackApiError as e:
            logger.error(f"Error looking up user by email: {str(e)}")
            raise

    def get_user_profile(self, user_id: str) -> dict:
        """Get a user's profile information."""
        try:
            response = self.client.users_profile_get(user=user_id)
            self._handle_response(response)
            return response["profile"]
        except SlackApiError as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise

    def get_users_in_channel(self, channel_id: str) -> List[str]:
        """Get list of user IDs in a channel using pagination."""
        try:
            all_members = []
            cursor = None
            
            while True:
                # Get a page of members
                response = self.client.conversations_members(
                    channel=channel_id,
                    cursor=cursor,
                    limit=200  # More conservative limit to avoid rate limiting
                )
                self._handle_response(response)
                
                # Add members from this page
                all_members.extend(response["members"])
                
                # Check if there are more pages
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break
                
                logger.debug(f"Fetched {len(all_members)} channel members, getting next page...")
                # Add delay between requests to avoid rate limiting
                time.sleep(1)
            
            logger.info(f"Total channel members fetched: {len(all_members)}")
            return all_members
        except SlackApiError as e:
            logger.error(f"Error getting channel members: {str(e)}")
            raise

    def get_bot_info(self, bot_id: str) -> dict:
        """Get information about a bot user."""
        try:
            response = self.client.bots_info(bot=bot_id)
            self._handle_response(response)
            return response["bot"]
        except SlackApiError as e:
            logger.error(f"Error getting bot info: {str(e)}")
            raise