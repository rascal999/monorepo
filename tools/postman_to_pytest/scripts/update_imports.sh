#!/usr/bin/env bash

# Update imports in all test files
for dir in tests/generator/*; do
  if [ -d "$dir" ]; then
    for file in "$dir"/test_*.py; do
      if [ -f "$file" ]; then
        # Update ContentGenerator import
        sed -i 's/from src\.generator\.content_generator import ContentGenerator/from src.generator.test import ContentGenerator/g' "$file"
        # Update FixtureGenerator import
        sed -i 's/from src\.generator\.fixtures import FixtureGenerator/from src.generator.handlers.fixtures import FixtureGenerator/g' "$file"
        # Update TestFileGenerator import
        sed -i 's/from src\.generator\.test_file import TestFileGenerator/from src.generator.test import TestFileGenerator/g' "$file"
      fi
    done
  fi
done
