# Phase 1: MVP (Minimum Viable Product)

## Goals
- Convert Postman collections to pytest files using dependency information
- Use dependency graph YML for test ordering and variable relationships
- Extract request details from Postman collection JSON
- Generate pytest fixtures for variable sharing between tests
- Support both static and dynamic variables
- Handle variable scoping and cleanup
- Create a clear and organized test structure
- Mirror Postman collection folder structure in output

## Implementation Steps

### 1. Core Framework Setup
- Project structure
  - src/ directory for source code
  - tests/ directory for test files
  - examples/ directory for sample files
- Basic CLI interface
  - Input YML file argument (dependency graph)
  - Input JSON file argument (Postman collection)
  - Output directory argument (generated_tests/)
  - Target endpoint options (--target or --name)
  - Collection folder exclusion option
  - Dependency folder exclusion option
  - Help command
- Essential dependencies
  - pytest
  - pyyaml
  - pytest-dependency
  - click (for CLI)

### 2. Core Conversion Logic
- Input parsing
  - Dependency graph YML reading
  - Postman collection JSON reading
  - Schema validation for both inputs
  - Error handling
  - Variable dependency extraction
  - Request details extraction
  - Collection folder structure analysis
- Variable Management
  - Extract variables from dependency graph
  - Generate pytest fixtures for variables
  - Handle variable dependencies
  - Support both static and dynamic variables
- Test file generation
  - Test function creation based on endpoints
  - Proper test ordering using pytest-dependency
  - Fixture generation for variable sharing
  - Variable scope management

### 3. Initial Testing
- Unit tests for core functionality
  - YAML parsing tests
  - Dependency analysis tests
  - Test generation logic tests
  - Folder structure tests
- Integration tests
  - End-to-end conversion test
  - Test execution order verification
  - Variable sharing verification
  - Directory structure verification

## Deliverables

### 1. Working CLI Tool
- Command line interface
  ```bash
  # Using HTTP method and path
  postman2pytest \
    --collection input.json \      # Postman collection with request details
    --dependencies input.yml \     # Dependency graph from postman_dependency_graph
    --output generated_tests \     # Output directory for generated tests
    --target "GET /api/endpoint" \ # Target endpoint in format: "{HTTP_METHOD} {PATH}"
    --exclude-collection-folder auth \
    --exclude-dependency-folder tutorials

  # Using Postman friendly names
  postman2pytest \
    --collection input.json \
    --dependencies input.yml \
    --output generated_tests \
    --name "User Management/Get User Details" \ # Target using Postman folder/test name
    --exclude-collection-folder auth \
    --exclude-dependency-folder tutorials
  ```
- Target endpoint handling:
  * Option 1: --target argument in format: "{HTTP_METHOD} {PATH}"
    - Example: --target "GET /api/users"
    - Technical format matching dependency graph
  * Option 2: --name argument using Postman folder/test names
    - Format: "Folder Name/Test Name" or "Test Name"
    - Example: --name "User Management/Get User Details"
    - More user-friendly as it matches Postman UI
  * If neither specified:
    - Generates tests for all endpoints in the collection
    - Maintains proper dependency ordering for all tests
    - Organizes tests according to collection structure
  * For any option:
    - Generates tests for target endpoint and its dependencies
    - Example: if target needs user ID from another endpoint,
      tests will be generated for both in correct order
- Comprehensive error reporting
- Help documentation with examples

### 2. Test File Generation
- Organized test structure in generated_tests/
  - Directory structure mirrors Postman collection folders
  - One test file per endpoint chain
  - Clear test function naming based on endpoint
  - Proper test ordering using @pytest.mark.dependency
  - Support for excluding specific collection folders
- Variable handling
  - Fixtures for variable sharing
  - Proper variable scoping
  - Variable cleanup after tests
  - Support for both static and dynamic variables
- Test dependencies
  - Automatic dependency detection from YML
  - Proper test ordering based on dependencies
  - Clear dependency documentation in test files
- Generated test features
  - Clear docstrings explaining dependencies
  - Comments for variable usage
  - Proper assertion structure
  - Error handling for missing dependencies

### 3. Documentation
- README with:
  - Installation instructions
  - Usage examples with collection and dependency YML
  - CLI options
  - Variable handling explanation
  - Test dependency management
  - Folder structure explanation
- Inline code documentation
- Example files

## Success Criteria
1. Can successfully parse both dependency YML and collection JSON
2. Extracts correct request details from collection
3. Generates properly ordered pytest files
4. Variable sharing works correctly through fixtures
5. Test dependencies are properly managed
6. Generated tests can be executed with pytest
7. Variable scoping and cleanup works correctly
8. Clear and organized test structure
9. Output directory structure matches collection structure
10. Folder exclusions work correctly for both inputs
11. Both --target and --name options work correctly

## Testing Plan
1. Unit Tests
   - JSON parsing
   - Test generation
   - Request handling
   - Authentication
   - Folder structure handling
   - Name resolution (Postman folder/test names)

2. Integration Tests
   - Full conversion process
   - Test execution
   - Basic error cases
   - Directory structure verification
   - Name-based target resolution

## Dependencies
- Python 3.8+
- pytest
- pytest-dependency
- pyyaml
- click
- requests (for test execution)
- python-dotenv (for environment configuration)
- requests-oauthlib (for OAuth authentication)

## Authentication & Environment Configuration
- OAuth 2.0 support:
  * Basic auth to OAuth token exchange
  * Token caching in .oauth_token file
  * Custom auth header configuration
  * Token refresh handling
- Proxy configuration:
  * HTTP/HTTPS proxy support
  * Proxy authentication
  * SSL verification options
  * Custom certificate paths
- Environment variables:
  * .env file for configuration
  * .env.sample for documentation
  * Secure credential handling
  * Environment variables loaded by conftest.py
  * Common variables provided as pytest fixtures:
    - env_url: Base URL for API requests
    - tls_verify: SSL verification setting
  * Generated tests use fixtures instead of direct env var access
  * Centralized environment configuration in conftest.py
  * Easy override of environment settings through pytest fixtures

## Limitations
- Single target endpoint per conversion (when using --target or --name)
- Basic variable type support
- No support for complex variable transformations
- Manual test assertion configuration

## Next Steps
After MVP completion, move to Phase 2:
- Support for multiple target endpoints
- Enhanced variable type support
- Variable transformation functions
- Automatic test assertion generation
- Support for test parameterization
