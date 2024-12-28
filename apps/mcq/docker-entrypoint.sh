#!/bin/sh

# Function to replace environment variables in nginx config
setup_nginx_conf() {
    local template=$1
    local output=$2
    echo "Setting up nginx configuration from $template..."
    envsubst '${DOMAIN}' < "$template" > "$output"
}

# Function to wait for nginx to be ready
wait_for_nginx() {
    echo "Waiting for nginx to start..."
    timeout=30
    while [ $timeout -gt 0 ]; do
        if curl -s http://localhost/.well-known/acme-challenge/ > /dev/null; then
            echo "Nginx is ready"
            return 0
        fi
        timeout=$((timeout-1))
        sleep 1
    done
    echo "Nginx failed to start"
    return 1
}

# Function to get/renew certificate
get_certificate() {
    # Check if domain is provided via environment variable
    if [ -z "$DOMAIN" ]; then
        echo "Error: DOMAIN environment variable not set"
        exit 1
    fi

    # Check if email is provided via environment variable
    if [ -z "$EMAIL" ]; then
        echo "Error: EMAIL environment variable not set"
        exit 1
    fi

    # Ensure webroot directory exists and is accessible
    mkdir -p /var/www/certbot
    chmod -R 755 /var/www/certbot

    # Setup and start nginx with HTTP-only config
    echo "Starting nginx with HTTP-only configuration..."
    setup_nginx_conf /etc/nginx/nginx.http.conf /etc/nginx/conf.d/default.conf
    
    nginx
    
    # Wait for nginx to be ready
    if ! wait_for_nginx; then
        echo "Failed to start nginx"
        exit 1
    fi

    # Request certificate
    echo "Requesting initial certificate for $DOMAIN"
    certbot certonly --webroot \
        --webroot-path /var/www/certbot \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        --domains "$DOMAIN" \
        --keep-until-expiring \
        --debug-challenges

    local cert_exit_code=$?
    
    # Stop nginx after certificate request
    nginx -s stop
    sleep 2

    if [ $cert_exit_code -ne 0 ]; then
        echo "Failed to obtain SSL certificate"
        exit 1
    fi
}

# Function to renew certificates
renew_certificates() {
    echo "Renewing certificates"
    certbot renew --webroot --webroot-path /var/www/certbot --non-interactive
}

# Create webroot directory for certbot
mkdir -p /var/www/certbot
chmod -R 755 /var/www/certbot

# Get initial certificate
get_certificate

# Setup nginx with SSL configuration
echo "Setting up SSL nginx configuration..."
setup_nginx_conf /etc/nginx/nginx.ssl.conf /etc/nginx/conf.d/default.conf

# Start periodic certificate renewal in background
while :; do
    sleep 12h
    renew_certificates
done &

# Start nginx with SSL configuration
echo "Starting nginx with SSL configuration"
exec nginx -g "daemon off;"
