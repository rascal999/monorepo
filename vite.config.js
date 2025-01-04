import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'
// Get version from environment variable or use development
function getVersion() {
  const version = process.env.APP_VERSION;
  return version ? `mcq/v${version}` : 'mcq/development';
}

function getFilesRecursively(dir, baseDir = dir) {
  let results = [];
  const items = fs.readdirSync(dir);

  for (const item of items) {
    const fullPath = path.join(dir, item);
    const relativePath = path.relative(baseDir, fullPath);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      results = results.concat(getFilesRecursively(fullPath, baseDir));
    } else if (item.endsWith('.json')) {
      results.push(relativePath);
    }
  }

  return results;
}

// https://vitejs.dev/config/
export default defineConfig({
  define: {
    'import.meta.env.VITE_APP_VERSION': JSON.stringify(getVersion())
  },
  server: {
    host: '0.0.0.0',
    port: 3000
  },
  build: {
    // Use esbuild minification (faster than terser)
    minify: 'esbuild',
    // CSS optimization
    cssCodeSplit: true,
    cssMinify: true,
    // Chunk optimization
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom'],  // Separate vendor chunks
        },
        // Optimize chunk size
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    // Enable source maps for production debugging if needed
    sourcemap: true,
    // Reduce chunk size warnings threshold
    chunkSizeWarningLimit: 1000
  },
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
              const files = getFilesRecursively(questionsDir);
              const fileLinks = files
                .map(file => `<a href="${file}">${file}</a>`)
                .join('\n');
              res.setHeader('Content-Type', 'text/html');
              res.end(fileLinks);
            } catch (error) {
              console.error('Error reading questions directory:', error);
              res.statusCode = 500;
              res.end('Failed to read questions directory');
            }
          } else {
            // Handle individual file requests
            // Remove leading slash if present
            const cleanUrl = req.url.startsWith('/') ? req.url.slice(1) : req.url;
            const filePath = path.join(questionsDir, cleanUrl);
            
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
