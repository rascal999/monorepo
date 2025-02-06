const fs = require('fs');
const os = require('os');
const path = require('path');

// Function to mask sensitive values
function maskSensitiveValues(envVars) {
    const maskedVars = {};
    for (const [key, value] of Object.entries(envVars)) {
        if (key.toUpperCase().includes('KEY') || key.toUpperCase().includes('TOKEN')) {
            if (value && value.length > 16) {
                // Show first 12 and last 3 chars, mask middle with asterisks
                maskedVars[key] = `${value.slice(0, 12)}${'*'.repeat(value.length - 15)}${value.slice(-3)}`;
            } else if (value && value.length > 3) {
                // For shorter values, show all but last 3 chars
                maskedVars[key] = `${value.slice(0, -3)}***`;
            } else {
                // If value is too short, just show as is
                maskedVars[key] = value || '';
            }
        } else {
            maskedVars[key] = value;
        }
    }
    return maskedVars;
}

// Get container ID (hostname in Docker)
const containerId = os.hostname();

// Get timestamp
const timestamp = new Date().toISOString().replace(/[:.]/g, '').slice(0, 15);

// Get all environment variables and mask sensitive values
const envVars = process.env;
const maskedVars = maskSensitiveValues(envVars);

// Get log directory from environment
const logDir = process.env.LOG_DIRECTORY || '/workspace/logs';

// Create log file with timestamp and container ID
const logPath = path.join(logDir, `${timestamp}-${containerId}.log`);

// Create directory if it doesn't exist
fs.mkdirSync(path.dirname(logPath), { recursive: true });

// Get command line arguments (excluding node and script path)
const args = process.argv.slice(2);

// Prepare log content
const logContent = {
    environment: maskedVars,
    ...(args.length > 0 && { arguments: args })
};

// Write to log file
fs.writeFileSync(logPath, JSON.stringify(logContent, null, 2));

// Also print to stdout
console.log(JSON.stringify(logContent, null, 2));