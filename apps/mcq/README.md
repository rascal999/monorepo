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

3. SSL Setup:
```bash
# Get SSL certificate (run once)
./scripts/get-cert.sh

# Start application with SSL
USE_SSL=true ./scripts/manage.sh start
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
