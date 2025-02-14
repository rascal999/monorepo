"""Common utilities and constants"""
import os
from typing import List

# OpenRouter models with web search capability
MODELS = [
    "deepseek/deepseek-r1",
    "openai/chatgpt-4o-latest",
    "anthropic/claude-3.5-sonnet:beta"
]

def get_sample_stocks() -> List[str]:
    """Get a list of sample FTSE stocks to analyze"""
    return [
        "LLOY.L",  # Lloyds Banking Group
        "VOD.L",   # Vodafone Group
        "BP.L",    # BP plc
        "HSBA.L",  # HSBC Holdings
        "GSK.L"    # GSK plc
    ]