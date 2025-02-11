"""Utilities for file operations."""

import os
from pathlib import Path
import shutil
import re
import logging
from .constants import MAX_FILENAME_LENGTH

def make_filename(original_name, suffix, max_length=MAX_FILENAME_LENGTH):
    """Create filename with suffix, ensuring total length <= max_length."""
    stem = Path(original_name).stem
    ext = Path(original_name).suffix
    suffix_len = len(suffix) + 1  # +1 for underscore
    ext_len = len(ext)
    max_stem_len = max_length - suffix_len - ext_len
    
    if len(stem) > max_stem_len:
        stem = stem[:max_stem_len]
    
    return f"{stem}_{suffix}{ext}"

def copy_and_rename(src_path, dest_dir, suffix):
    """Copy file to destination with suffix."""
    try:
        src_path = Path(src_path)
        new_name = make_filename(src_path.name, suffix)
        dest_path = dest_dir / new_name
        
        # Create parent directory if it doesn't exist
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy the file
        shutil.copy2(src_path, dest_path)
        return dest_path
    
    except Exception as e:
        logging.error(f"Error copying {src_path}: {e}")
        return None

def setup_output_dirs(base_dir):
    """Create output directories for internal medicine and surgery."""
    base_dir = Path(base_dir)
    
    # Create main directories
    internal_medicine_dir = base_dir / 'internal_medicine'
    surgical_dir = base_dir / 'surgical'
    rejected_dir = base_dir / 'rejected'
    
    # Create all directories
    for directory in [internal_medicine_dir, surgical_dir, rejected_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    return {
        'Internal Medicine': internal_medicine_dir,
        'Surgery': surgical_dir
    }, rejected_dir