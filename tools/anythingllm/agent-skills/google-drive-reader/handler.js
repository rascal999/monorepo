const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');
const os = require('os');

const runtime = {
  async handler(params, context = {}) {
    const { file } = params;
    const { introspect = console.log } = context;
    const callerId = `${this.config?.name || 'Google Drive Reader'}-v${this.config?.version || '1.0.0'}`;

    // Debug: Log tool selection and parameters
    introspect('=== Google Drive Reader Tool Selected ===');
    introspect('Parameters:', JSON.stringify(params, null, 2));

    try {
      // Validate required fields
      if (!file) {
        introspect('Error: Missing file parameter');
        return "Missing required field: file (e.g., 'document.pdf')";
      }

      // Get credentials from runtime args or environment variables
      let GOOGLE_CLIENT_ID = (this.runtimeArgs || {}).GOOGLE_CLIENT_ID || process.env.GOOGLE_CLIENT_ID;
      let GOOGLE_CLIENT_SECRET = (this.runtimeArgs || {}).GOOGLE_CLIENT_SECRET || process.env.GOOGLE_CLIENT_SECRET;
      let GOOGLE_REFRESH_TOKEN = (this.runtimeArgs || {}).GOOGLE_REFRESH_TOKEN || process.env.GOOGLE_REFRESH_TOKEN;
      
      if (!GOOGLE_CLIENT_ID || !GOOGLE_CLIENT_SECRET || !GOOGLE_REFRESH_TOKEN) {
        return "Missing required Google credentials. Please configure them in the agent skills settings or environment variables.";
      }

      // Create OAuth2 client
      const oauth2Client = new google.auth.OAuth2(
        GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET
      );

      // Set credentials using refresh token
      oauth2Client.setCredentials({
        refresh_token: GOOGLE_REFRESH_TOKEN
      });

      // Create Drive client
      const drive = google.drive({ version: 'v3', auth: oauth2Client });

      // Search for the file
      introspect(`Searching for file: ${file}`);
      const searchResponse = await drive.files.list({
        q: `name = '${file}' and trashed = false`,
        fields: 'files(id, name, mimeType)',
      });

      const files = searchResponse.data.files;
      if (!files || files.length === 0) {
        return `File '${file}' not found in Google Drive`;
      }

      const fileData = files[0];
      introspect(`Found file: ${fileData.name} (${fileData.id})`);

      // Create temp directory for downloads
      const tempDir = path.join(os.tmpdir(), 'google-drive-reader');
      if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir, { recursive: true });
      }

      // Download the file
      const tempFile = path.join(tempDir, fileData.name);
      introspect(`Downloading to: ${tempFile}`);

      const dest = fs.createWriteStream(tempFile);
      const downloadResponse = await drive.files.get(
        { fileId: fileData.id, alt: 'media' },
        { responseType: 'stream' }
      );

      await new Promise((resolve, reject) => {
        downloadResponse.data
          .on('end', () => {
            introspect('File downloaded successfully');
            resolve();
          })
          .on('error', err => {
            reject(err);
          })
          .pipe(dest);
      });

      // Read file content
      let content;
      if (fileData.mimeType.includes('text/')) {
        // Text files
        content = fs.readFileSync(tempFile, 'utf8');
      } else if (fileData.mimeType.includes('pdf')) {
        // PDF files (would need pdf-parse package)
        content = 'PDF content extraction not implemented';
      } else if (fileData.mimeType.includes('word')) {
        // Word files (would need mammoth package)
        content = 'Word document content extraction not implemented';
      } else {
        content = 'File type not supported for content extraction';
      }

      // Clean up temp file
      fs.unlinkSync(tempFile);

      // Format response
      let response = `Contents of ${file}:\n\n${content}`;

      introspect('Content extraction complete');
      return response;

    } catch (error) {
      introspect(`${callerId} error: ${error.message}`);
      if (error.response) {
        introspect(`Google Drive API response: ${JSON.stringify(error.response.data || {}, null, 2)}`);
      }

      if (error.code === 401) {
        return "Authentication failed. Please check your Google credentials.";
      }

      return `Failed to read file: ${error.message}`;
    }
  }
};

module.exports = { runtime };