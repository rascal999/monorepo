# Pytest Fixtures

## What are Fixtures?
Pytest fixtures are functions that provide a fixed baseline for tests. They initialize test environments, provide test data, or handle any setup/cleanup needed for tests to run properly. Fixtures help avoid code duplication and allow for modular, maintainable tests.

## Key Concepts
1. **Reusability**: Fixtures can be reused across multiple tests
2. **Scope**: Fixtures can have different scopes (function, class, module, session)
3. **Dependencies**: Fixtures can depend on other fixtures
4. **Automatic Cleanup**: Fixtures can handle both setup and cleanup

## Examples in Our Context

### 1. Authentication Fixtures
```python
@pytest.fixture
def auth_token():
    """Provide authentication token for API requests"""
    return "Bearer your-token-here"

@pytest.fixture
def api_key():
    """Provide API key for endpoints"""
    return "your-api-key-here"

# Usage in tests
def test_protected_endpoint(auth_token):
    headers = {"Authorization": auth_token}
    response = requests.get("/api/protected", headers=headers)
    assert response.status_code == 200
```

### 2. Request Data Fixtures
```python
@pytest.fixture
def user_data():
    """Provide test user data"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepass123"
    }

# Usage in tests
def test_create_user(user_data):
    response = requests.post("/api/users", json=user_data)
    assert response.status_code == 201
```

### 3. Environment Setup Fixtures
```python
@pytest.fixture(scope="session")
def base_url():
    """Provide base URL for API endpoints"""
    return "http://api.example.com"

@pytest.fixture(scope="session")
def api_client(base_url):
    """Configure API client with base URL"""
    return APIClient(base_url=base_url)
```

### 4. Database Fixtures
```python
@pytest.fixture
def test_database():
    """Set up test database"""
    # Setup
    db = create_test_database()
    yield db
    # Cleanup
    db.cleanup()
```

## How We'll Use Fixtures in the Converter

1. **Converting Postman Variables**
```python
# Postman environment variables become fixtures
@pytest.fixture
def environment_variables():
    return {
        "base_url": "http://api.example.com",
        "api_key": "your-api-key",
        "user_id": "123"
    }
```

2. **Request Prerequisites**
```python
@pytest.fixture
def auth_headers(auth_token):
    """Common headers needed for requests"""
    return {
        "Authorization": auth_token,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
```

3. **Test Data Management**
```python
@pytest.fixture
def test_data():
    """Load test data from external files"""
    with open("test_data.json") as f:
        return json.load(f)
```

4. **Dynamic Data Generation**
```python
@pytest.fixture
def unique_user():
    """Generate unique user data for tests"""
    return {
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"user_{uuid.uuid4().hex[:8]}@example.com"
    }
```

## Benefits in Our Context

1. **Maintainability**
   - Environment variables in one place
   - Easy to update test data
   - Centralized authentication management

2. **Reusability**
   - Common setup shared across tests
   - Consistent test data
   - Standardized configurations

3. **Cleanup**
   - Automatic resource cleanup
   - Test isolation
   - Database state management

4. **Flexibility**
   - Easy to modify for different environments
   - Support for different authentication methods
   - Configurable test data

## Implementation Strategy

1. **Variable Conversion**
   - Convert Postman environment variables to pytest fixtures
   - Handle different variable scopes appropriately
   - Support dynamic variable generation

2. **Authentication Handling**
   - Create fixtures for different auth types
   - Support token refresh mechanisms
   - Handle API key rotation

3. **Data Management**
   - Convert Postman test data to fixtures
   - Support external data files
   - Handle dynamic data generation

4. **Configuration**
   - Environment-specific settings
   - Test-specific configurations
   - Reusable request configurations
