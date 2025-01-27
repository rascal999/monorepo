import sys
import json
import requests
import re

class OllamaClient:
    def __init__(self, url, model):
        self.url = url.rstrip('/')
        self.model = model

    def check_model_availability(self):
        """Check if the specified model is available"""
        try:
            response = requests.get(f"{self.url}/api/tags")
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                return self.model in models
            return False
        except:
            return False

    def clean_response(self, text):
        """Remove thinking blocks and clean up the response"""
        # Remove entire <think>...</think> blocks
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # Remove any extra newlines that might have been created
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        # Remove markdown code blocks and explanatory text around JSON
        cleaned = re.sub(r'```(?:json)?\s*(\{.*?\})\s*```', r'\1', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'.*?(\{.*?\})', r'\1', cleaned, flags=re.DOTALL)
        return cleaned.strip()

    def generate_summary(self, ticket_data, detailed=False):
        """Generate a summary using Ollama"""
        if detailed:
            prompt = f"""Analyze these Jira tickets and provide a detailed summary with the following format:

TL;DR: (One sentence overview)

Key Points:
• (3-4 bullet points of the most important aspects)

Stakeholders:
• [Name] ([Role]) - (One sentence describing their specific contribution, input, or position on the ticket)

Possible Next Steps:
• (2-3 concrete actions that could help move the ticket forward)
• (Focus on unblocking issues or advancing the current state)

Summary: (2-3 paragraphs covering:
- Main purpose and scope
- Dependencies and related work
- Current status and progress
- Key discussion points from comments)

Tickets analyzed:
{json.dumps(ticket_data, indent=2)}

Please include relevant insights from ticket comments in your summary, especially any important decisions, blockers, or updates discussed.
Do not include any thinking or analysis process in the output.
"""
        else:
            prompt = f"""Analyze these Jira tickets and provide a concise overview with the following format:

TL;DR: (One sentence overview)

Key Points:
• (3-4 bullet points covering the main purpose, status, and key updates)

Stakeholders:
• [Name] ([Role]) - (One sentence describing their specific contribution, input, or position on the ticket)

Possible Next Steps:
• (2-3 concrete actions that could help move the ticket forward)

Tickets analyzed:
{json.dumps(ticket_data, indent=2)}

Do not include any thinking or analysis process in the output.
"""
        return self._send_request(prompt)

    def generate_response(self, context, query):
        """Generate a response to a user query about a ticket"""
        prompt = f"""Based on the following context and chat history, answer the user's question.
If the question cannot be answered using only the provided context, say so.

{context}

Please provide a clear and concise response focusing specifically on answering the user's question.
If your response is a command, provide ONLY the JSON command without any explanation or markdown formatting.

Important: When generating JQL queries:
1. Always include LIMIT 1 when looking for a single/latest ticket
2. Always include LIMIT 5 when looking for multiple tickets unless specifically asked for more
3. Never include explanatory text, only the JSON command

Example responses:
For latest ticket: {{"type": "jql", "query": "creator = 'Bob' ORDER BY created DESC LIMIT 1"}}
For recent tickets: {{"type": "jql", "query": "assignee = 'Alice' ORDER BY updated DESC LIMIT 5"}}

User query: {query}
"""
        return self._send_request(prompt)

    def _send_request(self, prompt):
        """Send request to Ollama API"""
        try:
            print(f"Generating response using {self.model}...", file=sys.stderr)
            
            # Check if model exists
            if not self.check_model_availability():
                print(f"Warning: Model '{self.model}' not found. You may need to run: ollama pull {self.model}", file=sys.stderr)
                print("Attempting to proceed anyway...", file=sys.stderr)
            
            # Try /api/generate endpoint first
            try:
                response = requests.post(
                    f"{self.url}/api/generate",
                    json={
                        'model': self.model,
                        'prompt': prompt,
                        'stream': False
                    }
                )
                
                if response.status_code == 404:
                    raise requests.exceptions.RequestException("API endpoint not found")
                    
                response.raise_for_status()
                result = response.json()
                
                if 'response' in result:
                    return self.clean_response(result['response'])
                    
            except requests.exceptions.RequestException:
                print("Trying alternative endpoint...", file=sys.stderr)
                # Try alternative endpoint for older Ollama versions
                response = requests.post(
                    f"{self.url}/api/chat",
                    json={
                        'model': self.model,
                        'messages': [{'role': 'user', 'content': prompt}],
                        'stream': False
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                if 'message' in result:
                    return self.clean_response(result['message']['content'])
            
            print("Warning: Unexpected response format", file=sys.stderr)
            return self.clean_response(str(result))
                
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to Ollama at {self.url}", file=sys.stderr)
            print("Please ensure Ollama is running and the URL is correct", file=sys.stderr)
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Ollama: {e}", file=sys.stderr)
            print("Response content:", e.response.text if hasattr(e, 'response') else "No response content", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Unexpected error while getting response: {e}", file=sys.stderr)
            return None