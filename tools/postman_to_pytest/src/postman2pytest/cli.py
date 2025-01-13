"""Command line interface for postman2pytest."""

import logging
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

# Configure root logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from . import __version__
from .parser import parse_collection
from .generator import TestGenerator
from .auth import AuthHandler


@click.command()
@click.argument('input_file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    '--output',
    '-o',
    type=click.Path(file_okay=False, path_type=Path),
    default='./tests',
    help='Output directory for generated tests',
)
@click.option('--version', is_flag=True, help='Show version information')
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Enable verbose debug output',
)
@click.option(
    '--env-file/--no-env-file',
    default=True,
    help='Generate .env.example template file with environment variables (default: enabled)',
)
def main(input_file: Path, output: Path, version: bool, env_file: bool, verbose: bool) -> None:
    """Convert Postman collection JSON files into pytest test files.

    Args:
        input_file: Path to Postman collection JSON file
        output: Directory where test files will be generated
        version: Show version information and exit
    """
    if version:
        click.echo(f"postman2pytest version {__version__}")
        sys.exit(0)

    try:
        # Configure logging level
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.getLogger('postman2pytest').setLevel(log_level)
        logger.debug("Debug logging enabled")
        
        # Load environment variables
        load_dotenv()
        logger.debug("Loaded environment variables")

        # Create output directory if it doesn't exist
        output.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created output directory: {output}")

        # Parse the Postman collection
        click.echo(f"Parsing Postman collection: {input_file}")
        logger.debug(f"Reading collection file: {input_file}")
        collection = parse_collection(input_file)

        # Initialize auth handler and extract configuration
        logger.debug("Initializing authentication handler")
        auth_handler = AuthHandler()
        auth_config = None
        if collection.auth:
            auth_config = auth_handler.extract_auth_config(collection.auth)
            if auth_config:
                click.echo(f"Found {auth_config.type} authentication configuration")

        # Generate test files
        click.echo(f"Generating pytest files in: {output}")
        logger.debug("Initializing test generator")
        # Use tools/postman_to_pytest as project root
        project_root = Path(__file__).parent.parent.parent
        generator = TestGenerator(
            output, 
            auth_handler, 
            env_file=env_file,
            project_root=project_root
        )
        generator.generate_tests(collection, auth_config)
        
        # Report variable extraction results
        if generator.variables:
            click.echo(f"\nExtracted {len(generator.variables)} variables:")
            by_type = {}
            for var in generator.variables.values():
                if var.type not in by_type:
                    by_type[var.type] = []
                by_type[var.type].append(var.name)
            
            for var_type, vars in by_type.items():
                click.echo(f"  {var_type.value}: {', '.join(vars)}")
            
            # Report generated files
            registry_path = project_root / 'variable_registry.json'
            if registry_path.exists():
                click.echo(f"\nVariable registry: {registry_path}")
                dest_registry = output / 'variable_registry.json'
                click.echo(f"Copied to: {dest_registry}")
            
            if env_file:
                env_path = output / '.env'
                click.echo(f"Generated environment file: {env_path}")

        click.echo("\nConversion completed successfully!")
        logger.debug("Test generation process completed")

    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}", exc_info=True)
        click.echo(f"Error: {str(e)}", err=True)
        if verbose:
            click.echo("\nFull error details (run with --verbose to see these):", err=True)
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
