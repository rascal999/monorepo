"""
Test fixtures for API testing.
"""
import os
import pytest
import requests
import urllib3
import warnings
from faker import Faker
from dotenv import load_dotenv

# Filter out InsecureRequestWarning
warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

@pytest.fixture(scope="session")
def env_vars():
    """Environment variables needed for tests."""
    print("\n=== Loading environment variables ===")
    # Load all environment variables
    env_dict = dict(os.environ)
    print("Loaded all environment variables")
    
    # Validate required variables
    required_vars = ["ENV_URL", "BASIC_AUTH_USERNAME", "BASIC_AUTH_PASSWORD", "TLS_VERIFY"]
    for var in required_vars:
        if var not in env_dict:
            print(f"Missing required environment variable: {var}")
            raise ValueError(f"Required environment variable {var} is not set")
        print(f"Validated {var}")
    
    # Map BASIC_AUTH_USERNAME to CLIENT_ID for backward compatibility
    env_dict["CLIENT_ID"] = env_dict["BASIC_AUTH_USERNAME"]
    print("Environment variables loaded successfully")
    return env_dict

@pytest.fixture(scope="session")
def faker_vars():
    """Faker variables for generating test data."""
    print("\n=== Generating faker variables ===")
    fake = Faker()
    vars_dict = {
        "$randomFirstName": fake.first_name(),
        "$randomLastName": fake.last_name(),
        "$randomFullName": f"{fake.first_name()} {fake.last_name()}",
        "$randomEmail": fake.email(),
        "$randomStreetAddress": fake.street_address(),
        "$randomStreetName": fake.street_name(),
        "$randomCompanyName": fake.company(),
        "$randomInt": str(fake.random_int(min=1000, max=9999))
    }
    print("Generated variables:", vars_dict)
    return vars_dict

@pytest.fixture(scope="session")
def api_session(env_vars):
    """Session with authentication for API requests."""
    print("\n=== Creating API session ===")
    session = requests.Session()
    
    # Configure SSL verification
    verify = env_vars["TLS_VERIFY"].lower() == "true"
    session.verify = verify
    print(f"SSL verification: {verify}")
    
    if not verify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Get bearer token
    auth_url = f"{env_vars['ENV_URL']}/v2.01/oauth/token"
    print(f"Getting bearer token from: {auth_url}")
    try:
        response = session.post(
            auth_url,
            auth=(env_vars["BASIC_AUTH_USERNAME"], env_vars["BASIC_AUTH_PASSWORD"])
        )
        response.raise_for_status()
        token = response.json()["access_token"]
        session.headers["Authorization"] = f"Bearer {token}"
        print("Bearer token obtained successfully")
    except Exception as e:
        print(f"Failed to get bearer token: {e}")
        raise
    
    return session
