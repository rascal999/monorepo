# Generated Mangopay API Tests

This directory contains pytest files generated from the Mangopay API Postman collection.

## Structure

- `conftest.py`: Shared fixtures including:
  - Environment variables (ENV_URL, CLIENT_ID, API_KEY)
  - Random data generators (email, names, addresses)
  - User creation fixtures that provide IDs for dependent tests

- `test_users.py`: Test functions for user-related endpoints:
  ```
  test_update_natural_user_owner  # Uses user_natural_owner fixture
  test_update_legal_user         # Uses user_legal_owner fixture
  test_list_users               # Lists all users
  test_view_user               # Uses user_legal_owner fixture
  test_view_user_emoney        # Uses user_natural_owner fixture
  ```

  Resource creation is handled by fixtures in conftest.py:
  ```
  user_natural_owner  # Creates and provides natural user ID
  user_legal_owner   # Creates and provides legal user ID
  ```

## Environment Setup

The tests use python-dotenv to load environment variables from the `.env` file in this directory. Required variables:

```
# API Configuration
ENV_URL=https://api.sandbox.mangopay.com

# OAuth Authentication
BASIC_AUTH_USERNAME=your_client_id  # Your Mangopay Client ID
BASIC_AUTH_PASSWORD=your_api_key    # Your Mangopay API Key
OAUTH_TOKEN_URL=https://api.sandbox.mangopay.com/oauth/token
OAUTH_SCOPE=read write              # Space-separated list of required scopes

# SSL Configuration
TLS_VERIFY=false  # Set to false if you have SSL certificate issues
```

Replace the authentication values with your Mangopay API credentials. The OAuth configuration is used to obtain access tokens for API requests. If you encounter SSL certificate verification errors, ensure TLS_VERIFY is set to false.

## Running Tests

Run all tests:
```bash
pytest
```

Run specific test:
```bash
pytest test_users.py::test_view_user
```

Show dependencies for a test:
```bash
pytest test_users.py::test_view_user --dry-run
```

Example dry-run output:
```
Dependency chain for: test_view_user
==================================================
test_create_legal_user_owner -> uses:
  - client_id (environment)
  - env_url (environment)
  - random_company_name (fixture)
  - random_email (fixture)
  - random_first_name (fixture)
  - random_int (fixture)
  - random_last_name (fixture)
  - random_street_address (fixture)
  - random_street_name (fixture)
test_create_legal_user_owner -> provides:
  - user_legal_owner (fixture)
  test_view_user -> uses:
    - client_id (environment)
    - env_url (environment)
    - user_legal_owner (fixture)
```

## Test Dependencies

Dependencies are managed through pytest fixtures:
- Resource creation is handled by fixtures in conftest.py
- Environment variables are provided through session-scoped fixtures
- Random data generators create unique values for each test run
- Test functions use fixtures to access required resources

## Generated From

- Collection: mgp-sample.json
- Dependencies: mgp-sample.yml
