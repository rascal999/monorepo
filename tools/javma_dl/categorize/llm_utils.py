"""Utilities for LLM operations."""

import json
import requests
import logging
import time
from .constants import SPECIALTIES, SURGICAL_CATEGORIES, INTERNAL_MEDICINE_CATEGORIES

def call_qwen_api(prompt, max_retries=3, retry_delay=2):
    """Call qwen API with retries."""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'qwen2.5:14b',
                    'prompt': prompt,
                    'stream': False
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                logging.warning(f"API call attempt {attempt + 1} failed: {e}")
                time.sleep(retry_delay)
            else:
                logging.error(f"All API call attempts failed: {e}")
                return None

def analyze_with_qwen(text, pdf_path):
    """Use qwen to analyze text and determine article type, species focus, and specialty."""
    specialties_str = "\n".join([
        "- Surgery (any surgical procedures or operations)",
        "Internal Medicine subspecialties:",
        *[f"- {specialty}" for specialty in INTERNAL_MEDICINE_CATEGORIES if specialty != "Surgery"]
    ])
    
    prompt = f"""Analyze this veterinary journal article text and determine:

1. Is this a proper research/scientific journal article? (not news, editorial, book review, etc.)
2. Does this article specifically focus on dogs and/or cats? (exclude if about other species)
3. Determine the specialty:
   - If it involves ANY surgical procedures, operations, or surgical techniques, classify as "Surgery"
   - Otherwise, classify into one of these internal medicine specialties:
{specialties_str}

Consider:
- Must be a research article (has methods, results, etc.)
- Must focus specifically on dogs and/or cats (not horses, livestock, or exotic pets)
- ANY surgical content should be classified as "Surgery"
- Medical management articles should be classified by their primary subspecialty
- If unclear or doesn't fit any category, use "None"

Text from first 2 pages:
{text[:3000]}  # Use first 3000 chars for context

Return a valid JSON object with this exact structure:
{{
    "is_journal_article": true/false,
    "is_small_animal": true/false,
    "reason": "Brief explanation of classification",
    "specialty": "Name of best matching specialty or None",
    "confidence": 0-100,
    "species_mentioned": ["list", "of", "species"],
    "keywords": ["key", "terms", "found"]
}}
"""
    
    # Call API with retries
    result = call_qwen_api(prompt)
    if not result or 'response' not in result:
        return None
    
    # Try to parse JSON response
    try:
        # Log raw response for debugging
        logging.debug(f"Raw API response for {pdf_path}: {result['response']}")
        
        # Clean up response - remove any leading/trailing text
        json_str = result['response']
        json_start = json_str.find('{')
        json_end = json_str.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = json_str[json_start:json_end]
        
        # Parse JSON
        analysis = json.loads(json_str)
        
        # Validate required fields
        required_fields = ['is_journal_article', 'is_small_animal', 'specialty', 'confidence']
        if not all(field in analysis for field in required_fields):
            logging.error(f"Missing required fields in response for {pdf_path}")
            return None
        
        # Map any surgical specialty to "Surgery"
        if analysis['specialty'] in SURGICAL_CATEGORIES:
            analysis['specialty'] = "Surgery"
        
        # Validate specialty
        valid_specialties = {"Surgery", "None"}.union(INTERNAL_MEDICINE_CATEGORIES)
        if analysis['specialty'] not in valid_specialties:
            logging.error(f"Invalid specialty '{analysis['specialty']}' for {pdf_path}")
            analysis['specialty'] = "None"
            analysis['confidence'] = 0
        
        # Force low confidence for unclear specialty
        if analysis['specialty'] == "None":
            analysis['confidence'] = 0
        
        return analysis
        
    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error for {pdf_path}: {e}")
        logging.error(f"Raw response: {result['response']}")
        return None
    except Exception as e:
        logging.error(f"Error processing response for {pdf_path}: {e}")
        return None