#!/bin/bash

# Example prompt
PROMPT="You are a shell command suggestion tool.

Recent commands:
- ls -la
- git status
- docker ps
- npm start
- curl localhost:3000

Current input: git

Suggest 3 relevant commands the user might want to run next.
Format as a numbered list:
1. command1
2. command2
3. command3"

# Escape the prompt for JSON
ESCAPED_PROMPT=$(printf '%s' "$PROMPT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')

# Create request body
REQUEST_BODY="{\"model\":\"qwen2.5-coder:3b\",\"prompt\":$ESCAPED_PROMPT,\"stream\":false,\"temperature\":0.7}"

# Send request to Ollama
echo "Sending request to Ollama..."
curl -s \
     -H "Content-Type: application/json" \
     -d "$REQUEST_BODY" \
     http://localhost:11434/api/generate | jq '.'

echo -e "\nExtracted commands:"
curl -s \
     -H "Content-Type: application/json" \
     -d "$REQUEST_BODY" \
     http://localhost:11434/api/generate | \
     jq -r '.response' | \
     grep -E '^[0-9]+\.' | \
     sed -E 's/^[0-9]+\.\s*`?([^`]*)`?$/\1/'