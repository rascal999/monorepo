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
- Simple test file generation
  - Test function creation
  - Basic assertions
  - Request mapping
- Basic request handling
  - HTTP method support
  - URL construction
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
- Add advanced proxy support
- Enhance test assertions
- Support multiple OAuth flows
- Add automatic OAuth configuration
