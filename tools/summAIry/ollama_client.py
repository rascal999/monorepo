import sys
import json
import requests
import re
from prompts import DETAILED_SUMMARY, CONCISE_SUMMARY, QUERY_RESPONSE

class OllamaClient:
    def __init__(self, url, model, verbose=False, debug=False):
        self.url = url.rstrip('/')
        self.model = model
        self.verbose = verbose
        self.debug = debug
        
    def debug_log(self, message):
        """Print debug message if debug mode is enabled"""
        if self.debug:
            print(Colors.colorize(f"[DEBUG] {message}", Colors.MAGENTA), file=sys.stderr)

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
        self.debug_log(f"Original response: {text}")
        
        # Remove entire <think>...</think> blocks
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        self.debug_log(f"After removing thinking blocks: {cleaned}")
        
        # Remove any extra newlines that might have been created
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        self.debug_log(f"After cleaning newlines: {cleaned}")
        
        # Remove markdown code blocks and explanatory text around JSON
        cleaned = re.sub(r'```(?:json)?\s*(\{.*?\})\s*```', r'\1', cleaned, flags=re.DOTALL)
        self.debug_log(f"After removing markdown: {cleaned}")
        
        # Only try to extract JSON if response looks like a command
        if cleaned.strip().startswith('{') and '"type"' in cleaned:
            match = re.search(r'\{[^{]*"type":[^}]*\}', cleaned)
            if match:
                self.debug_log(f"Found JSON command: {match.group(0)}")
                return match.group(0)
        
        # For non-command responses, just clean and return
        cleaned = cleaned.strip()
        self.debug_log(f"Final cleaned response: {cleaned}")
        return cleaned

    def generate_summary(self, ticket_data, detailed=False):
        """Generate a summary using Ollama"""
        prompt = DETAILED_SUMMARY if detailed else CONCISE_SUMMARY
        return self._send_request(prompt.format(ticket_data=json.dumps(ticket_data, indent=2)))

    def generate_response(self, context, query):
        """Generate a response to a user query about a ticket"""
        return self._send_request(QUERY_RESPONSE.format(context=context, query=query))
    def _send_request(self, prompt):
        """Send request to Ollama API"""
        try:
            print(f"Generating response using {self.model}...", file=sys.stderr)
            
            if self.verbose:
                print("\n=== Model Request ===", file=sys.stderr)
                print(prompt, file=sys.stderr)
                print("==================\n", file=sys.stderr)
            
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
                    response_text = self.clean_response(result['response'])
                    if self.verbose:
                        print("\n=== Model Response ===", file=sys.stderr)
                        print(response_text, file=sys.stderr)
                        print("===================\n", file=sys.stderr)
                    return response_text
                    
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
                    response_text = self.clean_response(result['message']['content'])
                    if self.verbose:
                        print("\n=== Model Response ===", file=sys.stderr)
                        print(response_text, file=sys.stderr)
                        print("===================\n", file=sys.stderr)
                    return response_text
            
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