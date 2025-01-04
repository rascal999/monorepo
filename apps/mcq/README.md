# MCQ (Multiple Choice Questions) Application

A web application for managing and taking multiple choice questions, with support for various medical and veterinary topics.

## Project Structure

```
apps/mcq/
├── api/            # Backend API server
├── src/            # Frontend React application
├── scripts/        # Management scripts
│   ├── manage.sh   # Main application management
│   └── get-cert.sh # SSL certificate acquisition
└── public/         # Static assets
```

## Development Setup

1. Copy the environment file:
```bash
cp .env.example .env
```

2. Start the development environment:
```bash
./scripts/manage.sh start
```

This will start:
- Frontend on http://localhost:8080
- API on http://localhost:3001
- PostgreSQL database on localhost:5432

## Production Setup

1. Copy and modify the production environment file:
```bash
cp .env.production .env
```

2. Update the following variables in `.env`:
- `DOMAIN`: Your domain name (e.g., mcq.example.com)
- `EMAIL`: Your email for SSL certificate notifications
- `POSTGRES_PASSWORD`: A secure database password
- `VERSION`: Application version to deploy (optional)
- `ENV`: Deployment environment (optional, defaults to prod)

3. SSL Setup:
```bash
# Get SSL certificate (run once)
./scripts/get-cert.sh
```

4. Deploy Application:
```bash
# Latest version
USE_SSL=true ./scripts/manage.sh start

# Specific version
VERSION=1.0.0 ENV=prod USE_SSL=true ./scripts/manage.sh start
```

## Version Management

The application uses semantic versioning (MAJOR.MINOR.PATCH) with environment tags.

### Version Management

#### Creating a New Version

```bash
cd apps/mcq

# Create a production release
./scripts/tag.sh 1.0.0
# This will:
# - Build the Docker images
# - Tag images as mcq_frontend:v1.0.0 and mcq_api:v1.0.0
# - Create git tag v1.0.0

# Create a staging release
./scripts/tag.sh 1.0.1 staging
# This will:
# - Build the Docker images
# - Tag images as mcq_frontend:v1.0.1-staging and mcq_api:v1.0.1-staging
# - Create git tag v1.0.1-staging
```

If a version tag already exists, you'll be prompted to:
- Force update the existing tag (y)
- Skip git tag creation (n)

#### Version Format

- Production: v1.0.0-prod
- Staging: v1.0.0-staging
- Development: v1.0.0-dev

#### Managing Versions

```bash
# List all versions
./scripts/manage.sh versions

# Clean up old versions
./scripts/manage.sh clean
```

### Deployment Examples

```bash
# Deploy production version
VERSION=1.0.0 ENV=prod ./scripts/manage.sh start

# Deploy staging version
VERSION=1.0.1 ENV=staging ./scripts/manage.sh start

# Deploy latest
./scripts/manage.sh start
```

## Management Scripts

### manage.sh
Main application management script:
```bash
./scripts/manage.sh <command>

Commands:
  start   - Start the application stack
  stop    - Stop the application stack
  restart - Restart the application stack
  clean   - Stop containers and clean up volumes/certificates
  logs    - Show logs from all services
```

### get-cert.sh
SSL certificate acquisition script:
```bash
./scripts/get-cert.sh
```
- Obtains SSL certificate from Let's Encrypt
- Requires port 80 to be available
- Run this before starting the app with SSL

## Environment Variables

### Frontend
- `NODE_ENV`: Environment mode (development/production)
- `FRONTEND_PORT`: HTTP port (default: 8080 in dev, 80 in prod)
- `FRONTEND_SSL_PORT`: HTTPS port (default: 8443 in dev, 443 in prod)
- `DOMAIN`: Domain name
- `EMAIL`: Email for SSL certificates
- `USE_SSL`: Enable/disable SSL (default: false in dev, true in prod)

### Database
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name

## Features

- Multiple choice questions organized by categories
- Question randomization
- Score tracking
- API-driven architecture
- SSL support for production
- Docker-based deployment
