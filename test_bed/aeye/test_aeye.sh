#!/usr/bin/env bash

# Function to add spacing between tests
space_out() {
    echo -e "\n----------------------------------------"
    echo "$1"
    echo "----------------------------------------"
}

# Test normal request
space_out "Testing normal GET request..."
curl -s http://localhost:8888/products

# Test benign POST request
space_out "Testing benign POST request..."
curl -X POST http://localhost:8888/api/feedback \
    -H "Content-Type: application/json" \
    -d '{"rating": 5, "comment": "Great service!"}'

# Test suspicious login attempt
space_out "Testing suspicious login attempt..."
curl -X POST http://localhost:8888/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "password123"}'

# Test potential SQL injection
space_out "Testing potential SQL injection..."
curl -X GET "http://localhost:8888/products?id=1%20OR%201=1"

# Test potential XSS attempt
space_out "Testing potential XSS attempt..."
curl -X POST http://localhost:8888/comments \
    -H "Content-Type: application/json" \
    -d '{"comment": "<script>alert(\"xss\")</script>"}'

# Test socket.io request (should be ignored)
space_out "Testing socket.io request (should be ignored)..."
curl -X POST http://localhost:8888/socket.io/ -d "test=1"

# Wait for logs and explain
space_out "Test complete!"
echo "Please check nginx error logs for classification results."
echo "Each request should have been sent to Ollama for classification."
echo "You should see classifications of SAFE or SUSPICIOUS with explanations."