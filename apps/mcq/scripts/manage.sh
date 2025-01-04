#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( dirname "$SCRIPT_DIR" )"

# Change to project directory
cd "$PROJECT_DIR"

# Function to display usage instructions
usage() {
    echo "Usage: $0 [start|stop|restart|clean|logs]"
    echo
    echo "Commands:"
    echo "  start   - Start the application stack"
    echo "  stop    - Stop the application stack"
    echo "  restart - Restart the application stack"
    echo "  clean   - Stop containers and clean up volumes/certificates"
    echo "  logs    - Show logs from all services"
    echo
    exit 1
}

# Function to start the application
start() {
    echo "Starting MCQ application stack..."
    docker-compose up -d
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
    *)
        usage
        ;;
esac
