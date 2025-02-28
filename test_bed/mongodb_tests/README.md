# MongoDB Tests

This directory contains scripts to test MongoDB functionality on G16/rig hosts.

## Overview

These tests verify that MongoDB is properly installed, running, and accessible. They test basic MongoDB operations including:

- Connecting to the MongoDB server
- Creating databases and collections
- Inserting documents
- Querying documents
- Updating documents
- Deleting documents

## Requirements

- Python 3
- `pymongo` Python package (will be installed automatically by the test script if needed)
- MongoDB service running

## Running the Tests

### Running All Tests

The easiest way to run all tests is to use the run_all_tests.sh script:

1. Make the script executable:
   ```bash
   chmod +x run_all_tests.sh
   ```

2. Run all tests:
   ```bash
   ./run_all_tests.sh
   ```

This script will run both the basic MongoDB tests and the Docker connectivity tests, and provide a summary of the results.

### Basic MongoDB Tests

If you want to run only the basic MongoDB tests:

1. Make the run script executable:
   ```bash
   chmod +x run_test.sh
   ```

2. Run the test script:
   ```bash
   ./run_test.sh
   ```

The script will:
- Check if the required Python packages are installed
- Install any missing packages
- Run the MongoDB test script
- Display the results

### Docker Connectivity Tests

To test only MongoDB connectivity from Docker containers:

1. Make the Docker test script executable:
   ```bash
   chmod +x test_docker_access.sh
   ```

2. Run the Docker test script:
   ```bash
   ./test_docker_access.sh
   ```

This script will:
- Check if Docker is installed and running
- Try to connect to MongoDB from a Docker container using different methods:
  - Using host.docker.internal
  - Using the Docker bridge network (172.17.0.1)
  - Using host network mode
- Display which connection methods work
- Provide troubleshooting tips if connections fail

## Test Script Details

### `test_mongodb.py`

This Python script performs the following tests:

1. Connects to MongoDB on localhost (127.0.0.1) port 27017
2. Retrieves and displays server information
3. Creates a test database and collection
4. Inserts test documents
5. Performs various queries to verify data retrieval
6. Updates a document and verifies the update
7. Cleans up by dropping the test database

### `run_test.sh`

This shell script:

1. Checks if the required Python packages are installed
2. Installs any missing packages
3. Runs the MongoDB test script
4. Provides feedback on the test results

### `test_docker_access.sh`

This shell script tests MongoDB connectivity from Docker containers:

1. Checks if Docker is installed and running
2. Attempts to connect to MongoDB using three different methods:
   - Using `host.docker.internal` (works on Docker Desktop)
   - Using the Docker bridge network IP (172.17.0.1)
   - Using host network mode
3. Reports which connection methods work
4. Provides example connection strings for Docker containers
5. Offers troubleshooting tips if connections fail

### `run_all_tests.sh`

This shell script runs all the MongoDB tests:

1. Executes the basic MongoDB tests (`run_test.sh`)
2. Executes the Docker connectivity tests (`test_docker_access.sh`)
3. Provides a summary of all test results
4. Returns a success or failure exit code based on all test results

## Troubleshooting

If the tests fail, check the following:

1. **MongoDB Service**: Ensure MongoDB is running
   ```bash
   sudo systemctl status mongodb
   ```

2. **MongoDB Configuration**: Check if MongoDB is listening on the expected address
   ```bash
   sudo netstat -tuln | grep 27017
   ```

3. **Firewall**: Ensure the MongoDB port is not blocked
   ```bash
   sudo ufw status
   ```

4. **Logs**: Check MongoDB logs for errors
   ```bash
   sudo journalctl -u mongodb
   ```

## Docker Container Access

If you're testing access from Docker containers, you can use:

```bash
docker run --rm mongo:latest mongosh --host host.docker.internal --eval "db.runCommand({ping: 1})"
```

This command will attempt to connect to the MongoDB server from a Docker container and execute a simple ping command.