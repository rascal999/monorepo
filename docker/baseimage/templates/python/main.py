import os
import json
import socket
import logging
import argparse
from datetime import datetime
from pathlib import Path

def mask_sensitive_values(env_vars):
    """Mask values of sensitive environment variables.
    For variables containing sensitive keywords, shows first 12 and last 3 characters
    if long enough, otherwise masks appropriately. Excludes URLs and other non-sensitive patterns."""
    SENSITIVE_KEYWORDS = {'KEY', 'TOKEN', 'PASSWORD', 'SECRET', 'CREDENTIAL', 'CERT', 'PRIVATE'}
    # Keywords that indicate the value should not be masked even if the key contains sensitive words
    EXCLUDE_PATTERNS = [
        'http://', 'https://',
        '.com', '.org', '.net', '.io',  # Common URL TLDs
        '_URL', '_ENDPOINT', '_URI',     # URL-related suffixes
        'OAUTH_TOKEN_EXPIRY'  # Non-sensitive OAuth config
    ]
    
    masked_vars = {}
    for key, value in env_vars.items():
        # Skip masking if value is None or empty
        if not value:
            masked_vars[key] = value
            continue
            
        # Check if key contains sensitive keywords
        if any(keyword in key.upper() for keyword in SENSITIVE_KEYWORDS):
            # Don't mask if value matches exclusion patterns
            if any(pattern.lower() in str(value).lower() for pattern in EXCLUDE_PATTERNS) or \
               any(suffix in key.upper() for suffix in ['_URL', '_ENDPOINT', '_URI']):
                masked_vars[key] = value
                continue
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

def parse_args():
    parser = argparse.ArgumentParser(description='APP_NAME application')  # Will be replaced by create_project.sh
    parser.add_argument('args', nargs='*', help='Additional arguments passed to the application')
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_args()
    
    # Set up logging
    logger = setup_logging()
    
    # Get all environment variables and mask sensitive values
    env_vars = dict(os.environ)
    masked_vars = mask_sensitive_values(env_vars)
    
    # Log environment variables
    logger.info("Environment variables:\n%s", json.dumps(masked_vars, indent=2, sort_keys=True))
    
    # Log command line arguments if any were provided
    if args.args:
        logger.info("Command line arguments: %s", args.args)

if __name__ == '__main__':
    main()