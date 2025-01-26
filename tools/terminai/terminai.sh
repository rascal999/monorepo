#!/bin/bash

# Configuration
TERMINAI_DEBUG=${TERMINAI_DEBUG:-0}
TERMINAI_LOG="/tmp/terminai_debug.log"

# Debug logging
debug_log() {
    [[ $TERMINAI_DEBUG -eq 1 ]] && echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$TERMINAI_LOG"
}

# Get recent command history
get_recent_history() {
    history | tail -n 5 | sed 's/^[[:space:]]*[0-9]\+[[:space:]]*//g'
}

# Get suggestions from Ollama using the working approach from test_ollama.sh
get_suggestions() {
    local history="$1"
    local current="$2"

    # Create example prompt
    local PROMPT="You are a shell command suggestion tool.

Recent commands:
$(printf '%s\n' "$history" | sed 's/^/- /')

Current input: $current

Suggest 3 relevant commands the user might want to run next.
Format as a numbered list:
1. command1
2. command2
3. command3"

    # Escape the prompt for JSON
    local ESCAPED_PROMPT=$(printf '%s' "$PROMPT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')

    # Create request body
    local REQUEST_BODY="{\"model\":\"qwen2.5-coder:3b\",\"prompt\":$ESCAPED_PROMPT,\"stream\":false,\"temperature\":0.7}"

    # Send request to Ollama and extract commands
    local commands=$(curl -s \
         -H "Content-Type: application/json" \
         -d "$REQUEST_BODY" \
         http://localhost:11434/api/generate | \
         jq -r '.response' | \
         grep -E '^[0-9]+\.' | \
         sed -E 's/^[0-9]+\.\s*`?([^`]*)`?$/\1/')

    if [[ -n "$commands" ]]; then
        echo "$commands"
        return 0
    fi

    echo "Error: Failed to get suggestions" >&2
    return 1
}

# Select command using fzf
select_command() {
    echo "$2" | fzf --height 40% \
                    --reverse \
                    --prompt="Select command: " \
                    --query="$1" \
                    --select-1 \
                    --exit-0 \
                    --bind=tab:accept
}

# Generic suggestion handler for both shells
suggest_command() {
    local current="$1" var_name="$2" cursor_var="$3"
    debug_log "Suggestion triggered for: $current"
    
    local suggestions=$(get_suggestions "$(get_recent_history)" "$current")
    if [[ $? -eq 0 ]]; then
        local selected=$(select_command "$current" "$suggestions")
        if [[ -n "$selected" ]]; then
            eval "$var_name=\"\$selected\""
            eval "$cursor_var=\${#selected}"
        fi
    else
        # Show error and redraw prompt
        echo -e "\n$suggestions"
        [[ -n "$ZSH_VERSION" ]] && zle reset-prompt || echo -en "\n$PS1"
        echo -n "$current"
    fi
}

# Shell-specific wrapper functions
terminai_suggest_bash() {
    suggest_command "$READLINE_LINE" READLINE_LINE READLINE_POINT
}

terminai_suggest_zsh() {
    suggest_command "$BUFFER" BUFFER CURSOR
}

# Initialize based on shell type
debug_log "TerminAI initializing"

# Check if script is being sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "This script must be sourced, not executed directly."
    echo "Usage: source $(basename "${BASH_SOURCE[0]}")"
    exit 1
fi

# Setup shell integration
if [[ -n "$BASH_VERSION" ]]; then
    debug_log "Setting up Bash completion"
    bind -x '"\t": terminai_suggest_bash'
elif [[ -n "$ZSH_VERSION" ]]; then
    debug_log "Setting up Zsh completion"
    zle -N terminai_suggest_zsh
    bindkey '^I' terminai_suggest_zsh
fi

debug_log "TerminAI initialization complete"