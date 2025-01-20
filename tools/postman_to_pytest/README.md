# Postman to Pytest Converter

A tool to convert Postman collections to Pytest test cases, with support for dependency-based test ordering.

## Features

- Converts Postman collections (JSON) to Pytest test cases
- Supports dependency graph configuration (YAML)
- Handles environment variables and dynamic variables
- Maintains test order based on dependencies
- Converts Postman test scripts to Pytest assertions

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Place your Postman collection JSON file in the project directory
2. Create a YAML file defining the dependencies between endpoints
3. Run the converter:

```bash
python -m postman2pytest <collection_file.json> <dependencies.yml>
```

The generated test files will be created in the `generated_tests` directory.

## Input Files

### Postman Collection (JSON)
- API endpoint definitions
- Request methods, headers, and bodies
- Test scripts and environment variables
- Authentication configuration

### Dependency Graph (YAML)
- Endpoint dependencies
- Variable usage and relationships
- Test execution order requirements

## Generated Tests

The converter creates a directory structure that mirrors your Postman collection:

```
generated_tests/
├── __init__.py
├── conftest.py
├── .env
└── all_mangopay_endpoints/
    ├── __init__.py
    └── users/
        ├── __init__.py
        ├── test_create_natural_user_owner.py
        ├── test_create_natural_user_payer.py
        ├── test_create_legal_user_owner.py
        ├── test_create_legal_user_payer.py
        ├── test_update_natural_user_owner.py
        ├── test_update_legal_user.py
        ├── test_view_user.py
        ├── test_view_user_emoney.py
        └── test_list_users.py
```

Each test file contains:
- Clear docstrings describing the test purpose
- Proper pytest fixtures for session management
- Environment variable handling
- Dynamic variable management
- Dependency markers for test ordering

## Test Dependencies

Tests use `pytest-dependency` to maintain proper execution order:

```python
@pytest.mark.dependency(name="test_create_natural_user_owner")
def test_create_natural_user_owner(api_session, env_vars, faker_vars, dynamic_vars):
    """Test creating a natural user with owner category."""
    ...
```

Dependencies are automatically handled based on:
- Variable usage (tests that set variables other tests need)
- Explicit dependencies defined in the YAML configuration
- API endpoint relationships

## Environment Setup

1. Copy the `.env.sample` template to create your `.env` file:
```bash
cp .env.sample .env
```

2. Update the `.env` file with your values. The file includes configuration for:
   - Custom variables (e.g., CLIENT_ID)
   - OAuth authentication flow
   - Proxy configuration
   - SSL/TLS settings
   - Environment selection
   - Logging preferences

See `.env.sample` for the complete list of available configuration options and their descriptions.

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Example

Using the example Mangopay API collection:

1. Input files:
   - `example/mgp-sample.json`: Mangopay API collection with user endpoints
   - `example/mgp-sample.yml`: Dependencies between user operations

2. Generate tests:
```bash
python -m postman2pytest example/mgp-sample.json example/mgp-sample.yml --output-dir example/generated_tests
```

3. Run tests:
```bash
pytest example/generated_tests -v
```

The generated tests will:
- Follow the same structure as the Postman collection
- Maintain dependencies between operations (e.g., create user before update)
- Handle environment variables and dynamic data
- Include proper assertions from Postman tests
