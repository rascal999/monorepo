"""Stock analysis module using OpenRouter models"""
import os
import json
import logging
import re
from typing import Dict
from openai import OpenAI
import httpx

logger = logging.getLogger(__name__)

class StockAnalyzer:
    def __init__(self, model: str):
        self.model = model
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
            
        # Configure client with custom transport
        transport = httpx.HTTPTransport(verify=False)  # Skip SSL verification if needed
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            http_client=httpx.Client(transport=transport)
        )

    def clean_json_response(self, content: str) -> str:
        """Clean model response to extract valid JSON"""
        # Remove markdown code blocks
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        
        # Remove newlines and extra spaces
        content = content.replace('\n', '')
        content = content.replace('    ', '')
        
        # Handle apostrophes and quotes properly
        content = content.replace("'", "\\'")  # Escape single quotes
        content = re.sub(r'(?<!\\)"', '\\"', content)  # Escape unescaped double quotes
        content = content.replace('\\"', '"')  # Unescape quotes at JSON property boundaries
        
        # Extract just the JSON object if there's extra text
        json_match = re.search(r'\{.*\}', content)
        if json_match:
            content = json_match.group(0)
            
        # Fix missing commas between properties
        content = re.sub(r'"([^"]+)"\s*"', r'"\1", "', content)  # Add comma between string values
        content = re.sub(r'(\d+(?:\.\d+)?)\s*"', r'\1, "', content)  # Add comma after numbers
        content = re.sub(r'}\s*"', r'}, "', content)  # Add comma after nested objects
        content = re.sub(r']\s*"', r'], "', content)  # Add comma after arrays
        
        # Ensure proper JSON structure
        if not content.startswith('{'):
            content = '{' + content
        if not content.endswith('}'):
            content = content + '}'
            
        logger.info(f"Cleaned JSON: {content}")
        return content

    def analyze_stock_data(self, _: str) -> Dict:
        """Analyze FTSE stocks to find the best investment opportunity"""
        try:
            # Prepare system message with web search instruction and strict output format
            system_message = """You are a stock market analyst with access to real-time market data and news.
            Search through all FTSE stocks to identify the single best investment opportunity right now.
            Consider:
            1. Current stock prices and recent price movements
            2. Latest news and market sentiment
            3. Trading volumes and market activity
            4. Company announcements and market events
            5. Sector performance and competitive positions

            Provide your analysis in this exact JSON format:
            {
                "recommendation": "buy|sell|hold",
                "stock": "STOCK_SYMBOL",
                "confidence": CONFIDENCE_SCORE,
                "reasoning": "BRIEF_EXPLANATION",
                "upsides": ["BULLET_POINT_1", "BULLET_POINT_2", "BULLET_POINT_3"],
                "downsides": ["BULLET_POINT_1", "BULLET_POINT_2"]
            }
            where:
            - CONFIDENCE_SCORE is a number between 0.0 and 1.0 based on the strength of available data and analysis
            - BULLET_POINTs are short, concise reasons (2-10 words each)
            
            IMPORTANT: Return ONLY the JSON object, no markdown formatting or other text."""

            # Prepare user message
            user_message = """Please analyze all FTSE stocks to identify the single best investment opportunity right now.
            Search for and consider:
            - Current market prices and trends across all FTSE stocks
            - Recent news articles and press releases
            - Trading patterns and volume
            - Market sentiment and analyst opinions
            - Sector performance and competitive positions
            
            Based on this real-time data, identify and analyze the FTSE stock that currently presents the strongest investment case."""

            # Log request details
            logger.info(f"Getting top FTSE stock pick from model {self.model}")
            logger.info(f"System message: {system_message}")
            logger.info(f"User message: {user_message}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )

            logger.info(f"Response: {response}")

            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                logger.info(f"Model response content: {content}")

                try:
                    # Clean and parse the response
                    cleaned_content = self.clean_json_response(content)
                    logger.info(f"Cleaned content: {cleaned_content}")
                    analysis = json.loads(cleaned_content)
                    
                    required_fields = ["recommendation", "stock", "confidence", "reasoning", "upsides", "downsides"]
                    if all(field in analysis for field in required_fields):
                        # Add model information to the analysis
                        analysis['model'] = self.model
                        return analysis
                    else:
                        missing_fields = [f for f in required_fields if f not in analysis]
                        logger.error(f"Missing required fields: {missing_fields}")
                        raise ValueError(f"Missing required fields: {missing_fields}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {str(e)}")
                    logger.debug(f"Raw content: {content}")
                    raise

            raise ValueError("No valid response from model")

        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            return {
                "recommendation": "hold",
                "stock": "ERROR",
                "confidence": 0.0,
                "reasoning": f"Analysis error: {str(e)}",
                "upsides": [],
                "downsides": [],
                "model": self.model  # Include model even in error case
            }
