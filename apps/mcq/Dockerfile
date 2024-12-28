FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install required packages
RUN apk add --no-cache \
    certbot \
    certbot-nginx \
    gettext \
    curl

# Create directories
RUN mkdir -p /var/www/certbot \
    && mkdir -p /etc/letsencrypt

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy questions directory
COPY --from=builder /app/public/questions /usr/share/nginx/html/questions

# Copy nginx configurations
COPY nginx.http.conf /etc/nginx/nginx.http.conf
COPY nginx.ssl.conf /etc/nginx/nginx.ssl.conf

# Copy entrypoint script
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

# Expose ports
EXPOSE 80
EXPOSE 443

# Start nginx with certificate management
ENTRYPOINT ["/docker-entrypoint.sh"]
