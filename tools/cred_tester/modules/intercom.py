import requests
from requests.exceptions import HTTPError
from . import add_proxy_arguments, get_proxy_dict

def add_arguments(parser):
    """
    Define the command-line arguments for Intercom API key testing.
    """
    parser.add_argument('access_token', type=str, help='Intercom Access Token')
    add_proxy_arguments(parser)

def test_credentials(args):
    """
    Test Intercom API credentials by making a request to the Intercom API.
    Returns True if credentials are valid, False otherwise.
    """
    try:
        # Get proxy configuration if specified
        proxies = get_proxy_dict(args)

        # Intercom API base URL
        base_url = "https://api.intercom.io/me"
        
        # Set up the headers with the access token
        headers = {
            'Authorization': f'Bearer {args.access_token}',
            'Accept': 'application/json'
        }

        # Make a request to retrieve user details
        response = requests.get(
            base_url,
            headers=headers,
            proxies=proxies,
            verify=not args.no_verify  # Disable SSL verification if --no-verify is set
        )

        # Raise an error for bad responses
        response.raise_for_status()

        # Parse the JSON response
        user_info = response.json()

        # Print out useful user information (adjust based on the actual API response fields)
        user_type = user_info.get('type', 'N/A')
        user_id = user_info.get('id', 'N/A')
        email = user_info.get('email', 'N/A')

        # Output user details
        print(f"Credentials are valid! Here are the user details:")
        print(f"User Type: {user_type}")
        print(f"User ID: {user_id}")
        print(f"Email: {email}")
        
        return True

    except HTTPError as http_err:
        if http_err.response.status_code == 401:
            print("Error: Invalid Intercom access token")
        else:
            print(f"HTTP error occurred: {http_err}")
        return False
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return False
