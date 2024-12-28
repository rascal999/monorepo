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
          const questionsDir = path.join(process.cwd(), 'public/questions');
          
          if (req.url === '/') {
            // Handle directory listing
            try {
              const files = fs.readdirSync(questionsDir)
                .filter(file => file.endsWith('.json'));
              const fileLinks = files.map(file => `<a href="${file}">${file}</a>`).join('\n');
              res.setHeader('Content-Type', 'text/html');
              res.end(fileLinks);
            } catch (error) {
              console.error('Error reading questions directory:', error);
              res.statusCode = 500;
              res.end('Failed to read questions directory');
            }
          } else {
            // Handle individual file requests
            const filePath = path.join(questionsDir, req.url);
            try {
              if (fs.existsSync(filePath) && filePath.endsWith('.json')) {
                const content = fs.readFileSync(filePath, 'utf-8');
                res.setHeader('Content-Type', 'application/json');
                res.end(content);
              } else {
                next();
              }
            } catch (error) {
              console.error(`Error reading file ${filePath}:`, error);
              next();
            }
          }
        });
      }
    }
  ]
})
