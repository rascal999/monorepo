#!/usr/bin/env python3
import time
import subprocess
import sys
import requests
from pathlib import Path

# Configuration
ACCESS_LOG = "/var/log/nginx/access.log"
BLOCKED_IPS = "/etc/nginx/blocked_ips.conf"
OLLAMA_URL = "http://host.docker.internal:11343/api/generate"

def log(msg):
    print(f"[MONITOR] {msg}", flush=True)

def block_ip(ip):
    log(f"Blocking IP: {ip}")
    with open(BLOCKED_IPS, "a") as f:
        f.write(f"{ip} 1;\n")
    subprocess.run(["nginx", "-s", "reload"])

def classify_request(ip, raw_request):
    log(f"Classifying request from {ip}...")
    
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "qwen2.5:7b-instruct",
            "prompt": f"""Analyze this HTTP request and determine if it's suspicious or malicious:

{raw_request}

Respond with either 'suspicious' or 'normal' based on:
1. If it's trying to access admin/system paths
2. If it contains SQL injection attempts
3. If it has suspicious headers or payloads
4. If it's probing for vulnerabilities
5. If it's attempting to exploit common web vulnerabilities

Response:"""
        }, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            is_suspicious = "suspicious" in result.get("response", "").lower()
            log(f"Classification result: {'suspicious' if is_suspicious else 'normal'}")
            return is_suspicious
            
    except Exception as e:
        log(f"Error calling Ollama: {e}")
    
    return False

def process_request(lines):
    if not lines:
        return
        
    # Get IP from first line
    try:
        ip = lines[0].split(" - ")[0]
    except:
        return
        
    # Skip static files and health checks
    first_line = lines[0].lower()
    if any(ext in first_line for ext in [".css", ".js", ".jpg", ".png", ".ico", ".woff", "/health"]):
        return
        
    # Join lines into raw request
    raw_request = "\n".join(lines)
    log(f"Processing request:\n{raw_request}")
    
    # Classify and block if suspicious
    if classify_request(ip, raw_request):
        block_ip(ip)

def main():
    log("Starting monitor...")
    Path(BLOCKED_IPS).touch()
    
    current_request = []
    
    try:
        process = subprocess.Popen(['tail', '-f', ACCESS_LOG], 
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)

        while True:
            line = process.stdout.readline().strip()
            if not line:
                continue
                
            # New request starts with IP address
            if " - [" in line:
                # Process previous request
                process_request(current_request)
                current_request = [line]
            # Continuation of current request
            elif "client" not in line and "keepalive connection" not in line:
                current_request.append(line)

    except KeyboardInterrupt:
        log("Shutting down...")
    except Exception as e:
        log(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()