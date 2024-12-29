FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with production flag
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application in production mode
ENV NODE_ENV=production
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

# Enable gzip compression in Nginx
RUN echo 'gzip on;\n\
    gzip_vary on;\n\
    gzip_min_length 10240;\n\
    gzip_proxied expired no-cache no-store private auth;\n\
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml application/javascript;\n\
    gzip_disable "MSIE [1-6]\.";\n' > /etc/nginx/conf.d/gzip.conf

# Copy entrypoint script
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

# Expose ports
EXPOSE 80
EXPOSE 443

# Start nginx with certificate management
ENTRYPOINT ["/docker-entrypoint.sh"]
