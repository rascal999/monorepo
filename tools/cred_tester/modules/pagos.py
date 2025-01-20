import requests
from requests.exceptions import HTTPError
from . import add_proxy_arguments, get_proxy_dict

def add_arguments(parser):
    """
    Define the command-line arguments for Pagos API key testing.
    """
    parser.add_argument('api_key', type=str, help='Pagos API Key')
    add_proxy_arguments(parser)

def test_credentials(args):
    """
    Test Pagos API credentials by making a simple request to the Pagos API.
    Returns True if credentials are valid, False otherwise.
    """
    try:
        # Get proxy configuration if specified
        proxies = get_proxy_dict(args)

        # Pagos API base URL
        base_url = "https://api.pagos.ai/v1"
        
        # Set up the headers with the API key
        headers = {
            'Authorization': f'Bearer {args.api_key}',
            'Content-Type': 'application/json'
        }

        # Make a request to retrieve account details
        response = requests.get(
            f"{base_url}/account",
            headers=headers,
            proxies=proxies,
            verify=not args.no_verify  # Disable SSL verification if --no-verify is set
        )

        # Raise an error for bad responses
        response.raise_for_status()

        # Parse the JSON response
        account_info = response.json()

        # Print out useful account information (adjust based on the actual API response fields)
        account_name = account_info.get('name', 'N/A')
        email = account_info.get('email', 'N/A')
        account_id = account_info.get('id', 'N/A')

        # Output account details
        print(f"Credentials are valid! Here are the account details:")
        print(f"Account Name: {account_name}")
        print(f"Email: {email}")
        print(f"Account ID: {account_id}")
        
        return True

    except HTTPError as http_err:
        if http_err.response.status_code == 401:
            print("Error: Invalid Pagos API key")
        else:
            print(f"HTTP error occurred: {http_err}")
        return False
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return False
