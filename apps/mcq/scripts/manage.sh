#!/usr/bin/env bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( dirname "$SCRIPT_DIR" )"

# Change to project directory
cd "$PROJECT_DIR"

# Function to start development environment
dev() {
    echo "Starting development environment..."
    
    # Start database with dev configuration
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d db
    
    # Install dependencies if needed
    [ ! -d "node_modules" ] && npm install
    [ ! -d "api/node_modules" ] && (cd api && npm install)
    
    # Function to start services using screen or tmux
    start_services() {
        if command -v screen >/dev/null 2>&1; then
            # Use screen if available
            screen -dmS mcq-frontend bash -c "cd '$PROJECT_DIR' && npm run dev"
            screen -dmS mcq-api bash -c "cd '$PROJECT_DIR/api' && npm run dev"
            echo "Development environment started (using screen)"
            echo "Use 'screen -r mcq-frontend' or 'screen -r mcq-api' to view output"
        elif command -v tmux >/dev/null 2>&1; then
            # Use tmux if available
            tmux new-session -d -s mcq-frontend "cd '$PROJECT_DIR' && npm run dev"
            tmux new-session -d -s mcq-api "cd '$PROJECT_DIR/api' && npm run dev"
            echo "Development environment started (using tmux)"
            echo "Use 'tmux attach -t mcq-frontend' or 'tmux attach -t mcq-api' to view output"
        else
            # Fallback to background processes with log files
            (cd "$PROJECT_DIR" && npm run dev > frontend.log 2>&1) &
            (cd "$PROJECT_DIR/api" && npm run dev > api.log 2>&1) &
            echo "Development environment started (using background processes)"
            echo "View logs in frontend.log and api.log"
        fi
    }
    
    start_services
}

# Function to stop development environment
dev_stop() {
    echo "Stopping development environment..."
    
    # Stop database
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
    
    # Stop screen sessions if they exist
    if command -v screen >/dev/null 2>&1; then
        screen -S mcq-frontend -X quit 2>/dev/null
        screen -S mcq-api -X quit 2>/dev/null
    fi
    
    # Stop tmux sessions if they exist
    if command -v tmux >/dev/null 2>&1; then
        tmux kill-session -t mcq-frontend 2>/dev/null
        tmux kill-session -t mcq-api 2>/dev/null
    fi
    
    # Kill any remaining npm processes
    pkill -f "node.*apps/mcq" 2>/dev/null
    
    # Clean up log files
    rm -f frontend.log api.log
    
    echo "Development environment stopped"
}

# Function to display usage instructions
usage() {
    echo "Usage: $0 [start|stop|restart|clean|logs|versions|update|dev|dev-stop]"
    echo
    echo "Commands:"
    echo "  start     - Start the application stack (VERSION=x.y.z ENV=prod for specific version)"
    echo "  stop      - Stop the application stack"
    echo "  restart   - Restart the application stack"
    echo "  clean     - Stop containers and clean up volumes/certificates"
    echo "  logs      - Show logs from all services"
    echo "  versions  - List available versions"
    echo "  update    - Pull latest changes and fetch tags"
    echo "  dev       - Start development environment (database in Docker, frontend/API with npm)"
    echo "  dev-stop  - Stop development environment"
    echo
    echo "Environment Variables:"
    echo "  VERSION  - Specify version to deploy (e.g., VERSION=1.0.0)"
    echo "  ENV      - Specify environment (e.g., ENV=prod)"
    echo
    exit 1
}

# Function to check SSL requirements
check_ssl_requirements() {
    local use_ssl=${USE_SSL:-false}
    
    # Source .env file if it exists and USE_SSL not set via environment
    if [ -z "${USE_SSL+x}" ] && [ -f .env ]; then
        # Extract USE_SSL value from .env file
        use_ssl=$(grep "^USE_SSL=" .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")
    fi

    # Check if SSL is enabled
    if [ "$use_ssl" = "true" ]; then
        # Get domain from environment or .env file
        local domain=${DOMAIN:-localhost}
        if [ -z "${DOMAIN+x}" ] && [ -f .env ]; then
            domain=$(grep "^DOMAIN=" .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")
        fi

        # Check for SSL certificates in both possible locations
        if { [ ! -d "ssl" ] || [ ! -f "ssl/fullchain.pem" ] || [ ! -f "ssl/privkey.pem" ]; } && \
           { [ ! -d "/etc/letsencrypt/live/$domain" ] || [ ! -f "/etc/letsencrypt/live/$domain/fullchain.pem" ] || [ ! -f "/etc/letsencrypt/live/$domain/privkey.pem" ]; }; then
            echo "Error: SSL is enabled (USE_SSL=true) but SSL certificates are missing."
            echo "Please run scripts/get-cert.sh to generate SSL certificates before starting the application."
            exit 1
        fi
        
        # If certs exist in /etc/letsencrypt but not in ssl/, copy them
        if [ ! -f "ssl/fullchain.pem" ] && [ -f "/etc/letsencrypt/live/$domain/fullchain.pem" ]; then
            mkdir -p ssl
            cp "/etc/letsencrypt/live/$domain/fullchain.pem" ssl/
            cp "/etc/letsencrypt/live/$domain/privkey.pem" ssl/
            chmod 644 ssl/*.pem
        fi
    fi
}

# Function to start the application
start() {
    local version=${VERSION:-latest}
    local env=${ENV:-prod}
    
    # Check SSL requirements before starting
    check_ssl_requirements
    
    echo "Starting MCQ application stack..."
    echo "Version: $version"
    echo "Environment: $env"
    
    if [ "$version" != "latest" ]; then
        frontend_tag="mcq_frontend:v${version}-${env}"
        api_tag="mcq_api:v${version}-${env}"

        # Check if images exist locally
        if docker image inspect "$frontend_tag" >/dev/null 2>&1 && docker image inspect "$api_tag" >/dev/null 2>&1; then
            echo "Using local images..."
        else
            echo "Building images..."
            docker-compose build
        fi

        # Tag as latest for docker-compose
        docker tag "$frontend_tag" mcq_frontend:latest 2>/dev/null || true
        docker tag "$api_tag" mcq_api:latest 2>/dev/null || true
    fi

    docker-compose up -d --build
    echo "Application started. Use '$0 logs' to view logs."
}

# Function to stop the application
stop() {
    echo "Stopping MCQ application stack..."
    docker-compose down
    echo "Application stopped."
}

# Function to clean up everything
cleanup() {
    echo "Cleaning up MCQ application..."
    
    # Stop all containers
    docker-compose down
    
    # Remove SSL-related directories
    echo "Removing SSL certificates and related files..."
    rm -rf ssl/* certbot/*
    
    # Remove tagged images
    echo "Removing tagged images..."
    docker images "mcq_frontend:v*" --format "{{.ID}}" | xargs -r docker rmi -f
    docker images "mcq_api:v*" --format "{{.ID}}" | xargs -r docker rmi -f
    
    # Remove any dangling images
    echo "Removing dangling Docker images..."
    docker image prune -f
    
    echo "Cleanup complete."
}

# Function to show logs
show_logs() {
    echo "Showing logs from all services (Ctrl+C to exit)..."
    docker-compose logs -f
}

# Function to list versions
list_versions() {
    echo "Available versions:"
    echo
    echo "Frontend:"
    docker images "mcq_frontend:v*" --format "table {{.Tag}}\t{{.CreatedAt}}"
    echo
    echo "API:"
    docker images "mcq_api:v*" --format "table {{.Tag}}\t{{.CreatedAt}}"
    echo
    echo "Git tags:"
    git tag -l "mcq/v*" --sort=-v:refname | head -n 5
}

# Function to update repository
update() {
    echo "Updating repository..."
    git pull
    echo "Fetching tags..."
    git fetch --tags
    echo "Update complete. Latest tags:"
    git tag -l "mcq/v*" --sort=-v:refname | head -n 5
}

# Main script logic
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        echo "Waiting for containers to stop completely..."
        sleep 5
        start
        ;;
    clean)
        cleanup
        ;;
    logs)
        show_logs
        ;;
    versions)
        list_versions
        ;;
    update)
        update
        ;;
    dev)
        dev
        ;;
    dev-stop)
        dev_stop
        ;;
    *)
        usage
        ;;
esac
