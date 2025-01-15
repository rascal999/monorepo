# Test Dependencies and Variables

## Test Dependencies

### Basic Test Dependencies
```python
# test_create_user.py
import pytest

@pytest.mark.dependency()
def test_create_user(auth_token):
    """Create a new user"""
    # Test implementation
    assert response.status_code == 201
    return response.json()["id"]

# test_get_user.py
@pytest.mark.dependency(depends=["test_create_user"])
def test_get_user(auth_token, user_id):
    """Get user details - depends on user creation"""
    # Test implementation
    assert response.status_code == 200
```

### Complex Dependency Chains
```python
# test_wallet_operations.py
@pytest.mark.dependency()
def test_create_user(auth_token):
    """First in dependency chain - create user"""
    # Implementation
    return user_id

@pytest.mark.dependency(depends=["test_create_user"])
def test_create_wallet(auth_token, user_id):
    """Second in chain - create wallet for user"""
    # Implementation
    return wallet_id

@pytest.mark.dependency(depends=["test_create_wallet"])
def test_add_funds(auth_token, wallet_id):
    """Third in chain - add funds to wallet"""
    # Implementation
    return transaction_id

@pytest.mark.dependency(depends=["test_add_funds"])
def test_check_balance(auth_token, wallet_id, transaction_id):
    """Final test - verify balance after fund addition"""
    # Implementation
```

### Dependency Groups
```python
# test_user_group.py
@pytest.mark.dependency(group="user_setup")
def test_create_user():
    # Implementation

@pytest.mark.dependency(group="user_setup")
def test_update_user_profile():
    # Implementation

# test_wallet_group.py
@pytest.mark.dependency(depends=["group:user_setup"])
def test_create_wallet():
    # Implementation
```

### Error Handling in Dependencies
```python
@pytest.mark.dependency()
def test_create_resource(auth_token):
    try:
        # Create resource
        assert response.status_code == 201
        return resource_id
    except AssertionError:
        pytest.skip("Resource creation failed")

@pytest.mark.dependency(depends=["test_create_resource"])
def test_use_resource(auth_token, resource_id):
    # This test will be skipped if resource creation failed
    # Implementation
```

## Variable Dependencies

### 1. Static Variables
```python
@pytest.fixture(scope="module")
def api_version():
    """Static API version"""
    return "v1"

@pytest.fixture(scope="module")
def base_url(api_version):
    """URL with API version"""
    return f"https://api.example.com/{api_version}"
```

### 2. Dynamic Variables (from responses)
```python
@pytest.fixture(scope="module")
def user_id(auth_token):
    """User ID from creation response"""
    response = create_user(auth_token)
    return response.json()["id"]

@pytest.fixture(scope="module")
def wallet_id(auth_token, user_id):
    """Wallet ID fixture depending on user creation"""
    response = create_wallet(auth_token, user_id)
    return response.json()["wallet_id"]
```

### 3. Environment Variables
```python
@pytest.fixture(scope="session")
def api_key():
    """API key from environment"""
    return os.getenv("API_KEY")

@pytest.fixture(scope="session")
def env_config():
    """Environment configuration"""
    return {
        "url": os.getenv("API_URL"),
        "timeout": int(os.getenv("REQUEST_TIMEOUT", "30")),
        "verify_ssl": os.getenv("VERIFY_SSL", "true").lower() == "true"
    }
```

## Test Execution Flow

### 1. Fixture Initialization
1. Session fixtures initialized:
   - env_url
   - auth_token
   - api_client
2. Module fixtures created:
   - user_id
   - test_data
3. Function fixtures created per test

### 2. Test Execution Order
1. Independent tests run first
2. Dependent tests follow based on:
   - Direct dependencies
   - Group dependencies
   - Variable dependencies

### 3. Resource Cleanup
1. Function-scoped fixtures cleaned up after each test
2. Module-scoped fixtures cleaned up after module
3. Session-scoped fixtures cleaned up at end
4. Cleanup occurs in reverse dependency order
