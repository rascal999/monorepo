"""Prompt loading utilities"""

import os

def load_prompt(name):
    """Load a prompt from a file"""
    prompt_path = os.path.join(os.path.dirname(__file__), f"{name}.txt")
    with open(prompt_path, 'r') as f:
        return f.read().strip()

# Load prompts at module import time
DETAILED_SUMMARY = load_prompt('detailed_summary')
CONCISE_SUMMARY = load_prompt('concise_summary')
QUERY_RESPONSE = load_prompt('query_response')
JQL_QUERY = load_prompt('jql_query')