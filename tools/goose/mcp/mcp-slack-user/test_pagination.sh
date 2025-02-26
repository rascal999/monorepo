#!/bin/bash

# Load environment variables
source .env

# Function to test channel listing with specific parameters
test_pagination() {
    local limit=$1
    local delay=$2
    local cursor=""
    local total_channels=0
    local page=1
    local start_time=$(date +%s)

    echo "Testing with limit=$limit and delay=$delay seconds"
    echo "----------------------------------------"

    while true; do
        # Build the cursor parameter
        local cursor_param=""
        if [ -n "$cursor" ]; then
            cursor_param="&cursor=$cursor"
        fi

        # Make the API call
        response=$(curl -s -X POST \
            -H "Authorization: Bearer $SLACK_USER_TOKEN" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            "https://slack.com/api/conversations.list?limit=$limit&types=public_channel,private_channel$cursor_param")

        # Check for rate limiting
        if echo "$response" | grep -q "\"error\":\"ratelimited\""; then
            echo "Rate limited on page $page! Waiting 60 seconds..."
            sleep 60
            continue
        fi

        # Extract channels and cursor
        channels_count=$(echo "$response" | jq '.channels | length')
        cursor=$(echo "$response" | jq -r '.response_metadata.next_cursor')
        
        # Update total and print progress
        total_channels=$((total_channels + channels_count))
        echo "Page $page: Got $channels_count channels (Total: $total_channels)"

        # Break if no more channels, regardless of cursor
        if [ "$channels_count" -eq 0 ] || [ "$cursor" = "null" ] || [ -z "$cursor" ]; then
            break
        fi

        # Wait before next request
        sleep $delay
        page=$((page + 1))
    done

    local end_time=$(date +%s)
    local total_time=$((end_time - start_time))

    echo "----------------------------------------"
    echo "Final results for limit=$limit, delay=$delay:"
    echo "Total channels: $total_channels"
    echo "Total pages: $page"
    echo "Total time: $total_time seconds"
    echo "Average time per page: $(echo "scale=2; $total_time/$page" | bc) seconds"
    echo "Average channels per page: $(echo "scale=2; $total_channels/$page" | bc)"
    echo
}

# Test different combinations
echo "Starting pagination tests..."
echo

# Test with different limits and delays
test_pagination 200 1  # Default: 200 per page, 1s delay
test_pagination 100 2  # More conservative: 100 per page, 2s delay
test_pagination 50 3   # Very conservative: 50 per page, 3s delay

echo "Tests complete!"