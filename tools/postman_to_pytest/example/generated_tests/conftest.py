"""
Pytest configuration and fixtures.
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

def pytest_configure(config):
    """Configure pytest."""
    config.option.dependency_ignore_unknown = True
    print("\n=== Session Start ===")
    print("Initializing dynamic vars store")

def pytest_sessionfinish():
    """Called after whole test run finished."""
    print("\n=== Session End ===")
    print("Final dynamic vars state:", _dynamic_vars_store._vars)

# Load environment variables
load_dotenv()

def pytest_runtest_call(item):
    """Called to execute the test item."""
    print(f"\n=== Before running {item.name} ===")
    print("Dynamic vars state:", _dynamic_vars_store._vars)

@pytest.fixture(scope="session")
def env_vars():
    """Environment variables needed for tests."""
    required_vars = ["ENV_URL", "BASIC_AUTH_USERNAME", "BASIC_AUTH_PASSWORD", "TLS_VERIFY"]
    env_dict = {}
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Required environment variable {var} is not set")
        env_dict[var] = value
    # Map BASIC_AUTH_USERNAME to CLIENT_ID for backward compatibility
    env_dict["CLIENT_ID"] = env_dict["BASIC_AUTH_USERNAME"]
    return env_dict

@pytest.fixture(scope="session")
def faker_vars():
    """Faker variables for generating test data."""
    fake = Faker()
    return {
        "$randomFirstName": fake.first_name(),
        "$randomLastName": fake.last_name(),
        "$randomEmail": fake.email(),
        "$randomStreetAddress": fake.street_address(),
        "$randomStreetName": fake.street_name(),
        "$randomCompanyName": fake.company(),
        "$randomInt": str(fake.random_int(min=1000, max=9999))
    }

@pytest.fixture(scope="session")
def api_session(env_vars):
    """Session with authentication for API requests."""
    session = requests.Session()
    # Set SSL verification based on TLS_VERIFY env var
    verify = env_vars["TLS_VERIFY"].lower() == "true"
    session.verify = verify
    if not verify:
        # Disable warnings for unverified HTTPS requests
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # Use Basic Auth to get bearer token
    auth_url = f"{env_vars['ENV_URL']}/v2.01/oauth/token"
    response = session.post(
        auth_url,
        auth=(env_vars["BASIC_AUTH_USERNAME"], env_vars["BASIC_AUTH_PASSWORD"])
    )
    response.raise_for_status()
    token = response.json()["access_token"]
    session.headers["Authorization"] = f"Bearer {token}"
    return session

class DynamicVarsStore:
    """Store for dynamic variables that persists across test runs."""
    def __init__(self):
        self._vars = {}

    def __getitem__(self, key):
        return self._vars[key]

    def __setitem__(self, key, value):
        self._vars[key] = value

    def __contains__(self, key):
        return key in self._vars

    def __str__(self):
        return str(self._vars)

_dynamic_vars_store = DynamicVarsStore()

@pytest.fixture(scope="session")
def dynamic_vars():
    """Store dynamic variables that are set during test execution."""
    return _dynamic_vars_store
