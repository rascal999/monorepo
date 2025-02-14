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

# Function to replace placeholders in a file
replace_placeholders() {
    local file="$1"
    local project_name="$2"
    local env_file="$3"
    local random_port="$4"

    # Create temp file
    local temp_file="$file.tmp"
    
    # Replace placeholders
    sed -e "s/APP_NAME/$project_name/g" \
        -e "s|ENV_FILE_PATH|$env_file|g" \
        -e "s/PORT/$random_port/g" \
        "$file" > "$temp_file"
    
    # Move temp file to original
    mv "$temp_file" "$file"
}

# Function to show project structure
show_structure() {
    eza --long --all --header --icons --git || ls -la
}

# Check if project name is provided
if [ -z "$1" ]; then
    error "Usage: $0 <language> <project-name> - Language can be python or node"
fi

if [ -z "$2" ]; then
    error "Usage: $0 <language> <project-name> - Language can be python or node"
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

# Build base images to ensure we have the latest versions
BASE_IMAGE="baseimage-$LANGUAGE:latest"
info "Building base images..."
if [ -f "$SCRIPT_DIR/build.sh" ]; then
    (cd "$SCRIPT_DIR" && ./build.sh) || error "Failed to build base images"
    success "Base images built successfully"
else
    error "build.sh script not found in $SCRIPT_DIR"
fi

# Verify the centralized .env exists
if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$ENV_EXAMPLE_FILE" ]; then
        error "Centralized .env file not found in $SCRIPT_DIR. Please copy .env.example to .env and configure it: cp $ENV_EXAMPLE_FILE $ENV_FILE"
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
mkdir -p "$TARGET_DIR/$PROJECT_NAME/workspace/logs" || error "Failed to create workspace/logs directory"

# Copy .env.example for reference
cp "$ENV_EXAMPLE_FILE" "$TARGET_DIR/$PROJECT_NAME/.env.example" || error "Failed to copy .env.example"

# Generate random port
RANDOM_PORT=$(( ( RANDOM % 201 ) + 4000 ))

# Copy and configure docker-compose.yml
cp "$TEMPLATES_DIR/docker-compose.yml" "$TARGET_DIR/$PROJECT_NAME/" || error "Failed to copy docker-compose.yml"
replace_placeholders "$TARGET_DIR/$PROJECT_NAME/docker-compose.yml" "$PROJECT_NAME" "$ENV_FILE" "$RANDOM_PORT"

# Copy template files based on language
if [ "$LANGUAGE" == "python" ]; then
    # Copy Python files
    cp "$TEMPLATES_DIR/python/Dockerfile" "$TARGET_DIR/$PROJECT_NAME/Dockerfile" || error "Failed to copy Python Dockerfile"
    cp "$TEMPLATES_DIR/python/.gitignore" "$TARGET_DIR/$PROJECT_NAME/.gitignore" || error "Failed to copy .gitignore"
    cp "$TEMPLATES_DIR/python/.dockerignore" "$TARGET_DIR/$PROJECT_NAME/.dockerignore" || error "Failed to copy .dockerignore"
    cp "$TEMPLATES_DIR/python/main.py" "$TARGET_DIR/$PROJECT_NAME/app/main.py" || error "Failed to copy main.py"
    
    # Copy tests directory
    cp -r "$TEMPLATES_DIR/python/tests" "$TARGET_DIR/$PROJECT_NAME/" || error "Failed to copy test files"
    
    # Replace APP_NAME in main.py and test files
    replace_placeholders "$TARGET_DIR/$PROJECT_NAME/app/main.py" "$PROJECT_NAME" "" ""
    replace_placeholders "$TARGET_DIR/$PROJECT_NAME/tests/test_main.py" "$PROJECT_NAME" "" ""
    
    # Create empty requirements.txt
    echo "# $PROJECT_NAME Requirements" > "$TARGET_DIR/$PROJECT_NAME/requirements.txt"
    
    # Create run script for Python that runs tests first
    cat <<EOF > "$TARGET_DIR/$PROJECT_NAME/run.sh"
#!/usr/bin/env bash
# Run tests first
docker-compose run --rm --build app pytest /app/tests/ || exit 1
# If tests pass, run the main application
docker-compose run --rm app python /app/app/main.py "\${@:1}"
EOF

elif [ "$LANGUAGE" == "node" ]; then
    # Copy Node.js files
    cp "$TEMPLATES_DIR/node/Dockerfile" "$TARGET_DIR/$PROJECT_NAME/Dockerfile" || error "Failed to copy Node.js Dockerfile"
    cp "$TEMPLATES_DIR/node/.gitignore" "$TARGET_DIR/$PROJECT_NAME/.gitignore" || error "Failed to copy .gitignore"
    cp "$TEMPLATES_DIR/node/.dockerignore" "$TARGET_DIR/$PROJECT_NAME/.dockerignore" || error "Failed to copy .dockerignore"
    cp "$TEMPLATES_DIR/node/index.js" "$TARGET_DIR/$PROJECT_NAME/app/index.js" || error "Failed to copy index.js"
    
    # Create package.json
    cat <<EOF > "$TARGET_DIR/$PROJECT_NAME/package.json"
{
  "name": "$PROJECT_NAME",
  "version": "1.0.0",
  "main": "app/index.js",
  "scripts": {
    "start": "node app/index.js"
  }
}
EOF

    # Create run script for Node.js
    cat <<EOF > "$TARGET_DIR/$PROJECT_NAME/run.sh"
#!/usr/bin/env bash
docker-compose run --rm --build app node index.js "\${@:1}"
EOF
fi

chmod +x "$TARGET_DIR/$PROJECT_NAME/run.sh"

# Create README.md
cat <<EOF > "$TARGET_DIR/$PROJECT_NAME/README.md"
# $PROJECT_NAME

## Setup
1. Ensure Docker is installed and running
2. Run \`./run.sh\` to start the application
   * You can pass arguments to the application: \`./run.sh arg1 arg2\`
   * Use \`./run.sh --help\` to see available options

## Development
- Source code in \`app/\` directory
- Workspace files in \`workspace/\` directory
- Environment variables are managed in the central .env file at $ENV_FILE
- See .env.example for available environment variables
- The application runs on port $RANDOM_PORT
- The application will:
  * Output environment variables to stdout (sensitive values masked)
  * Save logs to workspace/logs/[timestamp]-[container-id].log

## Logging
- Uses Python's built-in logging module (Python) or file system (Node.js)
- Log level controlled by LOG_LEVEL environment variable
- Log directory controlled by LOG_DIRECTORY environment variable
- Logs include timestamp and container ID
- Sensitive values (containing 'KEY' or 'TOKEN') are masked:
  * Long values: First 12 and last 3 visible
  * Medium values: All but last 3 visible
  * Short values: Shown as is

## Troubleshooting
- Check Docker logs: \`docker-compose logs\`
- Rebuild container: \`docker-compose build --no-cache\`
EOF

success "Project '$PROJECT_NAME' initialized successfully!"
info "Project created at: $TARGET_DIR/$PROJECT_NAME"
info "Random port assigned: $RANDOM_PORT"

cd "$TARGET_DIR/$PROJECT_NAME" || error "Failed to change to project directory"
./run.sh && show_structure

# Write path to temp file for cum to use
echo "$TARGET_DIR/$PROJECT_NAME" > /tmp/cum_last_project