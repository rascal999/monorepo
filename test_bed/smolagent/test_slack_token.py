#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def test_slack_token(token: str = None) -> None:
    """Test Slack Bot User OAuth Token and its permissions."""
    # Load environment variables from .env file
    load_dotenv()

    if not token:
        token = os.getenv("SLACK_BOT_TOKEN")
        if not token:
            print("Error: No token provided. Please set SLACK_BOT_TOKEN in .env file or pass token as argument.")
            sys.exit(1)

    if not token.startswith("xoxb-"):
        print("Error: Invalid token format. Bot User OAuth Token must start with 'xoxb-'")
        sys.exit(1)

    client = WebClient(token=token)
    tests = {
        "Auth Test": {
            "method": client.auth_test,
            "args": {},
            "scope": "None (basic connection)"
        },
        "List Channels": {
            "method": client.conversations_list,
            "args": {"types": "public_channel", "limit": 1},
            "scope": "channels:read"
        },
        "Channel History": {
            "method": client.conversations_history,
            "args": {"channel": "general", "limit": 1},  # Will be updated with real channel ID
            "scope": "channels:history"
        },
        "User Info": {
            "method": client.users_info,
            "args": {"user": "U0"},  # Will be updated with real user ID
            "scope": "users:read"
        }
    }

    print("\nTesting Slack Bot User OAuth Token...")
    print("-" * 50)

    # First test basic auth
    try:
        auth_info = client.auth_test()
        print(f"✓ Basic Authentication: Success")
        print(f"  • Bot User: {auth_info['user']}")
        print(f"  • Team: {auth_info['team']}")
        print(f"  • Bot ID: {auth_info['user_id']}")
        print("-" * 50)
    except SlackApiError as e:
        print(f"✗ Basic Authentication Failed: {e.response['error']}")
        sys.exit(1)

    # Get a real channel ID for testing
    try:
        channels = client.conversations_list(types="public_channel", limit=1)
        if channels["channels"]:
            channel_id = channels["channels"][0]["id"]
            tests["Channel History"]["args"]["channel"] = channel_id
    except SlackApiError:
        pass  # Will be caught in the main test loop

    # Get a real user ID for testing
    try:
        user_id = auth_info['user_id']
        tests["User Info"]["args"]["user"] = user_id
    except:
        pass  # Will be caught in the main test loop

    # Run all permission tests
    all_passed = True
    for test_name, test_info in tests.items():
        if test_name == "Auth Test":
            continue  # Already tested

        try:
            test_info["method"](**test_info["args"])
            print(f"✓ {test_name}: Success")
            print(f"  • Required scope: {test_info['scope']}")
        except SlackApiError as e:
            all_passed = False
            error = str(e.response['error'])
            print(f"✗ {test_name}: Failed - {error}")
            print(f"  • Missing scope: {test_info['scope']}")
        print("-" * 50)

    if all_passed:
        print("\n✅ All tests passed! Token has all required scopes.")
    else:
        print("\n❌ Some tests failed. Please check the missing scopes above.")
        print("\nRequired scopes for full functionality:")
        print("- channels:history")
        print("- channels:read")
        print("- users:read")
        print("\nNote: Search functionality is not available as it requires Enterprise Grid.")
        print("Use channel history to find messages instead.")
        print("\nAdd these scopes in your Slack App configuration at:")
        print("https://api.slack.com/apps > Your App > OAuth & Permissions > Scopes")

if __name__ == "__main__":
    token = sys.argv[1] if len(sys.argv) > 1 else None
    test_slack_token(token)