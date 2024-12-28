import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'questions-directory',
      configureServer(server) {
        server.middlewares.use('/questions', (req, res, next) => {
          if (req.url === '/') {
            const questionsDir = path.join(process.cwd(), 'public/questions');
            try {
              const files = fs.readdirSync(questionsDir)
                .filter(file => file.endsWith('.json'));
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify(files));
            } catch (error) {
              console.error('Error reading questions directory:', error);
              res.statusCode = 500;
              res.end(JSON.stringify({ error: 'Failed to read questions directory' }));
            }
          } else {
            next();
          }
        });
      }
    }
  ]
})
