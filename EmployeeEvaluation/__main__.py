"""
Employee Evaluation Report Generator - Main Entry Point

This is the main entry point for the Employee Evaluation system.
All business logic is handled by external modules to keep this script lean.
"""

import sys
import os

# Add lib directory to path for imports
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib')
sys.path.insert(0, lib_path)

# Import from lib folder
from orchestrator import EmployeeEvaluationOrchestrator


def main():
    """
    Main entry point for the Employee Evaluation system.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    orchestrator = EmployeeEvaluationOrchestrator()
    return orchestrator.run()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)