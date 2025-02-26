# Google Drive Reader Agent Skill

This AnythingLLM agent skill reads files from Google Drive using natural language commands.

## Setup Instructions

1. Create Google Cloud Project:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable the Google Drive API
   - Configure OAuth consent screen
   - Create OAuth 2.0 Client ID credentials
   - Download client ID and client secret

2. Get Refresh Token:
```bash
npm install
npm run get-token YOUR_CLIENT_ID YOUR_CLIENT_SECRET
```
This will:
- Open your browser for Google authorization
- Ask you to log in and grant access
- Display the refresh token to use in plugin.json

3. Configure plugin.json:
   - Add your client ID
   - Add your client secret
   - Add the refresh token from step 2

## Usage Examples

Read file contents:
```
Read file MyReport.pdf from Drive
Response:
Contents of MyReport.pdf:
[File contents displayed here]
```

Different ways to request files:
```
Show me the contents of ProjectNotes.txt
Get the content of meeting-minutes.docx
```

## Required Fields

- `file`: Name of file to read from Google Drive

## Configuration

The skill requires the following credentials in the agent skills settings:

- `GOOGLE_CLIENT_ID`: OAuth Client ID from Google Cloud Console
- `GOOGLE_CLIENT_SECRET`: OAuth Client Secret from Google Cloud Console
- `GOOGLE_REFRESH_TOKEN`: OAuth Refresh Token (obtained using get-refresh-token.js)

## Features

- Natural language commands to read files
- Supports multiple file types:
  - Text files (.txt, etc.)
  - PDF files (coming soon)
  - Word documents (coming soon)
- OAuth 2.0 authentication
- Proper error handling for:
  - File not found
  - Authentication issues
  - API errors
  - Unsupported file types

## Testing

Run tests with:
```bash
npm install
npm test
```

Tests cover:
- File searching
- Content reading
- Authentication
- Error handling

## Dependencies

- googleapis: Official Google APIs Node.js client
- express: For OAuth callback server (dev only)
- open: For opening browser (dev only)
- jest: Testing framework (dev only)