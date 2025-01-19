# AQA (Advanced Quiz Application)

A React-based quiz application with a Node.js/SQLite backend for creating and taking interactive quizzes.

## Features

- Interactive quiz interface
- Progress tracking
- Explanation support for questions
- Comprehensive completion stats:
  - Time taken per question
  - Average completion time
  - Detailed performance analysis
  - Question-by-question review
- SQLite database for persistent storage
- Sample JavaScript fundamentals quiz included

## Prerequisites

- Node.js (v16 or higher)
- npm (v7 or higher)

## Development Setup

Run the development script:
```bash
./scripts/dev.sh
```

This will:
1. Install all dependencies (if needed)
2. Set up the SQLite database with sample data (if needed)
3. Start both frontend and backend servers
4. Open the application at http://localhost:5173

The script handles all necessary setup and process management. Use Ctrl+C to stop all services.

## Project Structure

- `/src` - Frontend React application
  - `/components` - React components
  - `/hooks` - Custom React hooks
  - `/utils` - Utility functions
  - `/api` - API client code
  - `/server` - Backend server
    - `db.js` - Database configuration
    - `index.js` - Express server
    - `sample-data-sqlite.js` - Sample quiz data loader

## Technology Stack

- Frontend:
  - React
  - Vite
  - Formik for forms
  - CSS Modules for styling

- Backend:
  - Node.js
  - Express
  - SQLite3
  - Nodemon for development
