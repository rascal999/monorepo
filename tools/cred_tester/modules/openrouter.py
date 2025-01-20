import requests
from . import add_proxy_arguments, get_proxy_dict

def add_arguments(parser):
    """
    Define the command-line arguments for OpenRouter credential testing.
    This function is called by the main script.
    """
    parser.add_argument('api_key', type=str, help='OpenRouter API Key')
    add_proxy_arguments(parser)

def test_credentials(args):
    """
    Test OpenRouter credentials by making a simple API call.
    This function is called by the main script.
    Returns True if credentials are valid, False otherwise.
    """
    try:
        # Get proxy configuration if specified
        proxies = get_proxy_dict(args)
        
        # Set up the headers with the API key
        headers = {
            'Authorization': f'Bearer {args.api_key}',
            'HTTP-Referer': 'https://github.com/mangopay/appsec/pocs/cred_tester',  # Required by OpenRouter
            'Content-Type': 'application/json'
        }

        # Make a test request to validate the API key
        test_data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "test"}]
        }
        
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=test_data,
            proxies=proxies,
            verify=not args.no_verify
        )

        # Check if the request was successful
        response.raise_for_status()

        # Now that we know the key is valid, get the models list
        models_response = requests.get(
            'https://openrouter.ai/api/v1/models',
            headers=headers,
            proxies=proxies,
            verify=not args.no_verify
        )
        
        models_response.raise_for_status()
        data = models_response.json()
        
        print("OpenRouter credentials are valid! Available models:")
        models = data.get('data', [])
        for model in models:
            model_id = model.get('id', 'Unknown')
            model_name = model.get('name', model_id)
            context_length = model.get('context_length', 'Unknown context length')
            print(f"- {model_id}: {model_name} (Max context: {context_length})")
        
        return True

    except requests.exceptions.HTTPError as e:
        if e.response.status_code in [401, 403]:
            print("Invalid OpenRouter API key.")
        else:
            print(f"HTTP error occurred: {e.response.text}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while testing the credentials: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
