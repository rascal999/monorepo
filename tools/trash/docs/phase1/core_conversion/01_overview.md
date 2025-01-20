# Core Conversion Overview

## Components Overview

### 1. Parser Module
- Collection Parser
  * Purpose: Parse Postman collection JSON format
  * Components:
    - Request details extraction
    - Headers and auth parsing
    - Variable identification
    - Folder structure analysis
  * Location: src/parser/collection.py

- Dependency Parser
  * Purpose: Parse dependency graph YML format
  * Components:
    - Variable dependency extraction
    - Test ordering information
    - Folder exclusion rules
  * Location: src/parser/dependency.py

### 2. Generator Module
- Test Generator
  * Purpose: Generate pytest test files
  * Components:
    - Test function creation
    - Dependency management
    - Variable scope handling
  * Location: src/generator/test_generator.py

- Content Generator
  * Purpose: Generate test content and assertions
  * Components:
    - Request formatting
    - Response handling
    - Basic assertions
  * Location: src/generator/content_generator.py

- Fixture Generator
  * Purpose: Generate pytest fixtures
  * Components:
    - Variable fixtures
    - Authentication fixtures
    - Environment fixtures
  * Location: src/generator/fixtures.py

### 3. Utils Module
- Validation Utils
  * Purpose: Input validation and error handling
  * Components:
    - Schema validation
    - Input format checking
    - Error reporting
  * Location: src/utils/validation.py

- Path Utils
  * Purpose: Handle file and directory paths
  * Components:
    - Output path generation
    - Directory structure creation
    - Path normalization
  * Location: src/utils/paths.py

## Development Approach

### 1. Input Processing
1. Collection Processing
   - Read and validate Postman collection JSON
   - Extract request details (method, URL, headers)
   - Parse authentication information
   - Identify variables and their usage
   - Map collection folder structure

2. Dependency Processing
   - Parse dependency graph YML
   - Extract variable relationships
   - Determine test execution order
   - Process folder exclusions

### 2. Variable Management
1. Variable Identification
   - Static variables from YML
   - Dynamic variables from responses
   - Environment variables
   - Authentication tokens

2. Variable Handling
   - Scope determination
   - Fixture generation
   - Cleanup requirements
   - Value propagation

### 3. Test Generation
1. Structure Creation
   - Mirror Postman folder structure
   - Create test files
   - Generate conftest.py
   - Handle file naming

2. Content Generation
   - Test function creation
   - Fixture implementation
   - Request formatting
   - Basic assertions
