"""
Command Line Interface Module
"""

import argparse
import sys
from typing import List

from .orchestrator import (
    EmployeeEvaluationOrchestrator, 
    generate_reports_with_custom_paths,
    validate_system
)
from .excel_parser import parse_excel_to_json
from .html_generator import create_html_output_from_json
from .config import Config
from .utils import log_info, log_error


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Employee Evaluation Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Generate reports with default settings
  python main.py --validate                # Validate system configuration
  python main.py --input /path/to/data --output /path/to/output
  python main.py --parse-excel             # Parse Excel file to JSON (default paths)
  python main.py --parse-excel --excel-file custom.xlsx --json-output output.json
  python main.py --generate-website        # Generate HTML website from JSON data
  python main.py --generate-website --website-output custom-site
        """
    )
    parser.add_argument('--input', '-i', type=str, help='Input directory containing survey response files')
    parser.add_argument('--output', '-o', type=str, help='Output directory for generated reports')
    parser.add_argument('--validate', '-v', action='store_true', help='Validate system configuration and exit')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--parse-excel', action='store_true', help='Parse Excel file to JSON format')
    parser.add_argument('--excel-file', type=str, help='Path to Excel file to parse (used with --parse-excel)')
    parser.add_argument('--json-output', type=str, help='Path for JSON output file (used with --parse-excel)')
    parser.add_argument('--no-images', action='store_true', help='Skip copying employee profile images (used with --parse-excel)')
    parser.add_argument('--image-source', type=str, help='Source directory for employee images (used with --parse-excel)')
    parser.add_argument('--generate-website', action='store_true', help='Generate HTML website from parsed JSON data')
    parser.add_argument('--website-output', type=str, help='Output directory for website (used with --generate-website)')
    parser.add_argument('--version', action='version', version='Employee Evaluation System v1.0.0')
    return parser


def run_cli(args: List[str] = None) -> int:
    parser = create_argument_parser()
    parsed_args = parser.parse_args(args)
    try:
        if parsed_args.parse_excel:
            log_info("Parsing Excel file to JSON...")
            excel_file = parsed_args.excel_file or Config.get_excel_input_path()
            json_output = parsed_args.json_output or Config.get_json_output_path()
            copy_images = not parsed_args.no_images
            
            # Set default image source if not provided
            if copy_images and not parsed_args.image_source:
                image_source = Config.get_image_source_path()
            else:
                image_source = parsed_args.image_source
            
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
            json_file = parsed_args.json_output or Config.get_json_output_path()
            website_output = parsed_args.website_output or Config.get_website_output_path()
            
            success = create_html_output_from_json(json_file, website_output)
            if success:
                log_info(f"Successfully generated website in {website_output}")
                return 0
            else:
                log_error("Failed to generate website")
                return 1
                
        if parsed_args.validate:
            log_info("Validating system configuration...")
            if validate_system():
                log_info("System validation passed")
                return 0
            else:
                log_error("System validation failed")
                return 1
        if parsed_args.input or parsed_args.output:
            log_info("Generating reports with custom paths...")
            success = generate_reports_with_custom_paths(input_dir=parsed_args.input, output_dir=parsed_args.output)
            return 0 if success else 1
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
