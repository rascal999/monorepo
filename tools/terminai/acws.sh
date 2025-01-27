#!/bin/bash

# Check if input is provided
if [ $# -eq 0 ]; then
    echo "Usage: ac.sh 'description of command you want'"
    echo "Example: ac.sh 'find all python files modified in last 24 hours'"
    exit 1
fi

# Check if fzf is available
if ! command -v fzf >/dev/null 2>&1; then
    echo "Error: fzf is required but not installed" >&2
    exit 1
fi

# Check for OpenRouter API key
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "Error: OPENROUTER_API_KEY environment variable is required" >&2
    exit 1
fi

# Combine all arguments into one string
DESCRIPTION="$*"

# Create prompt
PROMPT="You are a genius shell command generator. Convert this description into shell commands:
$DESCRIPTION

Provide 5 different possible commands that could accomplish this task.
Format your response as a numbered list with just the commands, no explanation or backticks:
1. command1
2. command2
3. command3
4. command4
5. command5"

# Create request body
REQUEST_BODY="{
  \"model\": \"openai/gpt-4o:online\",
  \"messages\": [{
    \"role\": \"user\",
    \"content\": \"$PROMPT\"
  }]
}"

# Send request to OpenRouter
RESPONSE=$(curl -s \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     -H "HTTP-Referer: https://github.com/terminai" \
     -H "X-Title: Terminai" \
     -d "$REQUEST_BODY" \
     https://openrouter.ai/api/v1/chat/completions)

# Extract commands from response
COMMANDS=$(echo "$RESPONSE" | jq -r '.choices[0].message.content' | \
    grep -E '^[0-9]+\.' | \
    sed -E 's/^[0-9]+\.\s*`?([^`]*)`?$/\1/')

if [ -n "$COMMANDS" ]; then
    # Let user select command with fzf
    SELECTED=$(echo "$COMMANDS" | fzf --height 40% \
                                     --reverse \
                                     --prompt="Select command to execute: " \
                                     --select-1 \
                                     --exit-0)
    
    if [ -n "$SELECTED" ]; then
        # Copy to clipboard if xclip is available
        if command -v xclip >/dev/null 2>&1; then
            echo -n "$SELECTED" | xclip -selection clipboard
            echo "(Command copied to clipboard)"
        fi
        
        # Execute the command
        eval "$SELECTED"
    fi
else
    echo "Error: Failed to generate commands" >&2
    echo "Response: $RESPONSE" >&2
    exit 1
fi
