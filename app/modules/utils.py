"""
Utility Functions

Helper functions and utilities for the Employee Evaluation system.
"""

import os
import sys
from typing import List, Dict, Any
from datetime import datetime

VERBOSE = os.environ.get("EE_VERBOSE", "0") in ("1", "true", "True")

def set_verbose(enabled: bool) -> None:
    global VERBOSE
    VERBOSE = bool(enabled)


def get_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ensure_output_directory(output_dir: str = None) -> str:
    if output_dir is None:
        output_dir = get_project_root()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"


# Removed validate_input_files - no longer needed for txt processing


def log_debug(message: str) -> None:
    if VERBOSE:
        timestamp = get_timestamp()
        print(f"[{timestamp}] DEBUG: {message}")


def log_info(message: str) -> None:
    timestamp = get_timestamp()
    print(f"[{timestamp}] INFO: {message}")


def log_error(message: str) -> None:
    timestamp = get_timestamp()
    print(f"[{timestamp}] ERROR: {message}", file=sys.stderr)


def log_warning(message: str) -> None:
    timestamp = get_timestamp()
    print(f"[{timestamp}] WARNING: {message}")


def safe_filename(filename: str) -> str:
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def get_file_info(filepath: str) -> Dict[str, Any]:
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
