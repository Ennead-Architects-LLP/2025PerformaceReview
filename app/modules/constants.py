"""
Constants and Configuration

This module contains constant values and configuration settings for the Employee Evaluation system.
"""

import os

# Constants moved to config.py for centralization
# This file is kept for backward compatibility but most constants are now in Config class

BACKGROUND_IMAGE_URL = "https://image-cdn.hypb.st/https%3A%2F%2Fhypebeast.com%2Fimage%2F2021%2F08%2Fshanghai-astronomy-museum-ennead-architects-china-6.jpg?q=75&w=800&cbr=1&fit=max"

COMPANY_NAME = "EnneadTab"
COPYRIGHT_YEAR = "2025"
SYSTEM_NAME = "Employee Evaluation Report System"

DEFAULT_ENCODING = "utf-8"
DEFAULT_TIMEOUT = 30

# Removed get_data_source_path and is_data_source_available - no longer needed for txt processing

def get_background_image_url():
    return BACKGROUND_IMAGE_URL
