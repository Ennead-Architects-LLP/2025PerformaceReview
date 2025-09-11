"""
Employee Evaluation System

A modular system for processing employee evaluation data from text files
and generating both Excel and interactive HTML reports.

Modules:
    - parser: Handles parsing of survey response files
    - excel_generator: Creates Excel reports
    - html_generator: Creates interactive HTML reports
    - utils: Utility functions and helpers
    - config: Configuration settings
    - constants: Constants and configuration values
    - orchestrator: Main workflow orchestration
    - factory: Report creation factory
    - cli: Command-line interface
    - main: Main entry point
"""

__version__ = "1.0.0"
__author__ = "EnneadTab"
__description__ = "A system for processing employee evaluation data and generating reports"

from .parser import parse_input_files, parse_single_file, validate_employee_data
from .excel_generator import create_excel_output, create_summary_statistics
from .html_generator import create_html_output, prepare_chart_data
from .utils import log_info, log_error, print_summary
from .config import Config
from .constants import get_data_source_path, is_data_source_available
from .orchestrator import EmployeeEvaluationOrchestrator
from .factory import ReportFactory, create_custom_report, get_supported_formats

__all__ = [
    'parse_input_files',
    'parse_single_file', 
    'validate_employee_data',
    'create_excel_output',
    'create_summary_statistics',
    'create_html_output',
    'prepare_chart_data',
    'log_info',
    'log_error',
    'print_summary',
    'Config',
    'get_data_source_path',
    'is_data_source_available',
    'EmployeeEvaluationOrchestrator',
    'ReportFactory',
    'create_custom_report',
    'get_supported_formats'
]
