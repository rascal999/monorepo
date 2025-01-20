"""
Utilities for handling file operations.
"""
import os
import shutil
from pathlib import Path

def copy_env_file(base_dir: str, output_dir: str):
    """Copy .env to output directory."""
    src = os.path.join(base_dir, '.env')
    dst = os.path.join(output_dir, '.env')
    print(f"\n=== Copying .env file ===")
    print(f"Source path: {src}")
    print(f"Destination path: {dst}")
    print(f"Source exists: {os.path.exists(src)}")
    if os.path.exists(src):
        print("Copying file...")
        os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists
        shutil.copy2(src, dst)
        print("File copied successfully")
    else:
        print("WARNING: Source .env file not found")

def copy_conftest_file(base_dir: str, output_dir: str):
    """Copy conftest.py to output directory."""
    src = os.path.join(base_dir, 'conftest.py')
    dst = os.path.join(output_dir, 'conftest.py')
    if os.path.exists(src):
        shutil.copy2(src, dst)

def create_directory_structure(output_dir: str):
    """Create the basic directory structure for tests."""
    # Create root __init__.py file
    init_file = os.path.join(output_dir, '__init__.py')
    os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('"""Generated test package."""\n')

def normalize_path(path_parts: list) -> list:
    """Normalize path parts to match expected structure."""
    # Convert path parts to lowercase and replace spaces with underscores
    return [part.lower().replace(' ', '_') for part in path_parts]

def create_test_directory(base_dir: str, path_parts: list) -> str:
    """Create a directory for test files and return its path."""
    # Normalize path parts
    normalized_parts = normalize_path(path_parts)
    
    # Start with base directory
    current_dir = base_dir
    
    # Create each directory in path, adding __init__.py files
    for part in normalized_parts:
        current_dir = os.path.join(current_dir, part)
        os.makedirs(current_dir, exist_ok=True)
        init_file = os.path.join(current_dir, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('"""Generated test package."""\n')
    
    return current_dir
