# MCQ API Server

Backend API server for the MCQ (Multiple Choice Questions) application. Provides REST endpoints for accessing questions and categories from a PostgreSQL database.

## Database Schema

### Categories
- `id`: Primary key
- `name`: Category name
- `slug`: URL-friendly identifier
- `description`: Optional category description
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

### Questions
- `id`: Primary key
- `category_id`: Foreign key to categories
- `question_text`: The question content
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

### Options
- `id`: Primary key
- `question_id`: Foreign key to questions
- `option_text`: The option content
- `is_correct`: Boolean indicating if this is the correct answer
- `created_at`: Timestamp of creation

## API Endpoints

### GET /health
Health check endpoint

### GET /api/categories
Returns all categories

### GET /api/categories/:slug/questions
Returns all questions for a specific category

### GET /api/questions/:id
Returns a specific question with its options

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
Create a `.env` file with:
```
DATABASE_URL=postgresql://postgres:postgres@db:5432/mcq
PORT=3000
```

3. Start the services:
```bash
# From the root mcq directory
docker-compose up -d
```

4. Run database migration:
```bash
# After services are up
docker-compose exec api npm run migrate
```

## Development

Start the development server:
```bash
npm run dev
```

## Production

The server is configured to run in a Docker container as defined in the Dockerfile and docker-compose.yml.
