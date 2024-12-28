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

# Install certbot and its nginx plugin
RUN apk add --no-cache certbot certbot-nginx

# Create directory for certbot challenges
RUN mkdir -p /var/www/certbot

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy questions directory
COPY --from=builder /app/public/questions /usr/share/nginx/html/questions

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create directory for certificates
RUN mkdir -p /etc/letsencrypt

# Copy certificate initialization and renewal scripts
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

# Expose ports
EXPOSE 80
EXPOSE 443

# Start nginx with certificate management
ENTRYPOINT ["/docker-entrypoint.sh"]
