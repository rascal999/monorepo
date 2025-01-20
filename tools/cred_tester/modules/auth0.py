import requests
from requests.exceptions import HTTPError
from . import add_proxy_arguments, get_proxy_dict

def add_arguments(parser):
    """
    Define the command-line arguments for Auth0 API key testing.
    """
    parser.add_argument('domain', type=str, help='Auth0 Domain (e.g., your-domain.auth0.com)')
    parser.add_argument('client_id', type=str, help='Auth0 Client ID')
    parser.add_argument('client_secret', type=str, help='Auth0 Client Secret')
    parser.add_argument('audience', type=str, help='Auth0 API Audience (e.g., https://your-domain.auth0.com/api/v2/)')
    add_proxy_arguments(parser)

def test_credentials(args):
    """
    Test Auth0 credentials by generating a Management API token and retrieving information.
    Returns True if credentials are valid, False otherwise.
    """
    try:
        # Get proxy configuration if specified
        proxies = get_proxy_dict(args)

        # Auth0 OAuth token endpoint
        token_url = f"https://{args.domain}/oauth/token"
        
        # Set up the data for generating the access token
        token_data = {
            'client_id': args.client_id,
            'client_secret': args.client_secret,
            'audience': args.audience,
            'grant_type': 'client_credentials'
        }

        # Request the access token
        response = requests.post(
            token_url,
            json=token_data,
            proxies=proxies,
            verify=not args.no_verify  # Disable SSL verification if --no-verify is set
        )
        
        # Raise an error for bad responses
        response.raise_for_status()

        # Parse the JSON response to get the access token
        token_info = response.json()
        access_token = token_info.get('access_token', None)
        
        if not access_token:
            print("Failed to retrieve access token")
            return False

        print("Auth0 access token retrieved successfully!")

        # Now use the access token to retrieve tenant information or other details
        management_api_url = f"https://{args.domain}/api/v2/tenants/settings"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Make a request to retrieve tenant settings
        tenant_response = requests.get(
            management_api_url,
            headers=headers,
            proxies=proxies,
            verify=not args.no_verify  # Disable SSL verification if --no-verify is set
        )
        tenant_response.raise_for_status()

        # Print tenant information
        tenant_info = tenant_response.json()
        print(f"Tenant Information: {tenant_info}")
        return True

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return False
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return False
