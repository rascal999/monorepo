# Postman to Pytest Generator

Convert Postman collections to pytest files with proper test dependencies and variable management.

## Features

- Convert Postman collections to pytest test files
- Maintain test dependencies and execution order
- Handle variable sharing between tests via fixtures
- Support both static and dynamic variables
- Mirror Postman collection folder structure
- Exclude specific folders from collection or dependencies
- Target specific endpoints by method/path or Postman name

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd postman-to-pytest

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Usage

### Basic Usage

```bash
postman2pytest \
  --collection input.json \
  --dependencies input.yml \
  --output generated_tests
```

### Target Specific Endpoint

By HTTP method and path:
```bash
postman2pytest \
  --collection input.json \
  --dependencies input.yml \
  --output generated_tests \
  --target "GET /api/users/{{user_id}}"
```

By Postman folder/test name:
```bash
postman2pytest \
  --collection input.json \
  --dependencies input.yml \
  --output generated_tests \
  --name "Users/Get User"
```

### Exclude Folders

```bash
postman2pytest \
  --collection input.json \
  --dependencies input.yml \
  --output generated_tests \
  --exclude-collection-folder auth \
  --exclude-dependency-folder tutorials
```

## Input Files

### Postman Collection (JSON)

The tool accepts Postman Collection v2.1 format. Example:

```json
{
    "info": {
        "name": "Sample API Collection",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "Users",
            "item": [
                {
                    "name": "Get User",
                    "request": {
                        "method": "GET",
                        "url": {
                            "raw": "http://api.example.com/users/{{user_id}}",
                            "path": ["users", "{{user_id}}"]
                        },
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{token}}"
                            }
                        ]
                    }
                }
            ]
        }
    ]
}
```

### Dependencies (YAML)

The dependency graph defines variable relationships and test ordering. Example:

```yaml
postman_collection_dependencies:
  endpoints:
    "GET /users/{{user_id}}":
      uses_variables:
        token:
          type: dynamic
          set_by:
            - "POST /auth/login"
        user_id:
          type: dynamic
          set_by:
            - "POST /users"

  variables:
    token:
      type: dynamic
      scope: function
      description: "Authentication token from login"
      cleanup: true
```

## Output Structure

Generated tests mirror the Postman collection structure:

```
generated_tests/
├── Auth/
│   └── test_login.py
└── Users/
    ├── test_create_user.py
    ├── test_get_user.py
    └── test_update_user.py
```

Generated test files include:
- Proper test dependencies using pytest-dependency
- Fixtures for variable sharing
- Variable cleanup after tests
- Clear docstrings and comments

Example generated test:

```python
import pytest
import requests

@pytest.mark.dependency()
def test_post_auth_login():
    """Test login endpoint to get auth token."""
    response = requests.post(
        "http://api.example.com/auth/login",
        json={"username": "test", "password": "password"}
    )
    assert response.status_code == 200
    return response.json()["token"]

@pytest.mark.dependency(depends=["test_post_auth_login"])
def test_get_user(token):
    """Test get user endpoint."""
    response = requests.get(
        "http://api.example.com/users/123",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_cli.py
```

### Project Structure

```
postman-to-pytest/
├── src/
│   ├── parser/          # Input file parsing
│   ├── generator/       # Test file generation
│   └── utils/          # Utility functions
├── tests/              # Test files
└── examples/           # Example input files
```

## Dependencies

- Python 3.8+
- pytest
- pytest-dependency
- pyyaml
- click
- requests

## Limitations

- Single target endpoint per conversion (when using --target or --name)
- Basic variable type support
- No support for complex variable transformations
- Manual test assertion configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License
