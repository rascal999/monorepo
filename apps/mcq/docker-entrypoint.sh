#!/bin/sh

# Function to start nginx with HTTP configuration
start_http() {
    echo "Starting nginx with HTTP configuration..."
    echo "Setting up nginx configuration from /etc/nginx/nginx.http.conf..."
    envsubst '${DOMAIN}' < /etc/nginx/nginx.http.conf > /etc/nginx/conf.d/default.conf
    nginx -g 'daemon off;' &
    
    # Wait for nginx to start and verify it's responding
    echo "Waiting for nginx to be accessible..."
    until curl -s -f http://localhost/.well-known/acme-challenge/ > /dev/null 2>&1; do
        sleep 2
    done
    echo "Nginx is responding correctly"
    
    if [ "${USE_SSL}" = "true" ]; then
        echo "Waiting 10s for DNS propagation..."
        sleep 10
        echo "Attempting to obtain SSL certificate..."
        
        # First try to obtain the certificate
        certbot certonly --webroot \
            --webroot-path /var/www/certbot \
            --domain ${DOMAIN} \
            --email ${EMAIL} \
            --agree-tos \
            --non-interactive \
            --keep-until-expiring
        
        if [ $? -eq 0 ]; then
            echo "Successfully obtained SSL certificate. Switching to HTTPS..."
            # Stop nginx gracefully
            nginx -s quit
            wait
            
            # Switch to SSL configuration
            envsubst '${DOMAIN}' < /etc/nginx/nginx.ssl.conf > /etc/nginx/conf.d/default.conf
            nginx -g 'daemon off;' &
            
            # Trap SIGTERM and forward it to nginx
            trap "nginx -s quit" SIGTERM
            
            # Renew certificates automatically
            while :; do
                certbot renew --webroot --webroot-path /var/www/certbot
                sleep 12h
            done
        else
            echo "Failed to obtain SSL certificate. Continuing with HTTP only..."
            # Continue running with HTTP
            wait
        fi
    else
        # If SSL is not requested, just wait
        wait
    fi
}

# Main script
echo "Starting server..."
start_http
