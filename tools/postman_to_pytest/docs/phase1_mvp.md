# Phase 1: MVP (Minimum Viable Product)

## Goals
- Basic conversion of Postman collections to pytest files
- Support for essential HTTP methods (GET, POST, PUT, DELETE)
- Basic authentication support (Bearer token)
- Basic proxy support (HTTP/HTTPS)
- Directory structure that mirrors API paths
- Tests organized by HTTP verb per endpoint

## Implementation Steps

### 1. Core Framework Setup
- Project structure
  - src/ directory for source code
  - tests/ directory for test files
  - collections/ directory for Postman collections
  - auth/ directory for authentication handling
- Authentication setup
  - OAuth configuration file
  - Token management module
  - Authentication fixtures
- Basic CLI interface
  - Input file argument
  - Output directory argument
  - Help command
- Essential dependencies
  - pytest
  - requests
  - pydantic
  - click (for CLI)

### 2. Basic Conversion Logic
- JSON parsing
  - Collection file reading
  - Schema validation
  - Error handling
  - Variable extraction
- Variable Management
  - Extract variables from collection
  - Handle variables through environment files
  - Special handling for domain variables
  - Proper URL construction (domain vs path)
- Simple test file generation
  - Test function creation
  - Basic assertions
  - Request mapping
  - Variable substitution
- Basic request handling
  - HTTP method support
  - URL construction (base URL + path)
  - Headers management
  - Request body formatting
  - Proxy configuration
  - Basic proxy authentication

### 3. Initial Testing
- Unit tests for core functionality
  - JSON parsing tests
  - Conversion logic tests
  - Request handling tests
- Simple integration test
  - End-to-end conversion test
  - Basic request execution
  - Assertion verification

## Deliverables

### 1. Working CLI Tool
- Command line interface
  ```bash
  postman2pytest input.json --output ./tests
  ```
- Basic error reporting
- Help documentation

### 2. Basic Test File Generation
- Directory structure mirrors API paths (e.g., /api/v1/users -> tests/api/v1/users/)
- Separate test files by HTTP verb with verb-first naming (e.g., test_get_users.py, test_post_users.py)
- Files grouped by HTTP method for easier filtering and running specific types of tests
- Environment variables handling
  - Copy tools/postman_to_pytest/.env file to generated tests directory as .env
  - Variable registry generation:
    - Generate variable_registry.json in tools/postman_to_pytest/ from postman collection if it doesn't exist
    - Copy variable_registry.json to generated_tests/ during test generation
    - All variables default to fixture source type
    - Include placeholder regex patterns for response extraction
    - Example registry provided in docs/variable_registry.json.example
  - Variable registry features:
    - File-based variables from .env
    - Fixture-based variables (default source type)
    - Response-based variables with regex extraction
    - Collection-based variables from Postman
  - Track variable metadata and sources
  - Support regex patterns for response extraction
  - Domain variables handled separately
  - Base URL from environment
  - Path variables from collection
  - Response-based variables:
    - Extract values from test responses using regex patterns
    - Define source test and file for each response-based variable
    - Automatically add test dependencies based on variable sources
    - Centralized response logging in generated_tests root
    - Test ordering through pytest-dependency plugin
- Authentication fixtures
  - OAuth token acquisition
  - Token refresh handling
  - Token storage
  - Token injection into requests
- Basic pytest fixtures
- Request handling functions
- Clear test naming based on verb and endpoint

### 3. Simple Documentation
- README with installation instructions
- Basic usage examples
- Command line options
- Simple troubleshooting guide

## Success Criteria
1. Can successfully convert a basic Postman collection
2. Generated tests can be executed with pytest
3. Basic assertions work correctly
4. Bearer token authentication functions properly
5. All essential HTTP methods are supported
6. Variables are properly extracted and managed
7. URLs are correctly constructed (domain + path)

## Testing Plan
1. Unit Tests
   - JSON parsing
   - Test generation
   - Request handling
   - Authentication

2. Integration Tests
   - Full conversion process
   - Test execution
   - Basic error cases

## Dependencies
- Python 3.8+
- pytest
- pytest-dependency (for test ordering)
- requests[socks]
- requests-oauthlib
- pydantic
- click
- urllib3
- python-dotenv (for auth configuration)

## Limitations
- Basic proxy support only (no advanced features)
- Basic assertions only
- No pre-request scripts
- No dynamic variables
- Manual OAuth configuration required
- Single OAuth flow support

## Next Steps
After MVP completion, move to Phase 2:
- Support additional authentication methods
- Enhance test assertions
- Support multiple OAuth flows
- Add automatic OAuth configuration
- Support for different environments
