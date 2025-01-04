#!/bin/sh

# Clear any existing configuration
rm -f /etc/nginx/conf.d/default.conf

# Choose configuration based on SSL setting
if [ "${USE_SSL}" = "true" ] && [ -f /etc/letsencrypt/live/alm.gg/fullchain.pem ]; then
    echo "Starting with HTTPS configuration..."
    envsubst '${DOMAIN}' < /etc/nginx/nginx.ssl.conf > /etc/nginx/conf.d/default.conf
else
    echo "Starting with HTTP configuration..."
    envsubst '${DOMAIN}' < /etc/nginx/nginx.http.conf > /etc/nginx/conf.d/default.conf
fi

# Start nginx
echo "Starting nginx..."
nginx -g 'daemon off;'
