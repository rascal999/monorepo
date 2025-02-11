#!/bin/bash

# Create the traefik network
echo "Creating traefik-public network..."
docker network create traefik-public

# Start Traefik
echo "Starting Traefik..."
docker compose up -d

# Start example service
echo "Starting example service..."
docker compose -f example-service.yml up -d

echo "Setup complete! You can now access:"
echo "- Traefik dashboard: http://traefik.host"
echo "- Example service: http://test.mgp.host"
echo
echo "Test DNS resolution:"
echo "  ping test.mgp.host    # Should resolve to 127.0.0.1"
echo "  curl test.mgp.host    # Should show whoami response"