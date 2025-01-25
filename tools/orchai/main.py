#!/usr/bin/env python3
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set default level to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set orchai logger to DEBUG
orchai_logger = logging.getLogger('orchai')
orchai_logger.setLevel(logging.DEBUG)

# Set other loggers to WARNING to reduce noise
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('docker').setLevel(logging.WARNING)
logging.getLogger('git').setLevel(logging.WARNING)

logger = logging.getLogger('orchai')

def main():
    try:
        from core.orchestrator import Orchestrator
        orchestrator = Orchestrator()
        orchestrator.start()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        if 'orchestrator' in locals() and hasattr(orchestrator, 'cleanup'):
            orchestrator.cleanup()
        raise

if __name__ == '__main__':
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(__file__))
    main()