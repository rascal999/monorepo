# WhatsApp CLI

A command-line interface for WhatsApp that provides chat management and AI-powered message analysis.

## Features

- List all WhatsApp chats and contacts
- Fetch messages from specific contacts
- Send messages to contacts
- AI-powered message analysis using Ollama:
  - Sentiment and tone analysis
  - Relationship and emotional trend tracking
  - Suggested responses generation

## Requirements

- Python 3.6+
- WhatsApp API service (running on localhost:3000 by default)
- Ollama (running on localhost:11434 by default) for AI analysis features

## Installation

1. Clone the repository
2. Install dependencies: `pip install requests`
3. Copy `config.json.example` to `config.json` and update with your API credentials
4. Ensure Ollama is installed and running for analysis features

## Usage

### Basic Commands

```bash
# List all chats
python whatsapp_cli.py --list-chats

# List all contacts
python whatsapp_cli.py --list-contacts

# Fetch messages from a contact (by name or number)
python whatsapp_cli.py --fetch "John Doe" --limit 20

# Send a message to a contact
python whatsapp_cli.py --send "John Doe" --message "Hello, how are you?"
```

### AI Analysis Commands

```bash
# Perform sentiment analysis on messages
python whatsapp_cli.py --analyze "John Doe" --sentiment --limit 50

# Analyze relationship dynamics
python whatsapp_cli.py --analyze "John Doe" --relationship --limit 100

# Get suggested responses
python whatsapp_cli.py --analyze "John Doe" --suggest-responses --response-count 5

# Perform multiple analyses at once
python whatsapp_cli.py --analyze "John Doe" --sentiment --relationship --suggest-responses
```

## Configuration

Create a `config.json` file with the following structure:

```json
{
    "base_url": "http://localhost:3000",
    "api_key": "your-api-key-here",
    "session_id": "optional-session-id",
    "ollama_url": "http://localhost:11434",
    "ollama_model": "llama2"
}
```

You can also specify the Ollama URL and model via command line:

```bash
python whatsapp_cli.py --analyze "John Doe" --sentiment --ollama-url "http://localhost:11434" --ollama-model "llama2"
```

## Analysis Features

### Sentiment Analysis

Analyzes the emotional tone of messages, providing:
- Overall sentiment (positive, negative, neutral, mixed)
- Sentiment score (0-10)
- Dominant emotions
- Summary of emotional tone

### Relationship Analysis

Examines relationship dynamics, providing:
- Relationship quality assessment
- Communication style analysis
- Engagement level
- Key conversation topics
- Recommendations for improving communication
- Summary of relationship dynamics

### Response Suggestions

Generates contextually appropriate responses based on conversation history, providing:
- Multiple response options
- Tone description for each response
- Purpose explanation for each response