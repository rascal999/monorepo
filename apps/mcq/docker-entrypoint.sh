#!/bin/sh

# Function to start nginx in HTTP mode
start_http() {
    echo "Starting nginx in HTTP mode..."
    
    # Clear any existing configuration
    rm -f /etc/nginx/conf.d/default.conf
    
    # Set up HTTP configuration
    echo "Setting up HTTP configuration..."
    envsubst '${DOMAIN}' < /etc/nginx/nginx.http.conf > /etc/nginx/conf.d/default.conf
    
    # Start nginx
    echo "Starting nginx..."
    nginx -g 'daemon off;'
}

# Function to start nginx in HTTPS mode
start_https() {
    echo "Starting nginx for HTTPS setup..."
    
    # Clear any existing configuration and certificates
    rm -f /etc/nginx/conf.d/default.conf
    rm -rf /etc/letsencrypt/live/*
    rm -rf /etc/letsencrypt/archive/*
    rm -rf /etc/letsencrypt/renewal/*
    rm -rf /var/www/certbot/.well-known/acme-challenge/*
    
    # Set up HTTP configuration for ACME challenge
    echo "Setting up initial HTTP configuration..."
    envsubst '${DOMAIN}' < /etc/nginx/nginx.http.conf > /etc/nginx/conf.d/default.conf
    
    # Start nginx in background
    nginx
    
    # Set up certbot directories
    echo "Setting up certbot directories..."
    mkdir -p /var/www/certbot/.well-known/acme-challenge
    chmod -R 755 /var/www/certbot
    
    echo "Testing domain resolution..."
    if ! host "${DOMAIN}" > /dev/null 2>&1; then
        echo "Error: Domain ${DOMAIN} cannot be resolved"
        exit 1
    fi
    
    echo "Obtaining SSL certificate..."
    if [ "${CERTBOT_STAGING:-true}" = "true" ]; then
        echo "Using Let's Encrypt staging environment..."
        certbot certonly \
            --webroot \
            --webroot-path /var/www/certbot \
            --domain ${DOMAIN} \
            --email ${EMAIL} \
            --agree-tos \
            --non-interactive \
            --staging \
            --break-my-certs
    else
        echo "Using Let's Encrypt production environment..."
        certbot certonly \
            --webroot \
            --webroot-path /var/www/certbot \
            --domain ${DOMAIN} \
            --email ${EMAIL} \
            --agree-tos \
            --non-interactive
    fi
    
    if [ $? -eq 0 ]; then
        echo "Successfully obtained SSL certificate"
        
        # Switch to SSL configuration
        envsubst '${DOMAIN}' < /etc/nginx/nginx.ssl.conf > /etc/nginx/conf.d/default.conf
        
        # Reload nginx with new configuration
        nginx -s reload
        
        # Set up auto-renewal in background
        while :; do
            sleep 12h
            echo "Running certificate renewal check..."
            certbot renew --webroot --webroot-path /var/www/certbot
        done &
        
        # Keep nginx running
        wait
    else
        echo "Failed to obtain SSL certificate"
        exit 1
    fi
}

# Main script
echo "Starting server..."
if [ "${USE_SSL}" = "true" ]; then
    start_https
else
    start_http
fi
