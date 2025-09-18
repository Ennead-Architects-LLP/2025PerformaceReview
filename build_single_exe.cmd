@echo off
setlocal ENABLEDELAYEDEXPANSION

cd /d %~dp0

set OUTPUT_DIR=OUTPUT
set APP_NAME=2025 Ennead Performance Report
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

if exist build rmdir /S /Q build
if exist dist rmdir /S /Q dist

"%PY%" -m PyInstaller ^
  --noconfirm ^
  --name "%APP_NAME%" ^
  --windowed ^
  --onefile ^
  --icon "%ICON_PATH%" ^
  --add-data "assets;assets" ^
  --add-data "docs;docs" ^
  --hidden-import app.modules ^
  main.py

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if exist "dist\%APP_NAME%.exe" copy /Y "dist\%APP_NAME%.exe" "%OUTPUT_DIR%\%APP_NAME%.exe" >nul

echo Built: %OUTPUT_DIR%\%APP_NAME%.exe

REM Run the exe
"%OUTPUT_DIR%\%APP_NAME%.exe"

endlocal
