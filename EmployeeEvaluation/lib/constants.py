"""
Constants and Configuration

This module contains constant values and configuration settings for the Employee Evaluation system.
"""

import os

# Data source path
DATA_SOURCE_PATH = r"C:\Users\szhang\OneDrive - Ennead Architects\Human Resources - 2025 Self-Evaluation Forms - Survey.Responses"

# Background image URL
BACKGROUND_IMAGE_URL = "https://image-cdn.hypb.st/https%3A%2F%2Fhypebeast.com%2Fimage%2F2021%2F08%2Fshanghai-astronomy-museum-ennead-architects-china-6.jpg?q=75&w=800&cbr=1&fit=max"

# File patterns
INPUT_FILE_PATTERN = "INPUT*.txt"
OUTPUT_HTML_FILENAME = "OUTPUT.html"
OUTPUT_EXCEL_FILENAME = "OUTPUT.xlsx"
OUTPUT_CSV_FILENAME = "OUTPUT.csv"

# Company information
COMPANY_NAME = "EnneadTab"
COPYRIGHT_YEAR = "2025"
SYSTEM_NAME = "Employee Evaluation Report System"

# Default settings
DEFAULT_ENCODING = "utf-8"
DEFAULT_TIMEOUT = 30

# Validation settings
REQUIRED_FIELDS = ['name']
EXCLUDED_FIELDS = ['name', 'time']

# UI Settings
MAX_CONTAINER_WIDTH = "1400px"
CARD_MIN_WIDTH = "400px"
CHART_MIN_WIDTH = "350px"

# Color scheme (improved teal palette for better readability)
COLORS = {
    'primary': '#2B7A78',      # Darker teal for better contrast
    'secondary': '#1A5A58',    # Even darker for secondary elements
    'dark': '#0F1419',         # Darker text for better readability
    'light': '#F0F8F7',        # Lighter background for better contrast
    'white': '#FFFFFF',        # Pure white
    'accent': '#3AAFA9',       # Original teal as accent
    'text_primary': '#1A1A1A', # High contrast text
    'text_secondary': '#4A4A4A', # Secondary text
    'border': '#E0E8E7'        # Subtle border color
}

def get_data_source_path():
    """
    Get the configured data source path.
    
    Returns:
        str: The data source path
    """
    return DATA_SOURCE_PATH

def get_background_image_url():
    """
    Get the background image URL.
    
    Returns:
        str: The background image URL
    """
    return BACKGROUND_IMAGE_URL

def is_data_source_available():
    """
    Check if the data source path exists and is accessible.
    
    Returns:
        bool: True if data source is available, False otherwise
    """
    return os.path.exists(DATA_SOURCE_PATH)
