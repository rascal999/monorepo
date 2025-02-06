#!/usr/bin/env bash

# Function to print error messages
error() {
    echo "❌ Error: $1" >&2
    exit 1
}

# Function to print success messages
success() {
    echo "✅ $1"
}

# Function to print info messages
info() {
    echo "i️  $1"
}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASEFILES_DIR="$SCRIPT_DIR/basefiles"

# Verify basefiles directory exists
if [ ! -d "$BASEFILES_DIR" ]; then
    error "Basefiles directory not found at $BASEFILES_DIR"
fi

# Build Python base image
info "Building Python base image..."
docker build -t baseimage-python:latest -f "$BASEFILES_DIR/python/Dockerfile" "$BASEFILES_DIR/python" || error "Failed to build Python base image"
success "Python base image built successfully"

# Build Node.js base image
info "Building Node.js base image..."
docker build -t baseimage-node:latest -f "$BASEFILES_DIR/node/Dockerfile" "$BASEFILES_DIR/node" || error "Failed to build Node.js base image"
success "Node.js base image built successfully"

info "Base images are ready to use"
info "You can now create projects using create_project.sh"