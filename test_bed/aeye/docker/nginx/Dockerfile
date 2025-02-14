FROM openresty/openresty:alpine

# Install curl
RUN apk add --no-cache curl

# Create required directories
RUN mkdir -p /etc/nginx && \
    mkdir -p /var/log/nginx && \
    touch /etc/nginx/blocked_ips.conf && \
    chmod 666 /etc/nginx/blocked_ips.conf && \
    chown -R nobody:nobody /var/log/nginx

# Copy nginx configuration
COPY docker/nginx/nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY docker/nginx/conf.d /etc/nginx/conf.d
COPY docker/nginx/lua /usr/local/openresty/nginx/lua

# Expose port
EXPOSE 8888