#!/bin/bash

# Directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to script directory to ensure docker-compose.yml is accessible
cd "$SCRIPT_DIR"

# Function to display usage instructions
usage() {
    echo "Usage: $0 [start|stop|restart|clean|logs|setup-tls]"
    echo
    echo "Commands:"
    echo "  start     - Start the application stack in HTTP mode"
    echo "  stop      - Stop the application stack"
    echo "  restart   - Restart the application stack"
    echo "  clean     - Stop containers and clean up volumes/certificates"
    echo "  logs      - Show logs from all services"
    echo "  setup-tls - Configure TLS with Let's Encrypt"
    echo
    exit 1
}

# Function to start the application
start() {
    echo "Starting MCQ application stack in HTTP mode..."
    USE_SSL=false docker-compose up -d
    echo "Application started. Use '$0 logs' to view logs."
}

# Function to setup TLS
setup_tls() {
    echo "Setting up TLS with Let's Encrypt..."
    
    # Verify nginx is accessible
    echo "Verifying HTTP access..."
    for i in $(seq 1 12); do
        if curl -s -f http://localhost/ > /dev/null 2>&1; then
            echo "HTTP access verified"
            break
        fi
        if [ $i -eq 12 ]; then
            echo "Error: Cannot access nginx on HTTP. Please check your configuration."
            exit 1
        fi
        echo "Waiting for HTTP access... (attempt $i/12)"
        sleep 5
    done
    
    # Stop current stack
    docker-compose down
    
    # Start with SSL enabled
    echo "Restarting with SSL enabled..."
    USE_SSL=true docker-compose up -d
    
    echo "TLS setup initiated. Use '$0 logs' to monitor the certificate acquisition process."
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
    setup-tls)
        setup_tls
        ;;
    *)
        usage
        ;;
esac
