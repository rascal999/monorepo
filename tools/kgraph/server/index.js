const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const app = express();

// Enable CORS for the frontend
app.use(cors());
app.use(express.json());

// Create logs directory if it doesn't exist
const logsDir = path.join(__dirname, '..', 'logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir);
}

// Handle log requests
app.post('/log', (req, res) => {
  const { level, message, timestamp } = req.body;
  const sessionId = req.headers['x-session-id'];
  
  // Create log entry
  const logEntry = JSON.stringify({
    timestamp,
    level,
    message
  }) + '\n';

  // Write to session log
  fs.appendFile(
    path.join(logsDir, `session-${sessionId}.log`),
    logEntry,
    (err) => {
      if (err) console.error('Error writing to session log:', err);
    }
  );

  // Write to error log if it's an error
  if (level === 'error') {
    fs.appendFile(
      path.join(logsDir, `error-${sessionId}.log`),
      logEntry,
      (err) => {
        if (err) console.error('Error writing to error log:', err);
      }
    );
  }

  res.sendStatus(200);
});

const PORT = process.env.PORT || 3030;
app.listen(PORT, () => {
  console.log(`Log server running on port ${PORT}`);
});
