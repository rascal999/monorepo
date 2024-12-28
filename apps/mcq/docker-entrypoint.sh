#!/bin/sh

# Function to get/renew certificate
get_certificate() {
    # Check if domain is provided via environment variable
    if [ -z "$DOMAIN" ]; then
        echo "Error: DOMAIN environment variable not set"
        exit 1
    }

    # Check if email is provided via environment variable
    if [ -z "$EMAIL" ]; then
        echo "Error: EMAIL environment variable not set"
        exit 1
    }

    # Check if certificate already exists
    if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        echo "Requesting initial certificate for $DOMAIN"
        certbot certonly --nginx \
            --non-interactive \
            --agree-tos \
            --email "$EMAIL" \
            --domains "$DOMAIN" \
            --keep-until-expiring

        if [ $? -ne 0 ]; then
            echo "Failed to obtain SSL certificate"
            exit 1
        fi
    fi
}

# Function to renew certificates
renew_certificates() {
    echo "Renewing certificates"
    certbot renew --nginx --non-interactive
}

# Initial certificate request
get_certificate

# Start periodic certificate renewal in background
while :; do
    renew_certificates
    sleep 12h
done &

# Start nginx in foreground
echo "Starting nginx"
nginx -g "daemon off;"
