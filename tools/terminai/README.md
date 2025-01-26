# TerminAI

A minimal shell enhancement that suggests commands based on your recent terminal history when you press tab, powered by Ollama.

## Requirements

- Ollama (https://ollama.ai)
- jq
- bash or zsh shell

## Installation

1. Install Ollama from https://ollama.ai
2. Run the install script:
```bash
cd tools/terminai
chmod +x install.sh
./install.sh
```

## Usage

1. Start Ollama:
```bash
ollama serve
```

2. Press TAB while typing in your terminal to get AI-powered suggestions based on:
   - Your recent command history
   - Current command line input

The suggestions will appear below your prompt, and your current input will be preserved.

## Error Handling

TerminAI includes automatic error handling:

1. Ollama Connection
   - Checks if Ollama is running
   - Shows warning if Ollama is not available
   - Retries failed requests up to 3 times

2. Common Error Messages:
   - "Error: Ollama is not running" - Start Ollama with `ollama serve`
   - "Error: Unable to get suggestions" - Check Ollama status and logs
   - "Warning: Ollama not running" - Shown during startup if Ollama is unavailable

## Debug Mode

Enable debug mode to log operations for troubleshooting:

1. Enable debug logging:
```bash
export TERMINAI_DEBUG=1
source ~/.local/bin/terminai.sh
```

2. View debug logs:
```bash
tail -f /tmp/terminai_debug.log
```

Debug logs include:
- Initialization steps
- Current command line input
- History context
- Full HTTP responses from Ollama API:
  * Raw response body
  * HTTP status codes
  * Error messages
- Retry attempts with status codes
- Shell-specific operations

Example debug log:
```
[2025-01-25 16:44:00] Getting suggestions for current input: git
[2025-01-25 16:44:00] History context: ls
cd project
git status
[2025-01-25 16:44:00] Full Ollama HTTP response: {"response":"1. git commit -m \"update\"..."}
HTTP_STATUS:200
[2025-01-25 16:44:00] HTTP Status Code: 200
[2025-01-25 16:44:00] Parsed response: 1. git commit -m "update"...
```

To disable debug mode:
```bash
export TERMINAI_DEBUG=0
source ~/.local/bin/terminai.sh
```

## Troubleshooting

1. If Ollama is not responding:
```bash
# Check if Ollama is running
ps aux | grep ollama
# Start Ollama if needed
ollama serve
```

2. Verify the model is installed:
```bash
ollama pull qwen2.5-coder:3b
```

3. Check Ollama logs:
```bash
journalctl -u ollama
```

4. Enable debug mode and check HTTP responses:
```bash
export TERMINAI_DEBUG=1
source ~/.local/bin/terminai.sh
tail -f /tmp/terminai_debug.log
```

5. Try reloading your shell:
```bash
source ~/.local/bin/terminai.sh