#!/usr/bin/env bash
# MongoDB Docker Access Test Script
# This script tests MongoDB connectivity from a Docker container

set -e  # Exit on error

echo "MongoDB Docker Access Test"
echo "=========================="
echo

# Check if Docker is installed
if ! command -v docker &>/dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    echo "Please install Docker and try again"
    exit 1
fi

echo "✅ Docker is installed"

# Check if Docker daemon is running
if ! docker info &>/dev/null; then
    echo "❌ Docker daemon is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "✅ Docker daemon is running"
echo

echo "Testing MongoDB connectivity from Docker container..."
echo "----------------------------------------------------"

# Run MongoDB client in Docker container and try to connect to host
echo "Attempting to connect to MongoDB from Docker container..."
echo

# Try to connect using host.docker.internal (works on Docker Desktop)
echo "Method 1: Using host.docker.internal"
if docker run --rm mongo:latest mongosh --host host.docker.internal --eval "db.runCommand({ping: 1})" &>/dev/null; then
    echo "✅ Successfully connected to MongoDB using host.docker.internal"
    SUCCESS_HOST_INTERNAL=true
else
    echo "❌ Failed to connect using host.docker.internal"
    SUCCESS_HOST_INTERNAL=false
fi

echo

# Try to connect using Docker bridge network (172.17.0.1)
echo "Method 2: Using Docker bridge network (172.17.0.1)"
if docker run --rm mongo:latest mongosh --host 172.17.0.1 --eval "db.runCommand({ping: 1})" &>/dev/null; then
    echo "✅ Successfully connected to MongoDB using 172.17.0.1"
    SUCCESS_BRIDGE=true
else
    echo "❌ Failed to connect using 172.17.0.1"
    SUCCESS_BRIDGE=false
fi

echo

# Try to connect using host network
echo "Method 3: Using host network"
if docker run --rm --network host mongo:latest mongosh --host 127.0.0.1 --eval "db.runCommand({ping: 1})" &>/dev/null; then
    echo "✅ Successfully connected to MongoDB using host network"
    SUCCESS_HOST_NETWORK=true
else
    echo "❌ Failed to connect using host network"
    SUCCESS_HOST_NETWORK=false
fi

echo
echo "Test Summary"
echo "------------"

if [ "$SUCCESS_HOST_INTERNAL" = true ] || [ "$SUCCESS_BRIDGE" = true ] || [ "$SUCCESS_HOST_NETWORK" = true ]; then
    echo "✅ MongoDB is accessible from Docker containers!"
    
    echo
    echo "Working connection methods:"
    [ "$SUCCESS_HOST_INTERNAL" = true ] && echo "- host.docker.internal"
    [ "$SUCCESS_BRIDGE" = true ] && echo "- Docker bridge network (172.17.0.1)"
    [ "$SUCCESS_HOST_NETWORK" = true ] && echo "- Host network"
    
    echo
    echo "Example connection string for Docker containers:"
    if [ "$SUCCESS_HOST_INTERNAL" = true ]; then
        echo "mongodb://host.docker.internal:27017"
    elif [ "$SUCCESS_BRIDGE" = true ]; then
        echo "mongodb://172.17.0.1:27017"
    else
        echo "Use --network host and mongodb://127.0.0.1:27017"
    fi
    
    exit 0
else
    echo "❌ MongoDB is not accessible from Docker containers"
    echo
    echo "Troubleshooting tips:"
    echo "1. Ensure MongoDB is running: sudo systemctl status mongodb"
    echo "2. Check MongoDB is listening on the correct interfaces:"
    echo "   - Run: sudo netstat -tuln | grep 27017"
    echo "   - MongoDB should be listening on 127.0.0.1 and 172.17.0.1"
    echo "3. Check MongoDB configuration:"
    echo "   - Ensure bind_ip includes 127.0.0.1 and 172.17.0.1"
    echo "4. Check firewall rules:"
    echo "   - Ensure port 27017 is allowed for Docker bridge network"
    
    exit 1
fi