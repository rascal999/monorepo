#!/usr/bin/env python3
"""Command line interface for darkquery."""
import click
import logging
import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv

from .shell import DarkQueryShell
from .datasources.base import DataSource
from .datasources.jira import JIRADataSource
from .datasources.files import FileDataSource


def load_config() -> Dict[str, Dict[str, str]]:
    """Load configuration from environment variables.
    
    Returns:
        Dict containing configuration for data sources and Ollama
    """
    # Load .env file from the project root
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
    
    config = {
        'jira': {
            'url': os.getenv('JIRA_URL'),
            'email': os.getenv('JIRA_EMAIL'),
            'token': os.getenv('JIRA_TOKEN')
        },
        'ollama': {
            'url': os.getenv('OLLAMA_URL', 'http://localhost:11434'),
            'model': os.getenv('OLLAMA_MODEL', 'deepseek-r1-14b-32k:latest')
        }
    }
    
    return config


def setup_data_sources(config: Dict[str, Dict[str, str]]) -> Dict[str, DataSource]:
    """Set up data sources with configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dict mapping source names to DataSource instances
    """
    sources = {}
    
    # Initialize JIRA data source if configured
    jira_config = config.get('jira', {})
    if all(jira_config.values()):
        sources['jira'] = JIRADataSource(jira_config)
    
    # Initialize file data source (always available)
    sources['files'] = FileDataSource()
    
    return sources


@click.command()
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose logging of model messages')
def main(verbose: bool) -> None:
    """Interactive CLI tool for querying tickets and analyzing code."""
    # Set up logging
    log_level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('darkquery')
    
    try:
        # Load configuration
        config = load_config()
        
        if verbose:
            logger.info(f"Using Ollama model: {config['ollama']['model']}")
        
        # Set up data sources
        data_sources = setup_data_sources(config)
        
        if not data_sources:
            logger.error("No data sources configured")
            raise click.ClickException("No data sources configured. Please check your configuration.")
        
        # Start interactive shell with Ollama config
        shell = DarkQueryShell(
            data_sources=data_sources,
            ollama_url=config['ollama']['url'],
            ollama_model=config['ollama']['model'],
            verbose=verbose
        )
        shell.start()
        
    except Exception as e:
        logger.exception("Error starting darkquery")
        raise click.ClickException(str(e))


if __name__ == '__main__':
    main()