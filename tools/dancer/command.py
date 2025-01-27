#!/usr/bin/env python3

import os
import json
import re
import subprocess
from spinner import LoadingSpinner

class CommandExecutor:
    def __init__(self):
        # Define read-only commands
        self.read_only_commands = {
            'fetch_ticket', 'jql_search',
            'list_group_repos', 'list_repo_files', 'read_repo_files',
            'list_repo_issues', 'read_repo_issue',
            'list_repo_mrs', 'read_repo_mr'
        }
        
        # Map commands to script paths
        self.script_paths = {
            # Jira scripts
            'fetch_ticket': 'scripts/jira/fetch_ticket.py',
            'jql_search': 'scripts/jira/jql_search.py',
            'add_comment': 'scripts/jira/add_comment.py',
            'delete_ticket': 'scripts/jira/delete_ticket.py',
            # GitLab scripts
            'list_group_repos': 'scripts/gitlab/list_group_repos.py',
            'list_repo_files': 'scripts/gitlab/list_repo_files.py',
            'read_repo_files': 'scripts/gitlab/read_repo_files.py',
            'list_repo_issues': 'scripts/gitlab/list_repo_issues.py',
            'read_repo_issue': 'scripts/gitlab/read_repo_issue.py',
            'list_repo_mrs': 'scripts/gitlab/list_repo_mrs.py',
            'read_repo_mr': 'scripts/gitlab/read_repo_mr.py'
        }

    def execute(self, cmd_data):
        """Execute a script with given arguments"""
        try:
            script = cmd_data.get('command')
            args = cmd_data.get('args', [])
            description = cmd_data.get('description', '')
            next_step = cmd_data.get('next_step', 'Processing result')
            
            if script not in self.script_paths:
                return {"error": f"Unknown command '{script}'"}
            
            script_path = os.path.join(os.path.dirname(__file__), self.script_paths[script])
            if not os.path.exists(script_path):
                return {"error": f"Script not found: {script_path}"}
            
            # Print what we're doing
            print(f"\nCommand Step: {description}")
            print(f"Executing: {script} {' '.join(args)}")
            print(f"Next Step: {next_step}")
            
            # Check if command requires confirmation
            if script not in self.read_only_commands:
                confirm = input(f"\nThis operation will modify data. Proceed? (y/N): ")
                if confirm.lower() != 'y':
                    return {"error": "Operation cancelled by user"}
            
            # Execute with loading spinner
            with LoadingSpinner("Executing command...") as spinner:
                result = subprocess.run(
                    [script_path] + args,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    return {
                        "error": "Command failed",
                        "details": result.stderr,
                        "command": f"{script} {' '.join(args)}"
                    }
                
                return {"output": result.stdout}
                
        except Exception as e:
            return {"error": str(e)}

    def extract_command(self, response):
        """Extract command JSON from response"""
        try:
            # First try to find JSON in code block
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            
            # Then try to find bare JSON
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1:
                return json.loads(response[start:end + 1])
            
            return None
        except json.JSONDecodeError:
            return None