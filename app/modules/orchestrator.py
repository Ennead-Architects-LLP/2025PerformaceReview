"""
Orchestrator Module

This module handles the main workflow orchestration for the Employee Evaluation system.
All business logic and workflow coordination is handled here.
"""

import os
import sys
from typing import List, Dict, Tuple

# Import from modules package
from .html_generator import create_html_output_from_employees
from .excel_parser import parse_excel_to_employees
from .utils import log_info, log_error, log_warning, ensure_output_directory
from .config import Config


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
        """Check and log Excel data source availability."""
        excel_path = Config.get_excel_input_path()
        log_info(f"Excel data source path: {excel_path}")
        
        if os.path.exists(excel_path):
            log_info("Excel data source is available")
        else:
            log_error(f"Excel data source not found at: {excel_path}")
            raise FileNotFoundError(f"Excel file not found: {excel_path}")
    
    def _setup_output_directory(self) -> None:
        """Setup output directory."""
        output_dir = ensure_output_directory()
        log_info(f"Output directory: {output_dir}")
    
    def _parse_data(self) -> None:
        """Parse Excel data to Employee objects."""
        log_info("Parsing Excel data...")

        # Parse Excel to Employee objects
        excel_path = Config.get_excel_input_path()

        self.employees = parse_excel_to_employees(excel_path)
        if not self.employees:
            raise ValueError("Failed to parse Excel data!")

        log_info(f"Successfully parsed {len(self.employees)} employee records from Excel")

        # Optionally save to JSON for debugging/reference
        self._save_employee_data_json()

    def _save_employee_data_json(self) -> None:
        """Save employee data to JSON for reference (optional)."""
        try:
            json_path = Config.get_json_output_path()
            data_dir = Config.get_data_dir_path()
            Config.ensure_directory_exists(data_dir)

            # Convert employees to dicts and save
            employee_dicts = [emp.to_dict() for emp in self.employees]

            import json
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(employee_dicts, f, indent=2, ensure_ascii=False)

            log_info(f"Saved employee data to: {json_path}")
        except Exception as e:
            log_warning(f"Failed to save employee data JSON: {e}")

    def _generate_reports(self) -> None:
        """Generate HTML website from Employee objects."""
        log_info("Generating HTML website...")

        website_path = Config.get_website_output_path()

        success = create_html_output_from_employees(self.employees, website_path)
        if success:
            self.output_files.append(website_path)
            log_info(f"Successfully generated website at: {website_path}")
        else:
            raise ValueError("Failed to generate HTML website!")
    
    def _print_summary(self) -> None:
        """Print processing summary."""
        log_info(f"Generated {len(self.output_files)} output files:")
        for file_path in self.output_files:
            log_info(f"  - {file_path}")
    
    def _log_completion(self) -> None:
        """Log completion message."""
        log_info("Report generation completed successfully!")


# Removed generate_reports_with_custom_paths - no longer needed for txt processing


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
        # Check if Excel data source is available
        excel_path = Config.get_excel_input_path()
        if not os.path.exists(excel_path):
            log_warning(f"Excel data source not available: {excel_path}")
            return False
        
        # Check if required modules can be imported
        required_modules = [
            'app.modules.excel_parser', 'app.modules.html_generator', 
            'app.modules.utils', 'app.modules.config', 'app.modules.employee'
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
