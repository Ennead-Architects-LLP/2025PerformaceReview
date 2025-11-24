"""
Command Line Interface Module
"""

import argparse
import sys
from typing import List

from .orchestrator import (
    EmployeeEvaluationOrchestrator, 
    validate_system
)
from .excel_parser import parse_excel_to_json
from .html_generator import create_html_output_from_employees
from .config import Config
from .utils import log_info, log_error


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Employee Evaluation Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python employee_self_evaluation_app.py   # Generate complete pipeline (Excel to website)
  python employee_self_evaluation_app.py --validate                # Validate system configuration
  python employee_self_evaluation_app.py --parse-excel             # Parse Excel file to JSON only
  python employee_self_evaluation_app.py --generate-website        # Generate HTML website from JSON data
        """
    )
    parser.add_argument('--validate', '-v', action='store_true', help='Validate system configuration and exit')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--parse-excel', action='store_true', help='Parse Excel file to JSON format')
    parser.add_argument('--generate-website', action='store_true', help='Generate HTML website from parsed JSON data')
    parser.add_argument('--no-images', action='store_true', help='Skip copying employee profile images (used with --parse-excel)')
    parser.add_argument('--copy-external-images', action='store_true', help='Copy images from external EmployeeData repository')
    parser.add_argument('--external-repo-path', type=str, help='Path to external EmployeeData repository')
    parser.add_argument('--force-copy-images', action='store_true', help='Force overwrite existing images when copying from external repo')
    parser.add_argument('--version', action='version', version='Employee Evaluation System v1.0.0')
    return parser


def run_cli(args: List[str] = None) -> int:
    parser = create_argument_parser()
    parsed_args = parser.parse_args(args)
    try:
        if parsed_args.parse_excel:
            log_info("Parsing Excel file to JSON...")
            excel_file = Config.get_excel_input_path()
            json_output = Config.get_json_output_path()
            copy_images = not parsed_args.no_images
            image_source = Config.get_image_source_path()
            
            success = parse_excel_to_json(excel_file, json_output, copy_images, image_source)
            if success:
                log_info(f"Successfully parsed Excel file to {json_output}")
                if copy_images:
                    log_info("Employee profile images processed and copied")
                return 0
            else:
                log_error("Failed to parse Excel file")
                return 1
                
        if parsed_args.generate_website:
            log_info("Generating HTML website...")
            json_file = Config.get_json_output_path()
            website_output = Config.get_website_output_path()
            
            success = create_html_output_from_json(json_file, website_output)
            if success:
                log_info(f"Successfully generated website in {website_output}")
                return 0
            else:
                log_error("Failed to generate website")
                return 1
                
        if parsed_args.copy_external_images:
            log_info("Copying images from external EmployeeData repository...")
            from .external_repo_manager import copy_images_from_employee_data_repo
            
            external_repo_path = parsed_args.external_repo_path or Config.get_external_employee_data_repo_path()
            if not external_repo_path:
                log_error("No external repository path provided. Use --external-repo-path or configure in config.py")
                return 1
            
            success = copy_images_from_employee_data_repo(external_repo_path, parsed_args.force_copy_images)
            if success:
                log_info("Successfully copied images from external repository")
                return 0
            else:
                log_error("Failed to copy images from external repository")
                return 1
                
        if parsed_args.validate:
            log_info("Validating system configuration...")
            if validate_system():
                log_info("System validation passed")
                return 0
            else:
                log_error("System validation failed")
                return 1
        # Default behavior: run complete pipeline (Excel to website)
        log_info("Running complete pipeline: Excel parsing to website generation...")
        orchestrator = EmployeeEvaluationOrchestrator()
        return orchestrator.run()
    except KeyboardInterrupt:
        log_info("Operation cancelled by user")
        return 130
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        return 1


def main():
    return run_cli()


if __name__ == "__main__":
    sys.exit(main())
