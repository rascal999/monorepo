"""
Utilities for handling file operations.
"""
import os
import shutil
from pathlib import Path

def copy_env_file(base_dir: str, output_dir: str):
    """Copy .env.sample to .env if it doesn't exist."""
    src = os.path.join(base_dir, '.env.sample')
    dst = os.path.join(output_dir, '.env')
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.copy2(src, dst)

def copy_conftest_file(base_dir: str, output_dir: str):
    """Copy conftest.py to output directory."""
    src = os.path.join(base_dir, 'conftest.py')
    dst = os.path.join(output_dir, 'conftest.py')
    if os.path.exists(src):
        shutil.copy2(src, dst)

def create_directory_structure(output_dir: str):
    """Create the basic directory structure for tests."""
    # Create __init__.py files in output directory and subdirectories
    init_files = [
        os.path.join(output_dir, '__init__.py'),
        os.path.join(output_dir, 'all_mangopay_endpoints', '__init__.py'),
        os.path.join(output_dir, 'all_mangopay_endpoints', 'users', '__init__.py'),
    ]
    
    for init_file in init_files:
        os.makedirs(os.path.dirname(init_file), exist_ok=True)
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('"""Generated test package."""\n')

def normalize_path(path_parts: list) -> list:
    """Normalize path parts to match expected structure."""
    # Convert path parts to lowercase and replace spaces with underscores
    normalized = []
    for part in path_parts:
        if part == "All Mangopay endpoints":
            normalized.append("all_mangopay_endpoints")
        elif part == "Users":
            normalized.append("users")
        else:
            normalized.append(part.lower().replace(' ', '_'))
    return normalized

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
