#!/bin/sh

# Function to start nginx with HTTP-only configuration
start_http() {
    echo "Starting nginx with HTTP-only configuration..."
    echo "Setting up nginx configuration from /etc/nginx/nginx.http.conf..."
    envsubst '${DOMAIN}' < /etc/nginx/nginx.http.conf > /etc/nginx/conf.d/default.conf
    nginx -g 'daemon off;'
}

# Function to start nginx with HTTPS configuration
start_https() {
    echo "Starting nginx with HTTPS configuration..."
    
    # Check if we already have a certificate
    if [ -d "/etc/letsencrypt/live/${DOMAIN}" ]; then
        echo "Found existing certificate for ${DOMAIN}"
    else
        echo "Requesting initial certificate for ${DOMAIN}"
        certbot certonly --webroot \
            --webroot-path /var/www/certbot \
            --domain ${DOMAIN} \
            --email ${EMAIL} \
            --agree-tos \
            --non-interactive \
            --keep-until-expiring
        
        if [ $? -ne 0 ]; then
            echo "Failed to obtain SSL certificate"
            exit 1
        fi
    fi
    
    echo "Setting up nginx configuration from /etc/nginx/nginx.ssl.conf..."
    envsubst '${DOMAIN}' < /etc/nginx/nginx.ssl.conf > /etc/nginx/conf.d/default.conf
    
    # Start nginx
    echo "Starting nginx..."
    nginx -g 'daemon off;' &
    
    # Trap SIGTERM and forward it to nginx
    trap "nginx -s quit" SIGTERM
    
    # Renew certificates automatically
    while :; do
        certbot renew --webroot --webroot-path /var/www/certbot
        sleep 12h
    done
}

# Main script
echo "Waiting for nginx to start..."

if [ "${USE_SSL}" = "true" ]; then
    start_https
else
    start_http
fi
