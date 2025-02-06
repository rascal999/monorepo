import os
import json
import socket
import logging
from datetime import datetime
from pathlib import Path

def mask_sensitive_values(env_vars):
    """Mask values of environment variables containing 'KEY' or 'TOKEN',
    showing first 12 and last 3 characters."""
    masked_vars = {}
    for key, value in env_vars.items():
        if 'KEY' in key.upper() or 'TOKEN' in key.upper():
            if value and len(value) > 16:
                # Show first 12 and last 3 chars, mask middle with asterisks
                masked_vars[key] = f"{value[:12]}{'*' * (len(value)-15)}{value[-3:]}"
            elif value and len(value) > 3:
                # For shorter values, show all but last 3 chars
                masked_vars[key] = f"{value[:-3]}***"
            else:
                # If value is too short, just show as is
                masked_vars[key] = value if value else ""
        else:
            masked_vars[key] = value
    return masked_vars

def setup_logging():
    # Get container ID (hostname in Docker)
    container_id = socket.gethostname()
    
    # Get timestamp
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    
    # Get log directory from environment
    log_dir = os.getenv('LOG_DIRECTORY', '/workspace/logs')
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Create logger
    logger = logging.getLogger('APP_NAME')  # Will be replaced by create_project.sh
    logger.setLevel(getattr(logging, log_level))
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Create file handler
    log_path = Path(log_dir) / f'{timestamp}-{container_id}.log'
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

def main():
    # Set up logging
    logger = setup_logging()
    
    # Get all environment variables and mask sensitive values
    env_vars = dict(os.environ)
    masked_vars = mask_sensitive_values(env_vars)
    
    # Log environment variables
    logger.info("Environment variables:\n%s", json.dumps(masked_vars, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()