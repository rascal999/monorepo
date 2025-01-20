#!/usr/bin/env bash
# Setup development environment for postman2pytest

# Exit on error
set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Determine shell and source appropriate activation script
SHELL_NAME="$(basename "$SHELL")"
case "$SHELL_NAME" in
    "zsh")
        source venv/bin/activate
        ;;
    "bash")
        source venv/bin/activate
        ;;
    *)
        echo "Unsupported shell: $SHELL_NAME"
        echo "Please activate the virtual environment manually:"
        echo "source venv/bin/activate"
        exit 1
        ;;
esac

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

# Install package in development mode
echo "Installing package in development mode..."
python3 -m pip install -e .

# Run initial code formatting
echo "Running code formatting..."
python3 -m black src tests

# Run type checking
echo "Running type checking..."
python3 -m mypy src tests

# Run linting
echo "Running linting..."
python3 -m flake8 src tests

# Run tests
echo "Running tests..."
python3 -m pytest

echo "Development environment setup complete!"
echo "Activate the virtual environment with: source venv/bin/activate"
