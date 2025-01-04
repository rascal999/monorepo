#!/usr/bin/env bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( dirname "$SCRIPT_DIR" )"

# Change to project directory
cd "$PROJECT_DIR"

# Function to display usage instructions
usage() {
    echo "Usage: $0 [start|stop|restart|clean|logs|versions]"
    echo
    echo "Commands:"
    echo "  start    - Start the application stack (VERSION=x.y.z ENV=prod for specific version)"
    echo "  stop     - Stop the application stack"
    echo "  restart  - Restart the application stack"
    echo "  clean    - Stop containers and clean up volumes/certificates"
    echo "  logs     - Show logs from all services"
    echo "  versions - List available versions"
    echo
    echo "Environment Variables:"
    echo "  VERSION  - Specify version to deploy (e.g., VERSION=1.0.0)"
    echo "  ENV      - Specify environment (e.g., ENV=prod)"
    echo
    exit 1
}

# Function to start the application
start() {
    local version=${VERSION:-latest}
    local env=${ENV:-prod}
    
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
    *)
        usage
        ;;
esac
