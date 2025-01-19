import cors from 'cors';
import express from 'express';
import { config } from './config.js';

// Configure CORS options based on environment
const corsOptions = {
  origin: config.nodeEnv === 'production'
    ? ['http://localhost:5173', 'http://127.0.0.1:5173']  // Restrict in production
    : '*',  // Allow all origins in development
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'Accept'],
};

export function setupMiddleware(app) {
  // Enable CORS
  app.use(cors(corsOptions));
  
  // Enable CORS pre-flight for all routes
  app.options('*', cors(corsOptions));
  
  // Parse JSON bodies
  app.use(express.json());
  
  // Add request logging in development
  if (config.nodeEnv === 'development') {
    app.use((req, res, next) => {
      console.log(`${req.method} ${req.path}`);
      next();
    });
  }
}
