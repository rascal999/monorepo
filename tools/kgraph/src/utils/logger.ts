// Generate a unique session ID
const sessionId = new Date().toISOString().replace(/[:.]/g, '-');

// Function to send logs to server
const sendLog = async (level: string, message: string) => {
  try {
    await fetch('http://localhost:3030/log', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-ID': sessionId
      },
      body: JSON.stringify({
        level,
        message,
        timestamp: new Date().toISOString()
      })
    });
  } catch (error) {
    // Fallback to original console in case of server error
    const originalConsole = window.console;
    originalConsole.error('Error sending log to server:', error);
  }
};

// Store original console methods
const originalConsole = {
  log: console.log,
  error: console.error,
  warn: console.warn,
  info: console.info,
  debug: console.debug
};

// Override console methods
console.log = (...args) => {
  const message = args.map(arg => 
    typeof arg === 'object' ? JSON.stringify(arg) : arg
  ).join(' ');
  sendLog('info', message);
  originalConsole.log(...args);
};

console.error = (...args) => {
  const message = args.map(arg => 
    typeof arg === 'object' ? JSON.stringify(arg) : arg
  ).join(' ');
  sendLog('error', message);
  originalConsole.error(...args);
};

console.warn = (...args) => {
  const message = args.map(arg => 
    typeof arg === 'object' ? JSON.stringify(arg) : arg
  ).join(' ');
  sendLog('warn', message);
  originalConsole.warn(...args);
};

console.info = (...args) => {
  const message = args.map(arg => 
    typeof arg === 'object' ? JSON.stringify(arg) : arg
  ).join(' ');
  sendLog('info', message);
  originalConsole.info(...args);
};

console.debug = (...args) => {
  const message = args.map(arg => 
    typeof arg === 'object' ? JSON.stringify(arg) : arg
  ).join(' ');
  sendLog('debug', message);
  originalConsole.debug(...args);
};

// Export the session ID for reference
export const getSessionId = () => sessionId;
