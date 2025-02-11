#!/usr/bin/env python3

import os
from pathlib import Path
import shutil
import sys
import argparse

def setup_output_dir(base_dir):
    """Create and return the output directory path."""
    output_dir = base_dir / 'internal_medicine_articles'
    
    # Create with numerical suffix if exists
    if output_dir.exists():
        counter = 1
        while (base_dir / f'internal_medicine_articles_{counter}').exists():
            counter += 1
        output_dir = base_dir / f'internal_medicine_articles_{counter}'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def copy_with_structure(src_path, output_base, relative_to):
    """
    Copy file maintaining directory structure relative to a base path.
    
    Args:
        src_path: Path to source file
        output_base: Base output directory
        relative_to: Path to make structure relative to
    """
    try:
        # Convert paths to Path objects
        src_path = Path(src_path)
        relative_to = Path(relative_to)
        
        # Get relative path from base
        try:
            rel_path = src_path.relative_to(relative_to)
        except ValueError:
            print(f"Error: {src_path} is not relative to {relative_to}")
            return False
        
        # Construct destination path
        dest_path = output_base / rel_path
        
        # Create parent directories
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(src_path, dest_path)
        return True
        
    except Exception as e:
        print(f"Error copying {src_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Copy internal medicine articles to new directory maintaining structure.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Use default paths
  %(prog)s -o /path/to/output # Specify output directory
  %(prog)s -b /path/to/base   # Specify base directory for relative paths
""")
    
    parser.add_argument('-o', '--output',
                       help='Output directory (default: script directory)')
    parser.add_argument('-b', '--base',
                       help='Base directory for relative paths (default: current directory)')
    
    args = parser.parse_args()
    
    # Get script directory
    script_dir = Path(__file__).parent
    
    # Set input file path
    input_file = script_dir / 'internal_medicine_articles.txt'
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Set output directory
    if args.output:
        output_base = Path(args.output).expanduser().resolve()
    else:
        output_base = script_dir
    
    # Set base directory for relative paths
    if args.base:
        base_dir = Path(args.base).expanduser().resolve()
    else:
        base_dir = Path.cwd()
    
    # Create output directory
    output_dir = setup_output_dir(output_base)
    print(f"Created output directory: {output_dir}")
    
    # Read and process files
    try:
        with open(input_file, 'r') as f:
            files = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    if not files:
        print("No files found in input file")
        sys.exit(1)
    
    print(f"Found {len(files)} files to copy")
    
    # Copy files
    success_count = 0
    error_count = 0
    
    for i, file_path in enumerate(files, 1):
        print(f"\rCopying file {i}/{len(files)}: {Path(file_path).name}", end='', flush=True)
        
        if copy_with_structure(file_path, output_dir, base_dir):
            success_count += 1
        else:
            error_count += 1
            print()  # New line after error message
    
    # Clear progress line
    print("\r" + " " * 80 + "\r", end='', flush=True)
    
    # Print summary
    print(f"\nCopy complete!")
    print(f"Successfully copied: {success_count}")
    if error_count:
        print(f"Errors: {error_count}")
    print(f"\nFiles copied to: {output_dir}")

if __name__ == "__main__":
    main()