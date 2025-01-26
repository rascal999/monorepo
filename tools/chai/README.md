# Chai - WhatsApp Messaging Tool

A Python script for sending WhatsApp messages using [whatsapp-api](https://github.com/chrishubert/whatsapp-api).

## Prerequisites

1. Start the WhatsApp API server in tools/chai/whatsapp-api:
```bash
cd whatsapp-api
docker-compose pull && docker-compose up
```

2. Visit http://localhost:3001/session/start/ABCD in your browser

3. When the server starts, scan the QR code using:
   - Open WhatsApp on your phone
   - Go to Settings > Linked Devices
   - Tap on "Link a Device"
   - Scan the QR code shown in the console

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a .env file (optional, defaults shown):
```bash
WHATSAPP_API_URL=http://localhost:3001
WHATSAPP_SESSION_ID=ABCD
```

## Usage

Send a WhatsApp message:
```bash
python chai.py <phone_number> "Your message here"
```

Example:
```bash
python chai.py 1234567890 "Hello from WhatsApp!"
```

## Notes

- The WhatsApp API server must be running before using this script
- Phone numbers should be provided without special characters (no +, -, or spaces)
- Messages are sent through your personal WhatsApp account
- The first time you run the script, you'll need to scan the QR code shown in the API server console
- The API server runs on port 3001 by default
- Session data is saved locally by the API server, so you only need to scan the QR code once
- The session ID is set to 'ABCD' by default, you can change it in the .env file