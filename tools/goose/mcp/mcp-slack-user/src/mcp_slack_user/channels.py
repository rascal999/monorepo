from typing import List, Optional, Dict
import logging
import time
import json
import os
from pathlib import Path
from slack_sdk.errors import SlackApiError
from .client import SlackClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-slack")

# Pagination settings based on testing
CHANNELS_PER_PAGE = 50  # Conservative page size
DELAY_BETWEEN_PAGES = 2  # 2 second delay

class SlackChannels(SlackClient):
    """Handles Slack channel operations."""

    def __init__(self):
        super().__init__()
        self._channel_name_to_id: Dict[str, str] = {}  # Cache for channel name to ID mapping
        self._cache_file = Path(os.path.expanduser("~/.cache/mcp-slack-user/channel_cache.json"))
        self._load_cache()

    def _load_cache(self):
        """Load channel cache from file."""
        try:
            if self._cache_file.exists():
                with open(self._cache_file, 'r') as f:
                    self._channel_name_to_id = json.load(f)
                logger.debug(f"Loaded {len(self._channel_name_to_id)} channels from cache")
                logger.debug(f"Cached channels: {list(self._channel_name_to_id.keys())}")
        except Exception as e:
            logger.error(f"Error loading channel cache: {str(e)}")
            self._channel_name_to_id = {}

    def _save_cache(self):
        """Save channel cache to file."""
        try:
            self._cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._cache_file, 'w') as f:
                json.dump(self._channel_name_to_id, f)
            logger.debug(f"Saved {len(self._channel_name_to_id)} channels to cache")
            logger.debug(f"Updated cache with: {list(self._channel_name_to_id.keys())}")
        except Exception as e:
            logger.error(f"Error saving channel cache: {str(e)}")

    def get_channel_by_name(self, channel_name: str) -> dict:
        """Get channel by name directly."""
        try:
            # Check cache first
            channel_name = channel_name.lstrip('#')
            logger.info(f"Looking up channel: {channel_name}")
            
            if channel_name in self._channel_name_to_id:
                logger.info(f"Channel ID found in cache: {channel_name} -> {self._channel_name_to_id[channel_name]}")
                channel_id = self._channel_name_to_id[channel_name]
                try:
                    logger.debug(f"Verifying cached channel ID: {channel_id}")
                    return self.get_channel_info(channel_id)
                except SlackApiError as e:
                    logger.info(f"Cached channel ID invalid ({e}), removing: {channel_name}")
                    del self._channel_name_to_id[channel_name]
                    self._save_cache()

            # Try to get channel info directly first
            logger.info(f"Trying direct channel lookup: {channel_name}")
            response = self.client.conversations_info(channel=channel_name)
            self._handle_response(response)
            channel = response["channel"]
            logger.info(f"Found channel directly: {channel['name']} ({channel['id']})")
            
            # Update cache
            self._channel_name_to_id[channel["name"]] = channel["id"]
            self._save_cache()
            return channel
        except SlackApiError as e:
            if "channel_not_found" in str(e):
                # If not found by name, try to find in channel list
                logger.info(f"Channel not found directly, trying channel list: {channel_name}")
                channels = self.list_channels()
                for channel in channels:
                    # Update cache for all channels while we're here
                    self._channel_name_to_id[channel['name']] = channel['id']
                    if channel['name'] == channel_name:
                        logger.info(f"Found channel in listing: {channel['name']} ({channel['id']})")
                        self._save_cache()
                        return channel
                logger.error(f"Channel not found in any source: {channel_name}")
                raise ValueError(f"Channel not found: {channel_name}")
            logger.error(f"Error looking up channel: {str(e)}")
            raise

    def list_channels(self, exclude_archived: bool = True) -> List[dict]:
        """List all channels in the workspace using pagination."""
        try:
            all_channels = []
            cursor = None
            page = 1
            start_time = time.time()
            
            logger.info("Starting channel listing")
            while True:
                logger.info(f"Fetching page {page} (cursor: {cursor})")
                
                # Get a page of channels
                response = self.client.conversations_list(
                    exclude_archived=exclude_archived,
                    types="public_channel,private_channel",
                    cursor=cursor,
                    limit=CHANNELS_PER_PAGE
                )
                self._handle_response(response)
                
                # Add channels from this page
                channels = response["channels"]
                channels_count = len(channels)
                all_channels.extend(channels)
                
                # Update cache while we're here
                for channel in channels:
                    self._channel_name_to_id[channel['name']] = channel['id']
                    logger.debug(f"Caching channel: {channel['name']} -> {channel['id']}")
                
                logger.info(f"Page {page}: Got {channels_count} channels (Total: {len(all_channels)})")
                logger.debug(f"Page {page} channels: {[c['name'] for c in channels]}")
                
                # Break if no more channels or no cursor
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if channels_count == 0 or not cursor:
                    logger.info(f"Pagination complete: no more channels ({channels_count}) or no cursor ({cursor})")
                    break
                
                # Add delay between requests to avoid rate limiting
                logger.debug(f"Waiting {DELAY_BETWEEN_PAGES}s before next page")
                time.sleep(DELAY_BETWEEN_PAGES)
                page += 1
            
            # Save complete cache after listing all channels
            self._save_cache()
            
            end_time = time.time()
            total_time = end_time - start_time
            logger.info(
                f"Channel listing complete:\n"
                f"- Total channels: {len(all_channels)}\n"
                f"- Total pages: {page}\n"
                f"- Total time: {total_time:.2f}s\n"
                f"- Avg time per page: {total_time/page:.2f}s\n"
                f"- Avg channels per page: {len(all_channels)/page:.2f}\n"
                f"- Channel names: {[c['name'] for c in all_channels]}"
            )
            
            return all_channels
        except SlackApiError as e:
            logger.error(f"Error listing channels: {str(e)}")
            raise

    def create_channel(
        self,
        name: str,
        is_private: bool = False,
        user_ids: Optional[List[str]] = None
    ) -> dict:
        """Create a new channel."""
        try:
            logger.info(f"Creating channel: {name} (private: {is_private})")
            response = self.client.conversations_create(
                name=name,
                is_private=is_private
            )
            self._handle_response(response)
            channel = response["channel"]
            logger.info(f"Channel created: {channel['name']} ({channel['id']})")
            
            # Update cache
            self._channel_name_to_id[channel['name']] = channel['id']
            self._save_cache()
            
            # If user_ids provided, invite them to the channel
            if user_ids and channel["id"]:
                # Split into smaller chunks to avoid rate limiting
                chunk_size = 30
                for i in range(0, len(user_ids), chunk_size):
                    chunk = user_ids[i:i + chunk_size]
                    logger.info(f"Inviting users chunk {i//chunk_size + 1}: {chunk}")
                    self.invite_to_channel(channel["id"], chunk)
                    if i + chunk_size < len(user_ids):
                        logger.debug(f"Waiting {DELAY_BETWEEN_PAGES}s before next invite chunk")
                        time.sleep(DELAY_BETWEEN_PAGES)  # Add delay between chunks
                
            return channel
        except SlackApiError as e:
            logger.error(f"Error creating channel: {str(e)}")
            raise

    def archive_channel(self, channel_id: str) -> dict:
        """Archive a channel."""
        try:
            logger.info(f"Archiving channel: {channel_id}")
            response = self.client.conversations_archive(channel=channel_id)
            self._handle_response(response)
            return response
        except SlackApiError as e:
            logger.error(f"Error archiving channel: {str(e)}")
            raise

    def unarchive_channel(self, channel_id: str) -> dict:
        """Unarchive a channel."""
        try:
            logger.info(f"Unarchiving channel: {channel_id}")
            response = self.client.conversations_unarchive(channel=channel_id)
            self._handle_response(response)
            return response
        except SlackApiError as e:
            logger.error(f"Error unarchiving channel: {str(e)}")
            raise

    def invite_to_channel(self, channel_id: str, user_ids: List[str]) -> dict:
        """Invite users to a channel."""
        try:
            logger.info(f"Inviting users to channel {channel_id}: {user_ids}")
            response = self.client.conversations_invite(
                channel=channel_id,
                users=",".join(user_ids)
            )
            self._handle_response(response)
            return response
        except SlackApiError as e:
            logger.error(f"Error inviting users to channel: {str(e)}")
            raise

    def join_channel(self, channel_id: str) -> dict:
        """Join a channel."""
        try:
            logger.info(f"Joining channel: {channel_id}")
            response = self.client.conversations_join(channel=channel_id)
            self._handle_response(response)
            return response
        except SlackApiError as e:
            logger.error(f"Error joining channel: {str(e)}")
            raise

    def leave_channel(self, channel_id: str) -> dict:
        """Leave a channel."""
        try:
            logger.info(f"Leaving channel: {channel_id}")
            response = self.client.conversations_leave(channel=channel_id)
            self._handle_response(response)
            return response
        except SlackApiError as e:
            logger.error(f"Error leaving channel: {str(e)}")
            raise

    def get_channel_info(self, channel_id: str) -> dict:
        """Get information about a channel."""
        try:
            logger.info(f"Getting channel info: {channel_id}")
            response = self.client.conversations_info(channel=channel_id)
            self._handle_response(response)
            channel = response["channel"]
            logger.debug(f"Channel info: {channel['name']} ({channel['id']})")
            # Update cache
            self._channel_name_to_id[channel['name']] = channel['id']
            self._save_cache()
            return channel
        except SlackApiError as e:
            logger.error(f"Error getting channel info: {str(e)}")
            raise

    def rename_channel(self, channel_id: str, new_name: str) -> dict:
        """Rename a channel."""
        try:
            logger.info(f"Renaming channel {channel_id} to: {new_name}")
            response = self.client.conversations_rename(
                channel=channel_id,
                name=new_name
            )
            self._handle_response(response)
            channel = response["channel"]
            # Update cache with new name
            if channel['name'] != new_name:
                # Remove old name from cache if it changed
                old_name = next((name for name, id in self._channel_name_to_id.items() if id == channel_id), None)
                if old_name:
                    logger.debug(f"Removing old channel name from cache: {old_name}")
                    del self._channel_name_to_id[old_name]
            self._channel_name_to_id[channel['name']] = channel['id']
            self._save_cache()
            logger.info(f"Channel renamed: {channel['name']} ({channel['id']})")
            return channel
        except SlackApiError as e:
            logger.error(f"Error renaming channel: {str(e)}")
            raise