import express from 'express';
import { config } from './config.js';
import { setupMiddleware } from './middleware.js';
import { initDb, getQuizzes, createQuiz } from './db.js';
import { sampleQuiz } from './sample-data.js';
import routes from './routes.js';

const app = express();

// Setup middleware
setupMiddleware(app);

// Mount API routes
app.use('/api', routes);

// Initialize database
initDb().then(() => {
  console.log('Database initialized');

  // Initialize sample data

  // Create sample quiz if no quizzes exist
  getQuizzes().then(quizzes => {
    if (quizzes.length === 0) {
      createQuiz(sampleQuiz.title, sampleQuiz.questions)
        .then(() => console.log('Sample quiz created'))
        .catch(console.error);
    }
  });
});

// Start server
app.listen(config.port, () => {
  console.log(`Server running on port ${config.port}`);
});

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (error) => {
  console.error('Unhandled Rejection:', error);
  process.exit(1);
});
