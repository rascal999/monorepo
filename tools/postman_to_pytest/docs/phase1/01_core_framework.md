# Core Framework Setup

## Project Structure
- src/ directory for source code
- tests/ directory for test files
- examples/ directory for sample files
- generated_tests/ directory for output test files

## Essential Dependencies
- pytest
- pyyaml
- pytest-dependency
- click (for CLI)
- requests (for test execution)
- python-dotenv (for environment configuration)
- requests-oauthlib (for OAuth authentication)

## Requirements
- Python 3.8+

## Implementation Steps
- Project structure setup
  - src/ directory for source code
  - tests/ directory for test files
  - examples/ directory for sample files
  - generated_tests/ directory for output test files
- Basic CLI interface setup
  - Input YML file argument (dependency graph)
  - Input JSON file argument (Postman collection)
  - Output directory argument (generated_tests/)
  - Target endpoint options (--target or --name)
  - Collection folder exclusion option
  - Dependency folder exclusion option
  - Help command
