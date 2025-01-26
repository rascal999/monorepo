#!/bin/bash

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama is required but not installed. Please install it first."
    echo "Visit: https://ollama.ai"
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "jq is required but not installed. Please install it first."
    echo "Try: sudo apt install jq"
    exit 1
fi

# Check if fzf is installed
if ! command -v fzf &> /dev/null; then
    echo "fzf is required but not installed. Please install it first."
    echo "Try: sudo apt install fzf"
    echo "Or: git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf && ~/.fzf/install"
    exit 1
fi

# Pull required Ollama model
echo "Pulling qwen2.5-coder:3b model..."
ollama pull qwen2.5-coder:3b

# Copy script to user's bin directory
mkdir -p ~/.local/bin
cp terminai.sh ~/.local/bin/terminai.sh
chmod +x ~/.local/bin/terminai.sh

# Add to shell config
if [[ -n "$BASH_VERSION" ]]; then
    echo "source ~/.local/bin/terminai.sh" >> ~/.bashrc
    echo "Added to ~/.bashrc"
elif [[ -n "$ZSH_VERSION" ]]; then
    echo "source ~/.local/bin/terminai.sh" >> ~/.zshrc
    echo "Added to ~/.zshrc"
fi

echo "Installation complete! Please restart your shell or run:"
echo "source ~/.local/bin/terminai.sh"