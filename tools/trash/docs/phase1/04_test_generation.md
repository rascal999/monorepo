# Test File Generation

## Generated Test Structure
- Organized test structure in generated_tests/
  - Directory structure mirrors Postman collection folders
  - One test file per endpoint chain
  - Clear test function naming based on endpoint
  - Proper test ordering using @pytest.mark.dependency
  - Support for excluding specific collection folders

## Variable Handling
- Fixtures for variable sharing
  - Generated pytest fixtures
  - Proper variable scoping
  - Variable cleanup after tests
  - Support for both static and dynamic variables

## Test Dependencies
- Automatic dependency detection from YML
- Proper test ordering based on dependencies
- Clear dependency documentation in test files
- Dependency visualization support:
  * Preview dependency chains before generation
  * Show fixture relationships and sources
  * Display environment variable usage
  * Match postman_dependency_graph format

## Generated Test Features
- Clear docstrings explaining dependencies
- Comments for variable usage
- Proper assertion structure
- Error handling for missing dependencies

## Test File Organization
- Directory structure matches collection structure
- Logical test file naming
- Consistent file structure across generated tests
- Clear separation of concerns

## Documentation in Generated Tests
- File-level documentation explaining purpose
- Function-level documentation for each test
- Dependency documentation
- Variable usage documentation
- Error handling documentation

## Success Criteria
1. Generated tests can be executed with pytest
2. Variable scoping and cleanup works correctly
3. Clear and organized test structure
4. Output directory structure matches collection structure
5. Folder exclusions work correctly
6. Dependencies are properly managed
7. Variable sharing works correctly through fixtures
8. Dependency visualization matches actual test structure
9. Dry run output matches postman_dependency_graph format
