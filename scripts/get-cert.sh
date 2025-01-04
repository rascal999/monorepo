#!/usr/bin/env bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( dirname "$SCRIPT_DIR" )"

# Change to project directory
cd "$PROJECT_DIR"

# Source environment variables
if [ -f .env ]; then
    source .env
fi

# Stop any existing container
docker rm -f cert-nginx 2>/dev/null

# Create directories
mkdir -p certbot ssl

# Start a simple nginx container for ACME challenge
docker run -d --name cert-nginx \
    -p 80:80 \
    -v $PWD/certbot:/var/www/certbot \
    -v $PWD/scripts/cert-nginx.conf:/etc/nginx/conf.d/default.conf:ro \
    nginx:alpine

# Wait for nginx to start
echo "Waiting for nginx to start..."
sleep 5

# Run certbot
CERTBOT_ARGS="certonly --webroot --webroot-path /var/www/certbot --email admin@alm.gg --agree-tos --no-eff-email --force-renewal"

# Add staging flag if CERTBOT_STAGING is true
if [ "$CERTBOT_STAGING" = "true" ]; then
    CERTBOT_ARGS="$CERTBOT_ARGS --staging"
fi

docker run --rm \
    -v $PWD/ssl:/etc/letsencrypt \
    -v $PWD/certbot:/var/www/certbot \
    certbot/certbot $CERTBOT_ARGS \
    -d alm.gg

# Clean up
docker rm -f cert-nginx
