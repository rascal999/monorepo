import boto3
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from botocore.config import Config
from . import add_proxy_arguments, get_proxy_dict

def add_arguments(parser):
    """
    Define the command-line arguments for AWS credential testing.
    This function is called by the main script.
    """
    parser.add_argument('access_key', type=str, help='AWS Access Key ID')
    parser.add_argument('secret_key', type=str, help='AWS Secret Access Key')
    parser.add_argument('--session_token', type=str, help='AWS Session Token (Optional)', default=None)
    add_proxy_arguments(parser)

def test_credentials(args):
    """
    Test AWS credentials. This function is called by the main script.
    Returns True if credentials are valid, False otherwise.
    """
    try:
        # Get proxy configuration if specified
        proxies = get_proxy_dict(args)
        
        # Configure proxy settings and SSL verification for boto3
        config_args = {
            'verify': not args.no_verify  # Disable SSL verification if --no-verify is set
        }
        
        if proxies:
            if 'https' in proxies:
                config_args['proxies'] = {'https': proxies['https']}
            elif 'http' in proxies:
                config_args['proxies'] = {'https': proxies['http']}

        # Create a custom configuration with proxy and verification settings
        config = Config(**config_args)

        # Create a session with the provided credentials
        session = boto3.Session(
            aws_access_key_id=args.access_key,
            aws_secret_access_key=args.secret_key,
            aws_session_token=args.session_token  # Optional session token
        )
        
        # Use STS to verify the credentials, with proxy configuration if specified
        sts_client = session.client('sts', config=config)
        response = sts_client.get_caller_identity()
        
        # If the call succeeds, the credentials are valid
        print(f"Credentials are valid! Here are the details:\nAccount: {response['Account']}\nARN: {response['Arn']}\nUser ID: {response['UserId']}")
        return True
    
    except NoCredentialsError:
        print("No AWS credentials were provided.")
        return False
    except PartialCredentialsError:
        print("Partial credentials found. Please provide both Access Key ID and Secret Access Key.")
        return False
    except ClientError as e:
        print(f"Invalid AWS credentials or an error occurred: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
