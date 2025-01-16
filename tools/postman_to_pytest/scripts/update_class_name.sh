#!/usr/bin/env bash

# Update all test files to use ContentGenerator instead of TestContentGenerator
find tests/generator -type f -name "test_*.py" -exec sed -i 's/TestContentGenerator/ContentGenerator/g' {} +
