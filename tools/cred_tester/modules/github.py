import requests
from requests.exceptions import HTTPError
from . import add_proxy_arguments, get_proxy_dict

def add_arguments(parser):
    """
    Define the command-line arguments for GitHub token testing.
    """
    parser.add_argument('token', type=str, help='GitHub Personal Access Token')
    add_proxy_arguments(parser)

def test_credentials(args):
    """
    Test GitHub token by making a request to the GitHub API to retrieve user information.
    Returns True if credentials are valid, False otherwise.
    """
    try:
        # Get proxy configuration if specified
        proxies = get_proxy_dict(args)

        # GitHub API base URL
        base_url = "https://api.github.com"
        
        # Set up the headers with the token
        headers = {
            'Authorization': f'token {args.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        # Make a request to get authenticated user information
        response = requests.get(
            f"{base_url}/user",
            headers=headers,
            proxies=proxies,
            verify=not args.no_verify  # Disable SSL verification if --no-verify is set
        )

        # Raise an error for bad responses
        response.raise_for_status()

        # Parse the JSON response
        user_info = response.json()

        # Print out user information
        print("Credentials are valid! Here are the user details:")
        print(f"Login: {user_info.get('login', 'N/A')}")
        print(f"Name: {user_info.get('name', 'N/A')}")
        print(f"Email: {user_info.get('email', 'N/A')}")
        print(f"Company: {user_info.get('company', 'N/A')}")
        print(f"Location: {user_info.get('location', 'N/A')}")
        print(f"Public Repos: {user_info.get('public_repos', 'N/A')}")
        print(f"Account Created: {user_info.get('created_at', 'N/A')}")

        # Get user's scopes
        scopes = response.headers.get('X-OAuth-Scopes', 'N/A')
        print(f"\nToken Scopes: {scopes}")
        
        return True

    except HTTPError as http_err:
        if http_err.response.status_code == 401:
            print("Error: Invalid or expired GitHub token")
        else:
            print(f"HTTP error occurred: {http_err}")
        return False
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return False
