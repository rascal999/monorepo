#!/usr/bin/env python3
import argparse
import os
import sys
from dotenv import load_dotenv
from jira_client import JiraTicketManager
from ollama_client import OllamaClient
from interactive import InteractiveSession
from utils import validate_ticket_id, get_missing_credentials

def main():
    # Load environment variables from .env file
    load_dotenv()

    parser = argparse.ArgumentParser(description='Summarize Jira tickets using Ollama')
    parser.add_argument('ticket_id', nargs='?', help='Jira ticket ID (e.g. PROJ-123)')
    parser.add_argument('--jira-url', help='Jira instance URL (or set JIRA_URL env var)')
    parser.add_argument('--jira-token', help='Jira API token (or set JIRA_TOKEN env var)')
    parser.add_argument('--jira-email', help='Jira account email (or set JIRA_EMAIL env var)')
    parser.add_argument('--ollama-url', help='Ollama API URL (or set OLLAMA_URL env var)')
    parser.add_argument('--ollama-model', help='Ollama model to use (or set OLLAMA_MODEL env var)')
    parser.add_argument('--summary', action='store_true', help='Generate detailed summary instead of key points')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging of model messages')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    # Get credentials and configuration from args or environment variables
    jira_url = args.jira_url or os.getenv('JIRA_URL')
    jira_token = args.jira_token or os.getenv('JIRA_TOKEN')
    jira_email = args.jira_email or os.getenv('JIRA_EMAIL')
    ollama_url = args.ollama_url or os.getenv('OLLAMA_URL', 'http://localhost:11434')
    ollama_model = args.ollama_model or os.getenv('OLLAMA_MODEL', 'mistral')
    
    # Check for missing credentials
    missing = get_missing_credentials(jira_url, jira_token, jira_email)
    if missing:
        print(f"Error: Missing required credentials: {', '.join(missing)}", file=sys.stderr)
        print("Please provide them via command line arguments or set them in .env file", file=sys.stderr)
        sys.exit(1)
    
    # Initialize Jira client
    jira = JiraTicketManager(jira_url, jira_email, jira_token)
    if not jira.connect():
        sys.exit(1)
        
    # Initialize Ollama client
    ollama = OllamaClient(ollama_url, ollama_model, verbose=args.verbose, debug=args.debug)
    
    if args.interactive:
        # Run interactive session
        session = InteractiveSession(jira, ollama, debug=args.debug)
        if args.ticket_id and validate_ticket_id(args.ticket_id):
            session.process_ticket(args.ticket_id)
        session.run()
    else:
        # Single ticket mode
        if not args.ticket_id:
            parser.error("ticket_id is required in non-interactive mode")
            
        # Validate ticket ID format
        if not validate_ticket_id(args.ticket_id):
            print("Error: Invalid ticket ID format. Expected format: PROJECT-123", file=sys.stderr)
            sys.exit(1)
        
        # Get tickets
        issues = jira.get_related_tickets(args.ticket_id)
        if not issues:
            print("No tickets found or accessible", file=sys.stderr)
            sys.exit(1)
        
        print(f"Found {len(issues)} related tickets", file=sys.stderr)
        
        # Format data
        print("Formatting ticket data...", file=sys.stderr)
        ticket_data = jira.format_ticket_data(issues)
        
        # Get summary
        summary = ollama.generate_summary(ticket_data, detailed=args.summary)
        if not summary:
            sys.exit(1)
        
        # Print a newline before the summary for better readability
        print("\n" + summary)

if __name__ == '__main__':
    main()