#!/bin/sh

# Function to replace environment variables in nginx config
setup_nginx_conf() {
    envsubst '${DOMAIN}' < /etc/nginx/conf.d/default.conf > /etc/nginx/conf.d/default.conf.tmp
    mv /etc/nginx/conf.d/default.conf.tmp /etc/nginx/conf.d/default.conf
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

    # Start nginx temporarily for domain validation
    nginx

    # Request certificate
    echo "Requesting initial certificate for $DOMAIN"
    certbot certonly --webroot \
        --webroot-path /var/www/certbot \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        --domains "$DOMAIN" \
        --keep-until-expiring

    if [ $? -ne 0 ]; then
        echo "Failed to obtain SSL certificate"
        exit 1
    fi

    # Stop nginx after obtaining certificate
    nginx -s stop
}

# Function to renew certificates
renew_certificates() {
    echo "Renewing certificates"
    certbot renew --webroot --webroot-path /var/www/certbot --non-interactive
}

# Initial setup
setup_nginx_conf

# Create webroot directory for certbot
mkdir -p /var/www/certbot

# Get initial certificate
get_certificate

# Start periodic certificate renewal in background
while :; do
    sleep 12h
    renew_certificates
done &

# Start nginx with full configuration
echo "Starting nginx with SSL configuration"
nginx -g "daemon off;"
