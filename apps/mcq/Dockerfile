FROM node:18-alpine AS builder

WORKDIR /app

# Set up build arguments
ARG NODE_ENV=production
ARG APP_VERSION

# Copy package files
COPY package*.json ./

# Install ALL dependencies (including dev) for build step
RUN npm install --include=dev

# Copy source code
COPY . .

# Set environment variables for build
ENV NODE_ENV=${NODE_ENV}
ENV APP_VERSION=${APP_VERSION}
RUN npm run build

# Production stage
FROM nginx:alpine

# Install required packages
RUN apk add --no-cache \
    certbot \
    certbot-nginx \
    gettext \
    curl \
    bind-tools

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
COPY nginx.gzip.conf /etc/nginx/conf.d/gzip.conf

# Copy entrypoint script
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

# Expose ports
EXPOSE 80
EXPOSE 443

# Start nginx with certificate management
ENTRYPOINT ["/docker-entrypoint.sh"]
