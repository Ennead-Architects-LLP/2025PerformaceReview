"""
Command Line Interface Module

This module provides command-line interface functionality for the Employee Evaluation system.
"""

import argparse
import sys
from typing import List, Optional

from orchestrator import (
    EmployeeEvaluationOrchestrator, 
    generate_reports_with_custom_paths,
    validate_system
)
from utils import log_info, log_error


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Employee Evaluation Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Generate reports with default settings
  python main.py --validate         # Validate system configuration
  python main.py --input /path/to/data --output /path/to/output
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Input directory containing survey response files'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output directory for generated reports'
    )
    
    parser.add_argument(
        '--validate', '-v',
        action='store_true',
        help='Validate system configuration and exit'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Employee Evaluation System v1.0.0'
    )
    
    return parser


def run_cli(args: List[str] = None) -> int:
    """
    Run the command-line interface.
    
    Args:
        args: Command line arguments (defaults to sys.argv)
        
    Returns:
        int: Exit code
    """
    parser = create_argument_parser()
    parsed_args = parser.parse_args(args)
    
    try:
        # Handle validation mode
        if parsed_args.validate:
            log_info("Validating system configuration...")
            if validate_system():
                log_info("System validation passed")
                return 0
            else:
                log_error("System validation failed")
                return 1
        
        # Handle custom paths
        if parsed_args.input or parsed_args.output:
            log_info("Generating reports with custom paths...")
            success = generate_reports_with_custom_paths(
                input_dir=parsed_args.input,
                output_dir=parsed_args.output
            )
            return 0 if success else 1
        
        # Default mode - use orchestrator
        orchestrator = EmployeeEvaluationOrchestrator()
        return orchestrator.run()
        
    except KeyboardInterrupt:
        log_info("Operation cancelled by user")
        return 130
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        return 1


def main():
    """Main CLI entry point."""
    return run_cli()


if __name__ == "__main__":
    sys.exit(main())
