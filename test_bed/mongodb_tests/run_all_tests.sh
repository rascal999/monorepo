#!/bin/bash
# MongoDB Test Suite Runner
# This script runs all MongoDB tests

set -e  # Exit on error

echo "MongoDB Test Suite"
echo "================="
echo

# Make all scripts executable
chmod +x run_test.sh
chmod +x test_docker_access.sh

# Run basic MongoDB test
echo "Running basic MongoDB tests..."
echo "-----------------------------"
./run_test.sh
BASIC_TEST_RESULT=$?
echo

# Run Docker connectivity test
echo "Running Docker connectivity tests..."
echo "----------------------------------"
./test_docker_access.sh
DOCKER_TEST_RESULT=$?
echo

# Display summary
echo "Test Summary"
echo "============"
echo

if [ $BASIC_TEST_RESULT -eq 0 ]; then
    echo "✅ Basic MongoDB tests: PASSED"
else
    echo "❌ Basic MongoDB tests: FAILED"
fi

if [ $DOCKER_TEST_RESULT -eq 0 ]; then
    echo "✅ Docker connectivity tests: PASSED"
else
    echo "❌ Docker connectivity tests: FAILED"
fi

echo

if [ $BASIC_TEST_RESULT -eq 0 ] && [ $DOCKER_TEST_RESULT -eq 0 ]; then
    echo "🎉 All tests passed! MongoDB is properly configured and working."
    exit 0
else
    echo "⚠️ Some tests failed. Please check the output above for details."
    exit 1
fi