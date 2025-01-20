import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from . import add_proxy_arguments, get_proxy_dict

def add_arguments(parser):
    """
    Define the command-line arguments for Twilio API key testing.
    """
    parser.add_argument('account_sid', type=str, help='Twilio Account SID')
    parser.add_argument('auth_token', type=str, help='Twilio Auth Token')
    add_proxy_arguments(parser)

def test_credentials(args):
    """
    Test Twilio credentials by making a request to the Twilio API to retrieve account information.
    Returns True if credentials are valid, False otherwise.
    """
    try:
        # Get proxy configuration if specified
        proxies = get_proxy_dict(args)

        # Twilio API base URL
        twilio_base_url = f"https://api.twilio.com/2010-04-01/Accounts/{args.account_sid}.json"

        # Make the request with basic authentication (Account SID and Auth Token)
        response = requests.get(
            twilio_base_url,
            auth=HTTPBasicAuth(args.account_sid, args.auth_token),
            proxies=proxies,
            verify=not args.no_verify  # Disable SSL verification if --no-verify is set
        )

        # Raise an error for bad responses
        response.raise_for_status()

        # Parse the JSON response
        account_info = response.json()

        # Output account details
        print("Credentials are valid! Here are the account details:")
        print(f"Account SID: {account_info['sid']}")
        print(f"Friendly Name: {account_info['friendly_name']}")
        print(f"Account Status: {account_info['status']}")
        print(f"Account Type: {account_info['type']}")
        
        return True

    except HTTPError as http_err:
        if http_err.response.status_code == 401:
            print("Invalid Twilio credentials provided.")
        else:
            print(f"HTTP error occurred: {http_err}")
        return False
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return False
