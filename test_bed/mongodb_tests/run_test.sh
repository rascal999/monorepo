#!/bin/bash
# MongoDB Test Runner Script
# This script checks for pymongo, installs it if needed, and runs the MongoDB test

set -e  # Exit on error

echo "MongoDB Test Runner"
echo "=================="
echo

# Check if pymongo is installed
if python3 -c "import pymongo" &>/dev/null; then
    echo "✅ pymongo is already installed"
else
    echo "⚠️ pymongo is not installed. Attempting to install..."
    pip3 install pymongo
    echo "✅ pymongo has been installed"
fi

echo
echo "Running MongoDB test script..."
echo "-----------------------------"
echo

# Make the test script executable
chmod +x test_mongodb.py

# Run the test script
python3 test_mongodb.py

# Check exit status
if [ $? -eq 0 ]; then
    echo
    echo "✅ MongoDB test completed successfully!"
    echo "MongoDB is properly configured and working on this system."
else
    echo
    echo "❌ MongoDB test failed!"
    echo "Please check that MongoDB is running and accessible."
    echo "You can start MongoDB with: sudo systemctl start mongodb"
    exit 1
fi