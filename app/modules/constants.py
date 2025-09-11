"""
Constants and Configuration

This module contains constant values and configuration settings for the Employee Evaluation system.
"""

import os

DATA_SOURCE_PATH = r"C:\Users\szhang\OneDrive - Ennead Architects\Human Resources - 2025 Self-Evaluation Forms - Survey.Responses"
BACKGROUND_IMAGE_URL = "https://image-cdn.hypb.st/https%3A%2F%2Fhypebeast.com%2Fimage%2F2021%2F08%2Fshanghai-astronomy-museum-ennead-architects-china-6.jpg?q=75&w=800&cbr=1&fit=max"
INPUT_FILE_PATTERN = "INPUT*.txt"
OUTPUT_HTML_FILENAME = "OUTPUT.html"
OUTPUT_EXCEL_FILENAME = "OUTPUT.xlsx"
OUTPUT_CSV_FILENAME = "OUTPUT.csv"

COMPANY_NAME = "EnneadTab"
COPYRIGHT_YEAR = "2025"
SYSTEM_NAME = "Employee Evaluation Report System"

DEFAULT_ENCODING = "utf-8"
DEFAULT_TIMEOUT = 30

REQUIRED_FIELDS = ['name']
EXCLUDED_FIELDS = ['name', 'time']

MAX_CONTAINER_WIDTH = "1400px"
CARD_MIN_WIDTH = "400px"
CHART_MIN_WIDTH = "350px"

COLORS = {
    'primary': '#2B7A78',
    'secondary': '#1A5A58',
    'dark': '#0F1419',
    'light': '#F0F8F7',
    'white': '#FFFFFF',
    'accent': '#3AAFA9',
    'text_primary': '#1A1A1A',
    'text_secondary': '#4A4A4A',
    'border': '#E0E8E7'
}

def get_data_source_path():
    return DATA_SOURCE_PATH


def get_background_image_url():
    return BACKGROUND_IMAGE_URL


def is_data_source_available():
    return os.path.exists(DATA_SOURCE_PATH)
