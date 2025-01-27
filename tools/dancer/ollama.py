#!/usr/bin/env python3

import os
import json
import re
import requests
from spinner import LoadingSpinner

class OllamaClient:
    def __init__(self, url, model):
        self.url = url.rstrip('/')
        self.model = model

    def clean_response(self, response):
        """Remove think tags and clean up response"""
        # Remove <think>...</think> blocks
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        # Remove any JSON blocks in code fences
        response = re.sub(r'```(?:json)?\s*\{.*?\}\s*```', '', response, flags=re.DOTALL)
        # Clean up extra whitespace
        response = re.sub(r'\n\s*\n', '\n\n', response.strip())
        return response

    def send_message(self, messages, is_processing=False):
        """Send messages to Ollama"""
        # Show appropriate thinking message
        if is_processing:
            print("\nProcessing Step: Analyzing command output...")
            thinking_msg = "Processing results..."
        else:
            print("\nPlanning Step: Analyzing request...")
            thinking_msg = "Planning next step..."
        
        with LoadingSpinner(thinking_msg) as spinner:
            try:
                response = requests.post(f"{self.url}/api/chat", json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False
                })
                response.raise_for_status()
                raw_response = response.json()["message"]["content"]
                return self.clean_response(raw_response)
            except Exception as e:
                return f"Error communicating with Ollama: {str(e)}"

    def build_messages(self, prompt, history, user_input, command_result=None):
        """Build messages array for Ollama"""
        messages = [
            {"role": "system", "content": prompt}
        ]
        
        # Add history
        for entry in history:
            messages.extend([
                {"role": "user", "content": entry["user_input"]},
                {"role": "assistant", "content": entry["response"]}
            ])
            if entry.get("command_result"):
                if "error" in entry["command_result"]:
                    messages.append({
                        "role": "system", 
                        "content": f"Command error: {json.dumps(entry['command_result'])}"
                    })
                else:
                    messages.append({
                        "role": "system", 
                        "content": f"Command output: {entry['command_result']['output']}"
                    })
        
        # Add current input
        messages.append({"role": "user", "content": user_input})
        
        # Add command result if provided
        if command_result:
            if "error" in command_result:
                messages.append({
                    "role": "system", 
                    "content": f"Command error: {json.dumps(command_result)}"
                })
            else:
                messages.append({
                    "role": "system", 
                    "content": f"Command output: {command_result['output']}"
                })
        
        return messages