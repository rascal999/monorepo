import logging
import requests

logger = logging.getLogger('orchai.bot')

class RocketChatService:
    def __init__(self, rocket_url, auth_token, user_id):
        self.rocket_url = rocket_url.rstrip('/') + '/api/v1/'
        self.headers = {
            "X-Auth-Token": auth_token,
            "X-User-Id": user_id,
        }

    def channels_info(self, channel):
        """Get channel information"""
        response = requests.get(
            f"{self.rocket_url}channels.info",
            headers=self.headers,
            params={"roomName": channel}
        )
        return response

    def channels_history(self, room_id):
        """Get channel history"""
        response = requests.get(
            f"{self.rocket_url}channels.history",
            headers=self.headers,
            params={"roomId": room_id}
        )
        return response

    def send_message(self, message, bot_name):
        """Send a message to #general"""
        logger.debug(f"{bot_name} sending message: {message}")
        try:
            payload = {
                "channel": "#general",
                "text": message
            }
            response = requests.post(
                f"{self.rocket_url}chat.postMessage",
                headers=self.headers,
                json=payload
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                raise Exception(f"Failed to send message: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise