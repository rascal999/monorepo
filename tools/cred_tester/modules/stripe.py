import stripe
import requests
from stripe.error import AuthenticationError, APIConnectionError
from datetime import datetime
from . import add_proxy_arguments, get_proxy_dict

def add_arguments(parser):
    """
    Define the command-line arguments for Stripe API key testing.
    """
    parser.add_argument('api_key', type=str, help='Stripe Secret API Key')
    add_proxy_arguments(parser)

def test_credentials(args):
    """
    Test Stripe API credentials. This function is called by the main script.
    Returns True if credentials are valid, False otherwise.
    """
    try:
        # Set the Stripe API key
        stripe.api_key = args.api_key

        # Configure proxy if specified
        proxies = get_proxy_dict(args)
        if proxies:
            # Stripe uses a single proxy URL, so we prioritize HTTPS proxy
            stripe.proxy = proxies.get('https') or proxies.get('http')

        # Configure SSL verification
        if args.no_verify:
            # Monkey patch the requests Session to disable SSL verification
            original_request = stripe.api_requestor.APIRequestor.request
            def patched_request(self, *args, **kwargs):
                kwargs['verify'] = False
                return original_request(self, *args, **kwargs)
            stripe.api_requestor.APIRequestor.request = patched_request

        # Make a request to retrieve account details
        account = stripe.Account.retrieve()

        # Check and retrieve optional fields
        account_id = account.get('id', 'N/A')
        business_type = account.get('business_type', 'N/A')
        default_currency = account.get('default_currency', 'N/A')
        payouts_enabled = account.get('payouts_enabled', False)
        created = account.get('created', None)
        created_date = datetime.utcfromtimestamp(created).strftime('%Y-%m-%d %H:%M:%S') if created else 'N/A'
        support_phone = account.get('support_phone', 'N/A')
        support_email = account.get('support_email', 'N/A')
        website = account.get('url', 'N/A')
        country = account.get('country', 'N/A')

        # Output account details
        print(f"Credentials are valid! Here are the account details:")
        print(f"Account ID: {account_id}")
        print(f"Business Type: {business_type}")
        print(f"Country: {country}")
        print(f"Default Currency: {default_currency}")
        print(f"Payouts Enabled: {payouts_enabled}")
        print(f"Created: {created_date}")
        print(f"Support Phone: {support_phone}")
        print(f"Support Email: {support_email}")
        print(f"Website: {website}")
        
        return True

    except AuthenticationError:
        print("Invalid Stripe API key provided.")
        return False
    except APIConnectionError:
        print("Failed to connect to Stripe API. Check your network connection.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
