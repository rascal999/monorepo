# Core Conversion Documentation

This directory contains detailed documentation about the core conversion process from Postman collections to pytest tests.

## Contents

1. [Overview](01_overview.md)
   - Components Overview (Parser, Generator, Utils modules)
   - Development Approach (Input Processing, Variable Management, Test Generation)

2. [Implementation](02_implementation.md)
   - Phase 1: Basic Parsing
   - Phase 2: Variable Handling
   - Phase 3: Test Generation
   - Success Metrics

3. [Pytest Structure](03_pytest_structure.md)
   - Directory Organization
   - Configuration Files
   - Test File Structure
   - Fixture Scopes
   - Resource Cleanup

4. [Dependencies](04_dependencies.md)
   - Test Dependencies
   - Variable Dependencies
   - Test Execution Flow
   - Resource Management

## Key Concepts

- **Parser Module**: Handles reading and interpreting Postman collections and dependency graphs
- **Generator Module**: Creates pytest files, fixtures, and test functions
- **Utils Module**: Provides common utilities for validation and path handling
- **Test Dependencies**: Manages test ordering and relationships
- **Variable Management**: Handles data sharing between tests
- **Resource Cleanup**: Ensures proper cleanup of test resources

## Implementation Strategy

The conversion process follows a three-phase approach:
1. Parse input files and validate formats
2. Handle variables and generate fixtures
3. Generate final test files with proper dependencies

Each phase builds on the previous one, ensuring a robust and maintainable conversion process.
