# Employee Evaluation Report System

A simple pipeline to parse employee evaluation inputs and generate professional HTML and Excel reports. Outputs are published-ready artifacts in the `docs/` directory.

## Features
- Parse `INPUT*.txt` response files
- Generate interactive HTML dashboard with charts
- Generate formatted Excel workbook
- Centralized configuration and consistent output naming
- Simple root entry (`main.py`) and optional CLI

## Project Structure
```
app/
  modules/
    orchestrator.py
    parser.py
    html_generator.py
    excel_generator.py
    cli.py
    config.py
    constants.py
    utils.py

main.py                 # Root entrypoint
```

## Requirements
- Python 3.9+
- pip packages: `pandas`, `openpyxl`, `chardet`

Install:
```bash
pip install -r requirements.txt
```

If you do not have a `requirements.txt` yet, install manually:
```bash
pip install pandas openpyxl chardet
```

## Usage
Run from the repo root:
```bash
python main.py
```

Optional CLI entry:
```bash
python -c "from app.modules.cli import main; import sys; sys.exit(main())" -- --validate
python -c "from app.modules.cli import main; import sys; sys.exit(main())" -- --input ./data --output ./out
```

Enable verbose logs:
```bash
# Windows PowerShell
env:EE_VERBOSE=1; python main.py
```

## Inputs
Place `INPUT*.txt` files in the project root (or use `--input PATH`).

## Outputs
Artifacts are written to `docs/` for easy GitHub Pages hosting:
- HTML: `docs/_EvaluationSummary.html`
- Excel: `docs/_EvaluationSummary.xlsx`

The HTML includes a “Download Excel” button that references the matching Excel artifact in `docs/`.

## Notes
- Internal imports are package-relative for reliability.
- Output naming and paths are controlled by `app/modules/config.py`.