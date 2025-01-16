import os
import pytest
from faker import Faker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Faker for handling Postman's dynamic variables
fake = Faker()

@pytest.fixture(scope="session")
def env_vars():
    """Provide environment variables needed for tests."""
    required_vars = [
        'ENV_URL',
        'CLIENT_ID',
        'API_KEY'
    ]
    
    # Map BASIC_AUTH_PASSWORD to API_KEY if needed
    if not os.getenv('API_KEY') and os.getenv('BASIC_AUTH_PASSWORD'):
        os.environ['API_KEY'] = os.getenv('BASIC_AUTH_PASSWORD')

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        pytest.fail(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return {var: os.getenv(var) for var in required_vars}

@pytest.fixture(scope="session")
def faker_vars():
    """Provide Faker-based variables to simulate Postman's dynamic variables."""
    return {
        "$randomEmail": fake.email(),
        "$randomFirstName": fake.first_name(),
        "$randomLastName": fake.last_name(),
        "$randomStreetAddress": fake.street_address(),
        "$randomStreetName": fake.street_name(),
        "$randomCompanyName": fake.company(),
        "$randomInt": str(fake.random_int(min=1000, max=9999))
    }

@pytest.fixture(scope="session")
def api_session(env_vars):
    """Create and configure a requests session for API calls."""
    import requests
    from requests.auth import HTTPBasicAuth
    
    session = requests.Session()

    # Configure session with proxy and SSL settings from .env
    if os.getenv('HTTPS_PROXY'):
        session.proxies = {
            'https': os.getenv('HTTPS_PROXY'),
            'http': os.getenv('HTTP_PROXY', '')
        }
    
    # Disable SSL verification if specified in .env
    verify_ssl = os.getenv('TLS_VERIFY', 'true').lower() != 'false'
    
    # Configure OAuth2 authentication
    auth_url = f"{env_vars['ENV_URL']}/v2.01/oauth/token"
    auth_response = session.post(
        auth_url,
        auth=HTTPBasicAuth(env_vars['CLIENT_ID'], env_vars['API_KEY']),
        data={'grant_type': 'client_credentials'},
        verify=verify_ssl
    )
    auth_response.raise_for_status()
    
    # Set the bearer token and SSL verification for all subsequent requests
    token = auth_response.json()['access_token']
    session.headers.update({'Authorization': f'Bearer {token}'})
    session.verify = verify_ssl
    
    yield session
    
    session.close()

@pytest.fixture(scope="module")
def dynamic_vars():
    """Store dynamic variables that are set and used between tests."""
    return {}
