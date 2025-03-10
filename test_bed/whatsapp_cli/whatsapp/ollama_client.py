import requests
import json
from typing import Dict, List, Optional, Any, Union

class OllamaClient:
    """Client for interacting with Ollama API for chat analysis"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict:
        """Make HTTP request to Ollama API with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            print(f"Error making request to Ollama API: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return {"error": str(e)}
    
    def analyze_sentiment(self, messages: List[Dict]) -> Dict:
        """Analyze sentiment of messages"""
        formatted_messages = self._format_messages_for_analysis(messages)
        
        prompt = f"""
        Analyze the sentiment and tone of the following WhatsApp conversation.
        Provide a summary of the overall emotional tone, identifying key sentiments
        (positive, negative, neutral) and any emotional patterns.
        
        Messages:
        {formatted_messages}
        
        Provide your analysis in JSON format with the following structure:
        {{
            "overall_sentiment": "positive/negative/neutral/mixed",
            "sentiment_score": 0-10 (0 being very negative, 10 being very positive),
            "dominant_emotions": ["emotion1", "emotion2"],
            "summary": "brief summary of the emotional tone"
        }}
        """
        
        return self._analyze_with_ollama(prompt)
    
    def analyze_relationship(self, messages: List[Dict]) -> Dict:
        """Analyze relationship dynamics from messages"""
        formatted_messages = self._format_messages_for_analysis(messages)
        
        prompt = f"""
        Analyze the relationship dynamics in the following WhatsApp conversation.
        Identify patterns in communication, level of engagement, and emotional connection.
        
        Messages:
        {formatted_messages}
        
        Provide your analysis in JSON format with the following structure:
        {{
            "relationship_quality": "strong/moderate/weak/unclear",
            "communication_style": "formal/casual/intimate/distant",
            "engagement_level": "high/medium/low",
            "key_topics": ["topic1", "topic2"],
            "recommendations": ["suggestion1", "suggestion2"],
            "summary": "brief summary of relationship dynamics"
        }}
        """
        
        return self._analyze_with_ollama(prompt)
    
    def generate_responses(self, messages: List[Dict], count: int = 3) -> Dict:
        """Generate suggested responses based on conversation context"""
        # Get the last few messages for context (up to 10)
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        formatted_messages = self._format_messages_for_analysis(recent_messages)
        
        prompt = f"""
        Based on the following WhatsApp conversation, generate {count} appropriate
        responses that could be sent next. Consider the tone, context, and relationship
        dynamics of the conversation.
        
        Recent messages:
        {formatted_messages}
        
        Provide your suggested responses in JSON format with the following structure:
        {{
            "responses": [
                {{
                    "text": "response text",
                    "tone": "casual/formal/friendly/etc",
                    "purpose": "brief description of response purpose"
                }},
                ...
            ]
        }}
        """
        
        return self._analyze_with_ollama(prompt)
    
    def _format_messages_for_analysis(self, messages: List[Dict]) -> str:
        """Format messages for analysis prompt"""
        formatted = []
        
        for msg in messages:
            # Get sender info
            sender = "Me" if msg.get('fromMe') else msg.get('sender_name', 'Contact')
            
            # Get message content
            content = msg.get('body', '')
            if not content and msg.get('type'):
                content = f"[{msg['type'].upper()} message]"
            
            # Format timestamp
            timestamp = msg.get('timestamp', 0)
            
            formatted.append(f"[{timestamp}] {sender}: {content}")
        
        return "\n".join(formatted)
    
    def _analyze_with_ollama(self, prompt: str, model: str = None) -> Dict:
        """Send prompt to Ollama for analysis"""
        # Use provided model or fall back to instance model
        model_to_use = model if model else self.model
        
        data = {
            "model": model_to_use,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for more consistent results
                "num_predict": 1024  # Limit response length
            }
        }
        
        response = self._make_request("/api/generate", data)
        
        if "error" in response:
            return {"error": response["error"]}
        
        # Try to parse JSON from the response
        try:
            # Extract JSON from the response text
            response_text = response.get("response", "")
            # Find JSON content (might be surrounded by markdown code blocks)
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_content = response_text[json_start:json_end]
                return json.loads(json_content)
            else:
                return {"error": "No valid JSON found in response", "raw_response": response_text}
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON from response", "raw_response": response.get("response", "")}