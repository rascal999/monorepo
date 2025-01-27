"""Ollama interaction for natural language processing."""
import json
import logging
import re
from pathlib import Path
from typing import Dict, Optional

import requests


class OllamaClient:
    """Client for interacting with Ollama."""
    
    def __init__(self, url: str, model: str, verbose: bool = False):
        """Initialize Ollama client.
        
        Args:
            url: URL of Ollama instance
            model: Name of model to use
            verbose: Enable verbose output
        """
        self.url = url
        self.model = model
        self.verbose = verbose
        self.logger = logging.getLogger("darkquery.ollama")
        
        # Load prompt template
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        self.prompt_template = (self.prompts_dir / "prompt.txt").read_text()
    
    def query(self, query: str, context: Optional[Dict] = None) -> str:
        """Send query to Ollama.
        
        Args:
            query: Query string
            context: Optional context information
            
        Returns:
            Response string from model
        """
        # Build context string
        context_str = json.dumps(context or {}, indent=2)
        
        # Format prompt template using simple string replacement
        prompt = self.prompt_template.replace("%CONTEXT%", context_str)
        prompt = prompt.replace("%QUERY%", query)
        
        if self.verbose:
            self.logger.info(f"Sending prompt to Ollama:\n{prompt}")
        
        response = requests.post(
            f"{self.url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama request failed: {response.text}")
            
        result = response.json()['response']
        
        if self.verbose:
            self.logger.info(f"Ollama response: {result}")
            
        return self._clean_response(result)
    
    def _clean_response(self, response: str) -> str:
        """Clean response of any thinking tags or unwanted formatting.
        
        Args:
            response: Response string from model
            
        Returns:
            Cleaned response string
        """
        # Remove thinking tags and content
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        
        # Remove any remaining XML-like tags
        response = re.sub(r'<[^>]+>', '', response)
        
        # Remove emoji shortcodes
        response = re.sub(r':[a-zA-Z0-9_+-]+:', '', response)
        
        # Clean up extra whitespace
        response = re.sub(r'\n\s*\n', '\n\n', response)
        response = response.strip()
        
        return response