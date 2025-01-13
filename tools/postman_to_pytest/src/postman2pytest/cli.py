"""Command line interface for postman2pytest."""

import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

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
    '--env-file/--no-env-file',
    default=True,
    help='Generate .env.example template file with environment variables (default: enabled)',
)
def main(input_file: Path, output: Path, version: bool, env_file: bool) -> None:
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
        # Load environment variables
        load_dotenv()

        # Create output directory if it doesn't exist
        output.mkdir(parents=True, exist_ok=True)

        # Parse the Postman collection
        click.echo(f"Parsing Postman collection: {input_file}")
        collection = parse_collection(input_file)

        # Initialize auth handler and extract configuration
        auth_handler = AuthHandler()
        auth_config = None
        if collection.auth:
            auth_config = auth_handler.extract_auth_config(collection.auth)
            if auth_config:
                click.echo(f"Found {auth_config.type} authentication configuration")

        # Generate test files
        click.echo(f"Generating pytest files in: {output}")
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

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
