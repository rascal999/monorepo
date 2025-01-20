import requests
from requests.exceptions import HTTPError
from . import add_proxy_arguments, get_proxy_dict

def add_arguments(parser):
    """
    Define the command-line arguments for Basic Auth testing.
    """
    parser.add_argument('username', type=str, help='Username for Basic Auth')
    parser.add_argument('password', type=str, help='Password for Basic Auth')
    parser.add_argument('url', type=str, help='URL to test Basic Auth against')
    add_proxy_arguments(parser)

def test_credentials(args):
    """
    Test Basic Auth credentials by making a request to the specified URL.
    Returns True if credentials are valid, False otherwise.
    """
    try:
        # Get proxy configuration if specified
        proxies = get_proxy_dict(args)

        # Make request with basic auth
        response = requests.get(
            args.url,
            auth=(args.username, args.password),
            headers={'User-Agent': 'CredentialTester/1.0'},
            proxies=proxies,
            verify=not args.no_verify  # Disable SSL verification if --no-verify is set
        )

        # Raise an error for bad responses
        response.raise_for_status()

        # If we get here, the credentials worked
        print("Credentials are valid! Server response details:")
        print(f"Status Code: {response.status_code}")
        print(f"Server: {response.headers.get('Server', 'N/A')}")
        print(f"Content Type: {response.headers.get('Content-Type', 'N/A')}")
        
        # Print authentication related headers if present
        auth_headers = [
            'WWW-Authenticate',
            'Authentication-Info',
            'Authorization'
        ]
        print("\nAuthentication Headers:")
        for header in auth_headers:
            if header in response.headers:
                print(f"{header}: {response.headers[header]}")
        
        return True

    except HTTPError as http_err:
        if http_err.response.status_code == 401:
            print("Error: Invalid credentials - Authentication failed")
        elif http_err.response.status_code == 403:
            print("Error: Valid credentials but access forbidden")
        else:
            print(f"HTTP error occurred: {http_err}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to {args.url}")
        return False
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return False
