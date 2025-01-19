import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Verify required environment variables
if (!process.env.OPENROUTER_API_KEY) {
  console.error('ERROR: OPENROUTER_API_KEY environment variable is not set');
  console.error('Make sure the .env file exists in the server directory and contains OPENROUTER_API_KEY');
  process.exit(1);
}

// Log environment configuration for debugging
console.log('Server configuration:', {
  workingDirectory: process.cwd(),
  nodeEnv: process.env.NODE_ENV,
  hasOpenRouterKey: !!process.env.OPENROUTER_API_KEY,
  openRouterKeyLength: process.env.OPENROUTER_API_KEY?.length
});

export const config = {
  port: process.env.PORT || 3001,
  nodeEnv: process.env.NODE_ENV || 'development',
  openRouterApiKey: process.env.OPENROUTER_API_KEY
};
