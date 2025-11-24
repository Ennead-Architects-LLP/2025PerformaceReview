@echo off
setlocal ENABLEDELAYEDEXPANSION

REM ============================================================
REM Build script for Evaluator-Employee PDF Maker
REM This is a SEPARATE app from the Employee Self-Evaluation Report Generator
REM - Entry point: evaluator_employee_pdf_maker.py
REM - Old app entry point: employee_self_evaluation_app.py (formerly main.py)
REM - Output EXE: evaluator-employee-pdf-maker.exe
REM - Old app EXE: "2025 Ennead Performance Report.exe"
REM ============================================================

cd /d %~dp0

set OUTPUT_DIR=OUTPUT
set APP_NAME=evaluator-employee-pdf-maker
set ICON_SRC=assets\icons\ennead_architects_logo.ico
set ICON_PATH=assets\icons\app_icon_multi.ico

REM Prefer venv python
set PY=%CD%\.venv\Scripts\python.exe
if not exist "%PY%" set PY=python

"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install -r requirements.txt
"%PY%" -m pip install pyinstaller

REM Generate multi-size ICO to ensure consistent icon in all Explorer views
"%PY%" scripts\generate_icon.py "%ICON_SRC%" "%ICON_PATH%"

REM Clean build artifacts to avoid conflicts with other app builds
if exist build rmdir /S /Q build
if exist dist rmdir /S /Q dist
REM Also clean any spec file from this app to avoid conflicts
if exist "%APP_NAME%.spec" del /Q "%APP_NAME%.spec"

REM Build the EXE with unique name to avoid conflicts
"%PY%" -m PyInstaller ^
  --noconfirm ^
  --name "%APP_NAME%" ^
  --windowed ^
  --onefile ^
  --icon "%ICON_PATH%" ^
  --add-data "assets;assets" ^
  --hidden-import app.modules ^
  --clean ^
  evaluator_employee_pdf_maker.py

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if exist "dist\%APP_NAME%.exe" copy /Y "dist\%APP_NAME%.exe" "%OUTPUT_DIR%\%APP_NAME%.exe" >nul

echo Built: %OUTPUT_DIR%\%APP_NAME%.exe

REM Run the exe
"%OUTPUT_DIR%\%APP_NAME%.exe"

endlocal

