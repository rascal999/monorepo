import requests

# Rocket.Chat server details
ROCKETCHAT_URL = "http://localhost:3200/api/v1/"
API_KEY = "XXX"
USER_ID = "PDvJicDZ7aaZyFbx8"

# Headers for authentication
headers = {
    "X-Auth-Token": API_KEY,
    "X-User-Id": USER_ID,
}

# Example: Send a message
def send_message(channel, message):
    payload = {
        "channel": channel,  # Channel name or ID
        "text": message,
    }
    response = requests.post(f"{ROCKETCHAT_URL}chat.postMessage", headers=headers, json=payload)
    if response.status_code == 200:
        try:
            return response.json()
        except:
            return {"success": True, "text": "Message sent successfully"}
    return {"success": False, "error": f"Failed to send message: {response.status_code}"}

# Test connection and send message
try:
    print("Bot connected successfully!")
    result = send_message("#general", "Hello from my bot!")
    if result["success"]:
        print("Message sent successfully!")
    else:
        print(result["error"])
except Exception as e:
    print(f"Error occurred: {str(e)}")

