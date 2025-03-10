import json
from typing import Dict, List, Optional, Any, Union
from .ollama_client import OllamaClient

class MessageAnalyzer:
    """Analyze WhatsApp messages using Ollama"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", ollama_model: str = "llama2"):
        self.client = OllamaClient(base_url=ollama_url, model=ollama_model)
    
    def analyze_sentiment(self, messages: List[Dict]) -> Dict:
        """Analyze sentiment and tone of messages"""
        if not messages:
            return {"error": "No messages to analyze"}
        
        result = self.client.analyze_sentiment(messages)
        return self._format_sentiment_result(result)
    
    def analyze_relationship(self, messages: List[Dict]) -> Dict:
        """Analyze relationship dynamics from messages"""
        if not messages:
            return {"error": "No messages to analyze"}
        
        result = self.client.analyze_relationship(messages)
        return self._format_relationship_result(result)
    
    def generate_responses(self, messages: List[Dict], count: int = 3) -> Dict:
        """Generate suggested responses based on conversation context"""
        if not messages:
            return {"error": "No messages to analyze"}
        
        result = self.client.generate_responses(messages, count)
        return self._format_responses_result(result)
    
    def _format_sentiment_result(self, result: Dict) -> Dict:
        """Format sentiment analysis result for display"""
        if "error" in result:
            return result
        
        formatted = {
            "title": "Sentiment Analysis",
            "sections": [
                {
                    "heading": "Overall Sentiment",
                    "content": f"{result.get('overall_sentiment', 'Unknown')} (Score: {result.get('sentiment_score', 'N/A')})"
                },
                {
                    "heading": "Dominant Emotions",
                    "content": ", ".join(result.get('dominant_emotions', ['Unknown']))
                },
                {
                    "heading": "Summary",
                    "content": result.get('summary', 'No summary available')
                }
            ]
        }
        
        return formatted
    
    def _format_relationship_result(self, result: Dict) -> Dict:
        """Format relationship analysis result for display"""
        if "error" in result:
            return result
        
        formatted = {
            "title": "Relationship Analysis",
            "sections": [
                {
                    "heading": "Relationship Quality",
                    "content": result.get('relationship_quality', 'Unknown')
                },
                {
                    "heading": "Communication Style",
                    "content": result.get('communication_style', 'Unknown')
                },
                {
                    "heading": "Engagement Level",
                    "content": result.get('engagement_level', 'Unknown')
                },
                {
                    "heading": "Key Topics",
                    "content": ", ".join(result.get('key_topics', ['Unknown']))
                },
                {
                    "heading": "Recommendations",
                    "content": "\n- " + "\n- ".join(result.get('recommendations', ['No recommendations available']))
                },
                {
                    "heading": "Summary",
                    "content": result.get('summary', 'No summary available')
                }
            ]
        }
        
        return formatted
    
    def _format_responses_result(self, result: Dict) -> Dict:
        """Format suggested responses result for display"""
        if "error" in result:
            return result
        
        responses = result.get('responses', [])
        
        formatted = {
            "title": "Suggested Responses",
            "sections": []
        }
        
        for i, response in enumerate(responses, 1):
            formatted["sections"].append({
                "heading": f"Response {i}",
                "content": f"{response.get('text', 'No text')}\n\nTone: {response.get('tone', 'Unknown')}\nPurpose: {response.get('purpose', 'Unknown')}"
            })
        
        return formatted

def print_analysis_result(result: Dict):
    """Print analysis result in a formatted way"""
    if "error" in result:
        print(f"\nError: {result['error']}")
        if "raw_response" in result:
            print(f"\nRaw response: {result['raw_response']}")
        return
    
    print(f"\n{'=' * 50}")
    print(f"{result.get('title', 'Analysis Result'):^50}")
    print(f"{'=' * 50}")
    
    for section in result.get('sections', []):
        print(f"\n{section.get('heading', 'Section')}:")
        print(f"{'-' * len(section.get('heading', 'Section'))}")
        print(section.get('content', 'No content'))
    
    print(f"\n{'=' * 50}")