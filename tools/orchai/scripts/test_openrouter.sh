#!/usr/bin/env bash

# Source environment variables
set -a
source .env
set +a

echo "Testing OpenRouter API..."
echo "Using API key: ${OPENROUTER_API_KEY:0:10}..."

# Test OpenRouter API
curl -s -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "HTTP-Referer: https://github.com/orchai" \
  -H "X-Title: OrchAI" \
  -d '{
    "model": "google/gemini-flash-1.5-8b",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "Say hello!"
      }
    ]
  }' | jq -r '.choices[0].message.content'