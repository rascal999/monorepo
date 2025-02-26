const { google } = require('googleapis');
const express = require('express');
const open = require('open');

// Read credentials from command line
const clientId = process.argv[2];
const clientSecret = process.argv[3];

if (!clientId || !clientSecret) {
  console.log('Usage: node get-refresh-token.js CLIENT_ID CLIENT_SECRET');
  process.exit(1);
}

// Create OAuth2 client
const oauth2Client = new google.auth.OAuth2(
  clientId,
  clientSecret,
  'http://localhost:3000/oauth2callback'
);

// Generate auth URL
const scopes = [
  'https://www.googleapis.com/auth/drive.readonly'
];

const authUrl = oauth2Client.generateAuthUrl({
  access_type: 'offline',
  scope: scopes,
  prompt: 'consent' // Force refresh token generation
});

// Start express server to handle callback
const app = express();

app.get('/oauth2callback', async (req, res) => {
  const { code } = req.query;
  
  try {
    // Exchange code for tokens
    const { tokens } = await oauth2Client.getToken(code);
    
    console.log('\nRefresh Token:', tokens.refresh_token);
    console.log('\nAdd this refresh token to your plugin.json setup_args.');
    
    res.send('Authorization successful! You can close this window.');
    setTimeout(() => process.exit(0), 1000);
    
  } catch (error) {
    console.error('Error getting tokens:', error.message);
    res.status(500).send('Authorization failed!');
    setTimeout(() => process.exit(1), 1000);
  }
});

// Start server and open auth URL
app.listen(3000, async () => {
  console.log('\nOpening browser for Google authorization...');
  console.log('\nNote: You will need to login and grant access to your Google Drive.');
  
  await open(authUrl);
});