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

The converter creates:
- Pytest test files
- Fixtures for shared resources
- Environment variable handling
- Request session management

## Example

Input files:
- `mgp-sample.json`: Mangopay API collection
- `mgp-sample.yml`: Dependency configuration

Generated output in `generated_tests/`:
- Test files following Pytest conventions
- Organized by endpoint categories
- Maintains dependencies between tests
