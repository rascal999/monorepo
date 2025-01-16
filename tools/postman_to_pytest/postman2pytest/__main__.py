"""
Main entry point for the Postman to Pytest converter.
"""

import sys
import argparse
from pathlib import Path
from .parser import parse_postman_collection, parse_dependency_config
from .resolver import DependencyResolver
from .generator import TestGenerator

def main():
    parser = argparse.ArgumentParser(
        description='Convert Postman collections to Pytest test cases'
    )
    parser.add_argument(
        'collection',
        type=str,
        help='Path to the Postman collection JSON file'
    )
    parser.add_argument(
        'dependencies',
        type=str,
        help='Path to the dependency configuration YAML file'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='generated_tests',
        help='Directory to output generated test files (default: generated_tests)'
    )

    args = parser.parse_args()

    try:
        # Parse input files
        print(f"Parsing Postman collection: {args.collection}")
        requests = parse_postman_collection(args.collection)
        print(f"Found {len(requests)} requests")

        print(f"Parsing dependency configuration: {args.dependencies}")
        config = parse_dependency_config(args.dependencies)

        # Resolve dependencies
        print("Resolving dependencies...")
        resolver = DependencyResolver(requests, config)
        ordered_requests = resolver.resolve_order()
        print(f"Resolved {len(ordered_requests)} requests in dependency order")

        # Generate test files
        print(f"Generating test files in: {args.output_dir}")
        generator = TestGenerator(args.output_dir)
        generator.generate_test_files(requests, resolver)
        print("Generated test files in directory structure matching Postman collection")

        print("\nConversion completed successfully!")
        print("\nTo run the tests:")
        print("1. Create a .env file with required environment variables:")
        print("   ENV_URL=<your_api_url>")
        print("   CLIENT_ID=<your_client_id>")
        print("   API_KEY=<your_api_key>")
        print("\n2. Install dependencies:")
        print("   pip install -r requirements.txt")
        print("\n3. Run the tests:")
        print(f"   pytest {args.output_dir} -v")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
