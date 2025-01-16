"""
File utility functions for managing test files and directories.
"""
import os
import shutil
from typing import List

def copy_env_file(base_dir: str, output_dir: str) -> None:
    """Copy .env file from project root to output directory."""
    src_env = os.path.join(base_dir, '.env')
    src_env_sample = os.path.join(base_dir, '.env.sample')
    dst_env = os.path.join(output_dir, '.env')
    
    if os.path.exists(src_env):
        shutil.copy2(src_env, dst_env)
    elif os.path.exists(src_env_sample):
        shutil.copy2(src_env_sample, dst_env)
    else:
        raise FileNotFoundError(f"Required .env file not found at {src_env} or {src_env_sample}")

def copy_conftest_file(base_dir: str, output_dir: str) -> None:
    """Copy conftest.py from project root to output directory."""
    src_conftest = os.path.join(base_dir, 'conftest.py')
    dst_conftest = os.path.join(output_dir, 'conftest.py')
    if os.path.exists(src_conftest):
        shutil.copy2(src_conftest, dst_conftest)
    else:
        raise FileNotFoundError(f"Required conftest.py file not found at {src_conftest}")

def create_directory_structure(output_dir: str) -> None:
    """Create the directory structure for generated tests."""
    os.makedirs(output_dir, exist_ok=True)
    init_file = os.path.join(output_dir, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('')

def create_test_directory(output_dir: str, path_parts: List[str]) -> str:
    """Create directory structure for a test file and return the output path."""
    if not path_parts:
        return output_dir
    
    folder_path = os.path.join(output_dir, *[p.lower().replace(' ', '_') for p in path_parts])
    os.makedirs(folder_path, exist_ok=True)
    
    # Create __init__.py files
    current_path = output_dir
    for folder in path_parts:
        current_path = os.path.join(current_path, folder.lower().replace(' ', '_'))
        init_file = os.path.join(current_path, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('')
    
    return folder_path
