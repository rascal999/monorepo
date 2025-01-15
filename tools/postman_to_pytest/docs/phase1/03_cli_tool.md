# CLI Tool

## Command Line Interface

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

## Target Endpoint Handling
- Option 1: --target argument
  * Format: "{HTTP_METHOD} {PATH}"
  * Example: --target "GET /api/users"
  * Technical format matching dependency graph

- Option 2: --name argument
  * Format: "Folder Name/Test Name" or "Test Name"
  * Example: --name "User Management/Get User Details"
  * More user-friendly as it matches Postman UI

- Default behavior (no target specified):
  * Generates tests for all endpoints in the collection
  * Maintains proper dependency ordering for all tests
  * Organizes tests according to collection structure

- For any option:
  * Generates tests for target endpoint and its dependencies
  * Example: if target needs user ID from another endpoint,
    tests will be generated for both in correct order

## Features
- Comprehensive error reporting
- Help documentation with examples
- Support for excluding specific collection folders
- Support for excluding dependency folders
- Automatic dependency resolution
- Clear output directory structure
