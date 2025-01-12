"""Command line interface for postman2pytest."""

import sys
from pathlib import Path
from typing import Optional

import click

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
def main(input_file: Path, output: Path, version: bool) -> None:
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
        # Create output directory if it doesn't exist
        output.mkdir(parents=True, exist_ok=True)

        # Parse the Postman collection
        click.echo(f"Parsing Postman collection: {input_file}")
        collection = parse_collection(input_file)

        # Extract authentication configuration
        auth_config = None
        if collection.auth:
            auth_config = AuthHandler.extract_auth_config(collection.auth)
            if auth_config:
                click.echo(f"Found {auth_config.type} authentication configuration")

        # Generate test files
        click.echo(f"Generating pytest files in: {output}")
        generator = TestGenerator(output)
        generator.generate_tests(collection)

        click.echo("Conversion completed successfully!")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
