#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv
from spinner import LoadingSpinner
from command import CommandExecutor
from ollama import OllamaClient

class DancerShell:
    def __init__(self):
        load_dotenv()
        
        # Load environment variables
        self.OLLAMA_URL = os.getenv('OLLAMA_URL')
        self.OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')
        
        if not all([self.OLLAMA_URL, self.OLLAMA_MODEL]):
            print("Error: Missing required environment variables (OLLAMA_URL, OLLAMA_MODEL)")
            sys.exit(1)
        
        # Initialize components
        self.history = []
        self.command_executor = CommandExecutor()
        self.ollama_client = OllamaClient(self.OLLAMA_URL, self.OLLAMA_MODEL)
        self.prompt = self.load_prompt()

    def load_prompt(self):
        """Load the prompt template"""
        try:
            with open(os.path.join(os.path.dirname(__file__), 'prompt/prompt.txt'), 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading prompt template: {e}")
            sys.exit(1)

    def process_response(self, response):
        """Process Ollama's response - look for command or text"""
        try:
            # Extract command if present
            cmd_data = self.command_executor.extract_command(response)
            if cmd_data and all(k in cmd_data for k in ("command", "args", "description")):
                # Execute command
                result = self.command_executor.execute(cmd_data)
                
                # Store command result in history
                self.history[-1]["command_result"] = result
                
                # Get next step from model
                messages = self.ollama_client.build_messages(
                    self.prompt,
                    self.history,
                    "Process this command result and provide a formatted summary:",
                    result
                )
                next_response = self.ollama_client.send_message(messages, is_processing=True)
                return next_response
            
            # If no command found, return the response as is
            return response
        except Exception as e:
            return f"Error processing response: {str(e)}"

    def run(self):
        """Run the interactive shell"""
        print(f"Dancer Shell - Connected to {self.OLLAMA_MODEL} at {self.OLLAMA_URL}")
        print("Type 'exit' to quit")
        print("-" * 50)

        while True:
            try:
                user_input = input("\ndancer> ").strip()
                if not user_input:
                    continue
                if user_input.lower() == 'exit':
                    break

                # Add history entry for this interaction
                history_entry = {
                    "user_input": user_input,
                    "response": None,
                    "command_result": None
                }
                self.history.append(history_entry)

                # Get initial response from Ollama
                messages = self.ollama_client.build_messages(self.prompt, self.history, user_input)
                response = self.ollama_client.send_message(messages)
                
                # Store response in history
                self.history[-1]["response"] = response
                
                # Process response and handle any commands
                result = self.process_response(response)
                
                # Print any text output
                if result and not result.startswith('Error:'):
                    print("\nResult:")
                    print(result)

            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
                if self.history:
                    self.history.pop()  # Remove incomplete interaction
            except Exception as e:
                print(f"Error: {str(e)}")
                if self.history:
                    self.history.pop()  # Remove failed interaction

if __name__ == "__main__":
    shell = DancerShell()
    shell.run()