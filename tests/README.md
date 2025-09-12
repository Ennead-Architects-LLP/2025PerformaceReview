# Test and Debug Scripts

This directory contains various test and debug scripts used during development of the Performance Review application.

## Directory Structure

### `debug/`
Contains debugging scripts for troubleshooting specific issues:

- **`debug_html.py`** - Debug HTML card generation and structure
- **`debug_mapping.py`** - Debug header mapping conflicts and issues
- **`detailed_check.py`** - Detailed analysis of HTML card content
- **`examine_html.py`** - Examine HTML file structure and content
- **`html_content_check.py`** - Check HTML content positioning and structure

### `scripts/`
Contains utility scripts for checking and validating various components:

- **`check_excel.py`** - Inspect Excel file columns and data
- **`check_headers.py`** - Validate header mapping functionality
- **`check_html.py`** - Basic HTML card structure validation
- **`check_html2.py`** - Advanced HTML structure analysis
- **`check_mappings.py`** - Check for header mapping conflicts
- **`final_check.py`** - Final validation of HTML generation

### `html/`
Contains HTML test files:

- **`test_cards.html`** - Test HTML card structure for development

## Usage

These scripts are primarily for development and debugging purposes. They can be run individually to test specific functionality or troubleshoot issues.

Most scripts expect to be run from the project root directory and may reference files in the `assets/` and `docs/` directories.

## Notes

- Some scripts may have hardcoded paths that assume they're run from the project root
- These scripts are not part of the main application and can be safely removed if no longer needed
- Consider updating import paths if moving these scripts to different locations
