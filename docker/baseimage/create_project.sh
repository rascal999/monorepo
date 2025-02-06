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

# Check if project name is provided
if [ -z "$1" ]; then
    error "Usage: $0 <language> <project-name>\nLanguage can be python or node"
fi

if [ -z "$2" ]; then
    error "Usage: $0 <language> <project-name>\nLanguage can be python or node"
fi

LANGUAGE=$1
PROJECT_NAME=$2
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TARGET_DIR=$(pwd)  # Directory where the command was run
ENV_FILE="$SCRIPT_DIR/.env"
ENV_EXAMPLE_FILE="$SCRIPT_DIR/.env.example"
TEMPLATES_DIR="$SCRIPT_DIR/templates"

# Validate language
if [[ ! "$LANGUAGE" =~ ^(python|node)$ ]]; then
    error "Invalid language. Must be 'python' or 'node'"
fi

# Check if required base image exists
BASE_IMAGE="baseimage-$LANGUAGE:latest"
if ! docker image inspect "$BASE_IMAGE" >/dev/null 2>&1; then
    error "Base image '$BASE_IMAGE' not found.\nPlease run './build.sh' first to build the base images."
fi

# Verify the centralized .env exists
if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$ENV_EXAMPLE_FILE" ]; then
        error "Centralized .env file not found in $SCRIPT_DIR\nPlease copy .env.example to .env and configure it:\n\ncp $ENV_EXAMPLE_FILE $ENV_FILE\n"
    else
        error "Neither .env nor .env.example found in $SCRIPT_DIR"
    fi
fi

# Verify templates directory exists
if [ ! -d "$TEMPLATES_DIR" ]; then
    error "Templates directory not found at $TEMPLATES_DIR"
fi

# Check if project directory already exists
if [ -d "$TARGET_DIR/$PROJECT_NAME" ]; then
    error "Project directory '$PROJECT_NAME' already exists"
fi

info "Creating project structure..."

# Create project structure
mkdir -p "$TARGET_DIR/$PROJECT_NAME/app" || error "Failed to create project directories"

# Copy template files
if [ "$LANGUAGE" == "python" ]; then
    # Copy Python files
    cp "$TEMPLATES_DIR/python/Dockerfile" "$TARGET_DIR/$PROJECT_NAME/Dockerfile" || error "Failed to copy Python Dockerfile to project"
    cp "$TEMPLATES_DIR/python/.gitignore" "$TARGET_DIR/$PROJECT_NAME/.gitignore" || error "Failed to copy Python .gitignore"
    cp "$TEMPLATES_DIR/python/.dockerignore" "$TARGET_DIR/$PROJECT_NAME/.dockerignore" || error "Failed to copy Python .dockerignore"
    
    # Create Python test file that returns environment
    cat <<EOF > "$TARGET_DIR/$PROJECT_NAME/app/main.py" || error "Failed to create main.py"
import os
import json

def main():
    # Get all environment variables
    env_vars = dict(os.environ)
    
    # Convert to JSON for pretty printing
    print(json.dumps(env_vars, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
EOF
    
    echo "# $PROJECT_NAME Requirements" > "$TARGET_DIR/$PROJECT_NAME/requirements.txt" || error "Failed to create requirements.txt"
    
elif [ "$LANGUAGE" == "node" ]; then
    # Copy Node.js files
    cp "$TEMPLATES_DIR/node/Dockerfile" "$TARGET_DIR/$PROJECT_NAME/Dockerfile" || error "Failed to copy Node.js Dockerfile to project"
    cp "$TEMPLATES_DIR/node/.gitignore" "$TARGET_DIR/$PROJECT_NAME/.gitignore" || error "Failed to copy Node.js .gitignore"
    cp "$TEMPLATES_DIR/node/.dockerignore" "$TARGET_DIR/$PROJECT_NAME/.dockerignore" || error "Failed to copy Node.js .dockerignore"
    
    # Create Node.js test file that returns environment
    cat <<EOF > "$TARGET_DIR/$PROJECT_NAME/app/index.js" || error "Failed to create index.js"
// Get all environment variables and print them
console.log(JSON.stringify(process.env, null, 2));
EOF
    
    # Create package.json
    cat <<EOF > "$TARGET_DIR/$PROJECT_NAME/package.json" || error "Failed to create package.json"
{
  "name": "$PROJECT_NAME",
  "version": "1.0.0",
  "main": "app/index.js",
  "scripts": {
    "start": "node app/index.js"
  }
}
EOF
fi

# Generate docker-compose.yml with resource limits
RANDOM_PORT=$(( ( RANDOM % 201 ) + 4000 ))
cat <<EOF > "$TARGET_DIR/$PROJECT_NAME/docker-compose.yml" || error "Failed to create docker-compose.yml"
version: '3.8'

services:
  $PROJECT_NAME:
    build:
      context: .
      dockerfile: Dockerfile
    env_file:
      - $ENV_FILE    # Reference centralized .env with absolute path
    volumes:
      - ./app:/app
    ports:
      - "\${RANDOM_PORT:-$RANDOM_PORT}:8000"
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
EOF

# Create run script with portable shebang
cat <<EOF > "$TARGET_DIR/$PROJECT_NAME/run.sh" || error "Failed to create run.sh"
#!/usr/bin/env bash
docker-compose up
EOF
chmod +x "$TARGET_DIR/$PROJECT_NAME/run.sh" || error "Failed to make run.sh executable"

# Create README.md
cat <<EOF > "$TARGET_DIR/$PROJECT_NAME/README.md" || error "Failed to create README.md"
# $PROJECT_NAME

## Setup
1. Ensure Docker is installed and running
2. Run \`./run.sh\` to start the application

## Development
- Source code is in the \`app/\` directory
- Environment variables are managed in the central .env file at $ENV_FILE
- The application runs on port $RANDOM_PORT
- The application will output all environment variables when run

## Troubleshooting
- Check Docker logs: \`docker-compose logs\`
- Rebuild container: \`docker-compose build --no-cache\`
EOF

success "Project '$PROJECT_NAME' initialized successfully!"
info "Project created at: $TARGET_DIR/$PROJECT_NAME"
info "Random port assigned: $RANDOM_PORT"
info "Run './run.sh' to start the application and see environment variables"