#!/bin/sh

# Clear any existing configuration
rm -f /etc/nginx/conf.d/default.conf

# Choose configuration based on SSL setting
if [ "${USE_SSL}" = "true" ] && [ -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
    echo "Starting with HTTPS configuration..."
    envsubst '${DOMAIN}' < /etc/nginx/nginx.ssl.conf > /etc/nginx/conf.d/default.conf
    
    # Start nginx in background
    echo "Starting nginx..."
    nginx &
    
    # Set up auto-renewal in background
    echo "Setting up certificate renewal..."
    while :; do
        certbot renew --webroot --webroot-path /var/www/certbot
        sleep 12h
    done &
    
    # Wait for all background processes
    wait
else
    echo "Starting with HTTP configuration..."
    envsubst '${DOMAIN}' < /etc/nginx/nginx.http.conf > /etc/nginx/conf.d/default.conf
    nginx -g 'daemon off;'
fi
