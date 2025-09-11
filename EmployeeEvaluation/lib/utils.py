"""
Utility Functions

This module contains helper functions and utilities for the Employee Evaluation system.
"""

import os
import sys
from typing import List, Dict, Any
from datetime import datetime


def get_project_root() -> str:
    """
    Get the project root directory (parent of lib folder).
    
    Returns:
        Path to the project root directory
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ensure_output_directory(output_dir: str = None) -> str:
    """
    Ensure the output directory exists, create if it doesn't.
    
    Args:
        output_dir: Directory path for output files
        
    Returns:
        Path to the output directory
    """
    if output_dir is None:
        output_dir = get_project_root()
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    return output_dir


def get_timestamp() -> str:
    """
    Get current timestamp in a readable format.
    
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_input_files(input_dir: str = None) -> List[str]:
    """
    Validate and get list of input files.
    
    Args:
        input_dir: Directory to search for input files
        
    Returns:
        List of valid input file paths
    """
    if input_dir is None:
        input_dir = get_project_root()
    
    input_files = []
    for filename in os.listdir(input_dir):
        if filename.startswith('INPUT') and filename.endswith('.txt'):
            filepath = os.path.join(input_dir, filename)
            if os.path.isfile(filepath):
                input_files.append(filepath)
    
    return sorted(input_files)


def log_info(message: str) -> None:
    """
    Log info message to console.
    
    Args:
        message: Message to log
    """
    timestamp = get_timestamp()
    print(f"[{timestamp}] INFO: {message}")


def log_error(message: str) -> None:
    """
    Log error message to console.
    
    Args:
        message: Error message to log
    """
    timestamp = get_timestamp()
    print(f"[{timestamp}] ERROR: {message}", file=sys.stderr)


def log_warning(message: str) -> None:
    """
    Log warning message to console.
    
    Args:
        message: Warning message to log
    """
    timestamp = get_timestamp()
    print(f"[{timestamp}] WARNING: {message}")


def safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def get_file_info(filepath: str) -> Dict[str, Any]:
    """
    Get file information.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Dictionary containing file information
    """
    if not os.path.exists(filepath):
        return {}
    
    stat = os.stat(filepath)
    return {
        'path': filepath,
        'size': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'modified': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        'created': datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
    }


def print_summary(employees: List[Dict[str, str]], all_fields: List[str], output_files: List[str]) -> None:
    """
    Print a summary of the processing results.
    
    Args:
        employees: List of processed employees
        all_fields: List of all fields found
        output_files: List of generated output files
    """
    print("\n" + "="*60)
    print("EMPLOYEE EVALUATION REPORT SUMMARY")
    print("="*60)
    print(f"Total Employees Processed: {len(employees)}")
    print(f"Total Fields Found: {len(all_fields)}")
    print(f"Fields: {', '.join(all_fields)}")
    print(f"Output Files Generated: {len(output_files)}")
    
    for filepath in output_files:
        file_info = get_file_info(filepath)
        if file_info:
            print(f"  - {os.path.basename(filepath)} ({file_info['size_formatted']})")
    
    print("="*60)
