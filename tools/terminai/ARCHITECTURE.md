# TerminAI MVP Architecture

## Overview
Simple shell command suggestion tool using Ollama to analyze terminal history when tab is pressed.

## MVP Components

### Shell Integration
- Basic shell function to capture tab press
- Read last few commands from history

### Ollama Integration  
- Send history context to local Ollama
- Get command suggestions
- Display to user

## MVP Implementation

```bash
# Core shell function
terminai_suggest() {
    # Get last 5 commands from history
    # Send to Ollama
    # Show suggestions
}

# Bind to tab
bind -x '"\t": terminai_suggest'
```

## Dependencies
- Ollama
- Bash/Zsh