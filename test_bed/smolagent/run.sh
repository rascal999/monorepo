#!/bin/bash

# Function to show usage
show_help() {
    echo "Usage: $0 [--ui]"
    echo ""
    echo "Options:"
    echo "  --ui    Launch with Gradio web interface"
    echo "  -h      Show this help message"
    echo ""
    echo "Without options, launches in CLI mode"
}

# Parse command line arguments
USE_UI=0

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --ui) USE_UI=1 ;;
        -h|--help) show_help; exit 0 ;;
        *) echo "Unknown parameter: $1"; show_help; exit 1 ;;
    esac
    shift
done

# Ensure we're in the script's directory
cd "$(dirname "$0")"

# Check if running in Docker
if [ -f /.dockerenv ]; then
    # In Docker, use the installed package
    if [ $USE_UI -eq 1 ]; then
        python3 -m smolagent.gradio_app
    else
        python3 -m smolagent.cli
    fi
else
    # Build and run Docker container
    docker build -t smolagent .
    
    if [ $USE_UI -eq 1 ]; then
        # Run with Gradio UI
        docker run -it --rm \
            -p 7860:7860 \
            -v "$(pwd)/.env:/app/.env" \
            smolagent python3 -m smolagent.gradio_app
    else
        # Run CLI mode
        docker run -it --rm \
            -v "$(pwd)/.env:/app/.env" \
            smolagent python3 -m smolagent.cli
    fi
fi