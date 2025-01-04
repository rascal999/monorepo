FROM node:18-alpine

WORKDIR /app

# Set up build argument
ARG NODE_ENV=production

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose API port
EXPOSE 3000

# Start the server
CMD ["npm", "start"]
