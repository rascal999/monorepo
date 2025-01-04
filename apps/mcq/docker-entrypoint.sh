#!/bin/sh

# Function to start nginx and handle SSL if needed
start_server() {
    echo "Starting nginx with HTTP configuration..."
    envsubst '${DOMAIN}' < /etc/nginx/nginx.http.conf > /etc/nginx/conf.d/default.conf
    
    # Start nginx in HTTP mode
    nginx
    
    # Wait for nginx to start and verify it's responding
    echo "Waiting for nginx to be accessible..."
    until curl -s -f http://localhost/ > /dev/null 2>&1; do
        echo "Waiting for nginx to respond..."
        sleep 5
    done
    echo "Nginx is responding correctly"

    # Create and verify certbot directories
    echo "Setting up certbot directories..."
    mkdir -p /var/www/certbot/.well-known/acme-challenge
    chmod -R 755 /var/www/certbot
    echo "test" > /var/www/certbot/.well-known/acme-challenge/test.txt
    
    # Verify ACME challenge directory is accessible
    echo "Verifying ACME challenge path..."
    if curl -s -f http://localhost/.well-known/acme-challenge/test.txt > /dev/null 2>&1; then
        echo "ACME challenge path is accessible"
        rm /var/www/certbot/.well-known/acme-challenge/test.txt
    else
        echo "Warning: ACME challenge path is not accessible"
        echo "Continuing with HTTP only"
        nginx -g 'daemon off;'
        exit 0
    fi
    
    if [ "${USE_SSL}" = "true" ]; then
        echo "Waiting 30s for DNS propagation..."
        sleep 30
        
        echo "Testing domain resolution..."
        if ! host "${DOMAIN}" > /dev/null 2>&1; then
            echo "Warning: Domain ${DOMAIN} cannot be resolved"
            echo "Continuing with HTTP only. Please check DNS configuration."
            nginx -g 'daemon off;'
            exit 0
        fi
        
        echo "Attempting to obtain SSL certificate..."
        CERTBOT_ARGS="--webroot --webroot-path /var/www/certbot --domain ${DOMAIN} --email ${EMAIL} --agree-tos --non-interactive"
        
        if [ "${CERTBOT_STAGING:-true}" = "true" ]; then
            echo "Using Let's Encrypt staging environment..."
            CERTBOT_ARGS="$CERTBOT_ARGS --staging"
        else
            echo "Using Let's Encrypt production environment..."
        fi
        
        certbot certonly $CERTBOT_ARGS
        
        if [ $? -eq 0 ]; then
            echo "Successfully obtained SSL certificate. Switching to HTTPS..."
            # Switch to SSL configuration
            envsubst '${DOMAIN}' < /etc/nginx/nginx.ssl.conf > /etc/nginx/conf.d/default.conf
            nginx -s reload
            
            # Set up auto-renewal in background
            while :; do
                sleep 12h
                echo "Running certificate renewal check..."
                certbot renew --webroot --webroot-path /var/www/certbot
            done &
            
            # Keep nginx running
            nginx -g 'daemon off;'
        else
            echo "Failed to obtain SSL certificate. Continuing with HTTP only..."
            nginx -g 'daemon off;'
        fi
    else
        echo "SSL not requested. Running with HTTP only..."
        nginx -g 'daemon off;'
    fi
}

# Main script
echo "Starting server..."
start_server
