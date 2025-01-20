import urllib3
from urllib3.exceptions import InsecureRequestWarning
import json
from datetime import datetime
import os
import base64
from . import add_proxy_arguments, get_proxy_dict

# Suppress insecure request warnings when --no-verify is used
urllib3.disable_warnings(InsecureRequestWarning)

def add_arguments(parser):
    """
    Define the command-line arguments for Mangopay API testing.
    """
    parser.add_argument('client_id', type=str, help='Mangopay Client ID')
    parser.add_argument('api_key', type=str, help='Mangopay API Key')
    parser.add_argument('--sandbox', action='store_true', help='Use Sandbox environment')
    add_proxy_arguments(parser)

def test_credentials(args):
    """
    Test Mangopay API credentials by making a direct request to the Mangopay API.
    Returns True if credentials are valid, False otherwise.
    """
    try:
        # Get proxy configuration if specified
        proxies = get_proxy_dict(args)
        if proxies:
            print(f"Using proxy configuration: {proxies}")
            proxy_url = proxies.get('https') or proxies.get('http')
            if proxy_url:
                # Create a proxy manager
                http = urllib3.ProxyManager(
                    proxy_url,
                    cert_reqs='CERT_NONE' if args.no_verify else 'CERT_REQUIRED',
                    retries=False
                )
        else:
            # Create a pool manager for direct connections
            http = urllib3.PoolManager(
                cert_reqs='CERT_NONE' if args.no_verify else 'CERT_REQUIRED',
                retries=False
            )

        # Set the base URL based on environment
        base_url = 'https://api.sandbox.mangopay.com' if args.sandbox else 'https://api.mangopay.com'
        
        # First, get the OAuth token
        oauth_url = f"{base_url}/oauth/token"
        auth_token = base64.b64encode(f"{args.client_id}:{args.api_key}".encode('ascii')).decode('ascii')
        
        print(f"Getting OAuth token from: {oauth_url}")
        
        # Make OAuth token request
        oauth_response = http.request(
            'POST',
            oauth_url,
            headers={
                'Authorization': f'Basic {auth_token}',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'cred_tester/1.0'
            },
            fields={
                'grant_type': 'client_credentials'
            }
        )

        print(f"OAuth Response Status: {oauth_response.status}")
        print(f"OAuth Response Headers: {dict(oauth_response.headers)}")
        
        # Check OAuth response
        if oauth_response.status != 200:
            print("Invalid Mangopay credentials provided.")
            print(f"Response content: {oauth_response.data.decode('utf-8')}")
            return False
        
        # Get the access token
        token_data = json.loads(oauth_response.data.decode('utf-8'))
        access_token = token_data.get('access_token')
        
        if not access_token:
            print("No access token in OAuth response")
            return False

        print("Successfully obtained OAuth token")

        # Now use the token to get client info
        client_url = f"{base_url}/v2.01/{args.client_id}/clients/"
        
        print(f"Getting client info from: {client_url}")

        # Make the client info request with bearer token
        response = http.request(
            'GET',
            client_url,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'User-Agent': 'cred_tester/1.0'
            }
        )

        print(f"Client Info Response Status: {response.status}")
        print(f"Client Info Response Headers: {dict(response.headers)}")

        # Check response status
        if response.status != 200:
            print(f"API request failed with status {response.status}")
            print(f"Response content: {response.data.decode('utf-8')}")
            return False

        # Parse the JSON response
        client_info = json.loads(response.data.decode('utf-8'))

        # Format creation date
        created = datetime.fromtimestamp(client_info.get('CreationDate', 0)).strftime('%Y-%m-%d %H:%M:%S') if client_info.get('CreationDate') else 'N/A'

        # Output client details
        print(f"\nCredentials are valid! Here are the account details:")
        print(f"Client ID: {client_info.get('Id', 'N/A')}")
        print(f"Client Name: {client_info.get('Name', 'N/A')}")
        print(f"Primary Contact Email: {client_info.get('Email', 'N/A')}")
        print(f"Primary Contact First Name: {client_info.get('ContactFirstName', 'N/A')}")
        print(f"Primary Contact Last Name: {client_info.get('ContactLastName', 'N/A')}")
        print(f"Platform Type: {client_info.get('PlatformType', 'N/A')}")
        print(f"Platform Description: {client_info.get('PlatformDescription', 'N/A')}")
        print(f"Created: {created}")
        print(f"Environment: {'Sandbox' if args.sandbox else 'Production'}")

        headquarters = client_info.get('HeadquartersAddress', {})
        if headquarters:
            print(f"Headquarters: {headquarters.get('AddressLine1', '')}, {headquarters.get('City', '')}, {headquarters.get('Country', '')}")

        return True

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False
