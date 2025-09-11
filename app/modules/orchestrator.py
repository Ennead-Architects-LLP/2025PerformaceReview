"""
Orchestrator Module

This module handles the main workflow orchestration for the Employee Evaluation system.
All business logic and workflow coordination is handled here.
"""

import os
import sys
from typing import List, Dict, Tuple

# Import from modules package
from .parser import parse_input_files
from .excel_generator import create_excel_output
from .html_generator import create_html_output
from .utils import log_info, log_error, log_warning, print_summary, ensure_output_directory
from .config import Config
from .constants import get_data_source_path, is_data_source_available


class EmployeeEvaluationOrchestrator:
    """Main orchestrator class for the Employee Evaluation system."""
    
    def __init__(self):
        self.employees = []
        self.all_fields = []
        self.output_files = []
    
    def run(self) -> int:
        """
        Main execution method.
        
        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        try:
            self._log_startup()
            self._check_data_source()
            self._setup_output_directory()
            self._parse_data()
            self._generate_reports()
            self._print_summary()
            self._log_completion()
            return 0
            
        except Exception as e:
            log_error(f"An error occurred: {str(e)}")
            return 1
    
    def _log_startup(self) -> None:
        """Log startup information."""
        log_info("Starting Employee Evaluation Report Generation...")
    
    def _check_data_source(self) -> None:
        """Check and log data source availability."""
        data_source = get_data_source_path()
        log_info(f"Data source path: {data_source}")
        
        if is_data_source_available():
            log_info("Data source is available")
        else:
            log_warning("Data source path not found - using local INPUT files")
    
    def _setup_output_directory(self) -> None:
        """Setup output directory."""
        output_dir = ensure_output_directory()
        log_info(f"Output directory: {output_dir}")
    
    def _parse_data(self) -> None:
        """Parse input data."""
        log_info("Parsing input files...")
        self.employees, self.all_fields = parse_input_files()
        
        if not self.employees:
            raise ValueError("No employee data found! Please check your input files.")
        
        log_info(f"Found {len(self.employees)} employees with fields: {self.all_fields}")
    
    def _generate_reports(self) -> None:
        """Generate Excel and HTML reports."""
        # Generate Excel output
        log_info("Generating Excel report...")
        excel_path = create_excel_output(
            self.employees, 
            self.all_fields, 
            Config.OUTPUT_EXCEL_FILENAME
        )
        self.output_files.append(excel_path)
        
        # Generate HTML output
        log_info("Generating HTML report...")
        html_path = create_html_output(
            self.employees, 
            self.all_fields, 
            Config.OUTPUT_HTML_FILENAME
        )
        self.output_files.append(html_path)
    
    def _print_summary(self) -> None:
        """Print processing summary."""
        print_summary(self.employees, self.all_fields, self.output_files)
    
    def _log_completion(self) -> None:
        """Log completion message."""
        log_info("Report generation completed successfully!")


def generate_reports_with_custom_paths(input_dir: str = None, output_dir: str = None) -> bool:
    """
    Generate reports with custom input and output directories.
    
    Args:
        input_dir: Directory containing input files
        output_dir: Directory for output files
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Change to input directory if specified
        if input_dir:
            original_dir = os.getcwd()
            os.chdir(input_dir)
        
        # Ensure output directory exists
        if output_dir:
            ensure_output_directory(output_dir)
        
        # Parse and generate reports
        employees, all_fields = parse_input_files()
        
        if not employees:
            log_error("No employee data found!")
            return False
        
        # Generate outputs
        create_excel_output(employees, all_fields)
        create_html_output(employees, all_fields)
        
        # Restore original directory
        if input_dir:
            os.chdir(original_dir)
        
        return True
        
    except Exception as e:
        log_error(f"Error generating reports: {str(e)}")
        return False


def run_batch_processing(file_paths: List[str]) -> Dict[str, any]:
    """
    Process multiple files in batch.
    
    Args:
        file_paths: List of file paths to process
        
    Returns:
        Dictionary with processing results
    """
    results = {
        'success': 0,
        'failed': 0,
        'errors': []
    }
    
    for file_path in file_paths:
        try:
            # Process individual file
            # This would need to be implemented based on requirements
            results['success'] += 1
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"{file_path}: {str(e)}")
    
    return results


def validate_system() -> bool:
    """
    Validate that the system is properly configured.
    
    Returns:
        True if system is valid, False otherwise
    """
    try:
        # Check if data source is available
        if not is_data_source_available():
            log_warning("Data source not available")
            return False
        
        # Check if required modules can be imported
        required_modules = [
            'parser', 'excel_generator', 'html_generator', 
            'utils', 'config', 'constants'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError as e:
                log_error(f"Required module {module} not available: {e}")
                return False
        
        log_info("System validation passed")
        return True
        
    except Exception as e:
        log_error(f"System validation failed: {e}")
        return False
