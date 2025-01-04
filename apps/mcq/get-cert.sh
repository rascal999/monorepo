#!/bin/bash

# Stop any existing container
docker rm -f cert-nginx 2>/dev/null

# Create directories
mkdir -p certbot
mkdir -p ssl

# Start a simple nginx container for ACME challenge
docker run -d --name cert-nginx \
    -p 80:80 \
    -v $PWD/certbot:/var/www/certbot \
    -v $PWD/cert-nginx.conf:/etc/nginx/conf.d/default.conf:ro \
    nginx:alpine

# Wait for nginx to start
echo "Waiting for nginx to start..."
sleep 5

# Run certbot
docker run --rm \
    -v $PWD/ssl:/etc/letsencrypt \
    -v $PWD/certbot:/var/www/certbot \
    certbot/certbot certonly \
    --webroot \
    --webroot-path /var/www/certbot \
    --email admin@alm.gg \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d alm.gg

# Clean up
docker rm -f cert-nginx
