# Employee Evaluation Report System

A pipeline to parse employee evaluation data from Excel files and generate professional HTML websites with employee data cards and profile images.

## Features
- Parse Excel files containing employee evaluation data
- Generate interactive HTML website with employee cards
- Copy and match employee profile images with fuzzy matching
- Centralized configuration and consistent output naming
- Simple root entry (`main.py`) and optional CLI

## Project Structure
```
app/
  modules/
    orchestrator.py
    excel_parser.py
    html_generator.py
    employee.py
    image_manager.py
    cli.py
    config.py
    constants.py
    utils.py

main.py                 # Root entrypoint
assets/
  data/                 # Excel input and JSON output
  images/               # Employee profile images
website/                # Generated HTML website
```

## Requirements
- Python 3.9+
- pip packages: `pandas`, `openpyxl`, `fuzzywuzzy`, `python-levenshtein`

Install:
```bash
pip install -r requirements.txt
```

## Usage
Run from the repo root:
```bash
python main.py
```

Optional CLI commands:
```bash
python main.py --parse-excel          # Parse Excel to JSON only
python main.py --generate-website     # Generate website from JSON only
python main.py --validate             # Validate system configuration
python main.py --no-images            # Skip copying profile images
```

Enable verbose logs:
```bash
# Windows PowerShell
env:EE_VERBOSE=1; python main.py
```

## Inputs
Place your Excel file at: `assets/data/Employee Self-Evaluation Data Export From MS Form.xlsx`

## Outputs
- JSON data: `assets/data/employee_data.json`
- Website: `website/` directory
- Images: `assets/images/` directory

## Notes
- Internal imports are package-relative for reliability.
- Output naming and paths are controlled by `app/modules/config.py`.