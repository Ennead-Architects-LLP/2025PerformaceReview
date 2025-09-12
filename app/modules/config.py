"""
Configuration Settings

This module contains configuration settings for the Employee Evaluation system.
"""

import os
from typing import Dict, Any


class Config:
    """Configuration class for Employee Evaluation system."""
    
    # Legacy file patterns (kept for backward compatibility)
    OUTPUT_HTML_FILENAME = "OUTPUT.html"
    OUTPUT_EXCEL_FILENAME = "OUTPUT.xlsx"
    OUTPUT_CSV_FILENAME = "OUTPUT.csv"

    # Project structure
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DOCS_DIR_NAME = "docs"
    OUTPUT_BASE_NAME = "_EvaluationSummary"
    
    # Excel parsing paths
    EXCEL_INPUT_FILE = "assets/data/Employee Self-Evaluation Data Export From MS Form.xlsx"
    JSON_OUTPUT_FILE = "assets/data/employee_data.json"
    IMAGE_MAPPINGS_FILE = "assets/data/image_mappings.json"
    
    # Image processing paths - cross-platform compatible
    IMAGE_SOURCE_DIR = os.path.join(os.path.expanduser("~"), "github", "EmployeeData", "assets", "images")
    IMAGE_TARGET_DIR = "assets/images"
    
    # Website generation paths
    WEBSITE_OUTPUT_DIR = "docs"
    WEBSITE_CSS_DIR = "docs/css"
    WEBSITE_JS_DIR = "docs/js"
    WEBSITE_ASSETS_DIR = "docs/assets"
    WEBSITE_IMAGES_DIR = "docs/assets/images"
    
    # Data directories
    DATA_DIR = "assets/data"
    ASSETS_DIR = "assets"
    
    # Default file names and paths
    DEFAULT_AVATAR_PATH = "assets/images/default-avatar.png"
    DEFAULT_JSON_OUTPUT = "employee_data.json"
    DEFAULT_IMAGE_MAPPINGS = "data/image_mappings.json"
    
    # File extensions and patterns
    SUPPORTED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
    EXCEL_FILE_EXTENSION = ".xlsx"
    JSON_FILE_EXTENSION = ".json"
    
    # Company and system information
    COMPANY_NAME = "EnneadTab"
    COPYRIGHT_YEAR = "2025"
    SYSTEM_NAME = "Employee Evaluation Report System"
    
    # Background and external URLs
    BACKGROUND_IMAGE_URL = "https://image-cdn.hypb.st/https%3A%2F%2Fhypebeast.com%2Fimage%2F2021%2F08%2Fshanghai-astronomy-museum-ennead-architects-china-6.jpg?q=75&w=800&cbr=1&fit=max"
    
    HTML_TITLE = "Employee Evaluation Report"
    CHART_TYPE = "doughnut"
    CHART_HEIGHT = 300
    
    COLORS = {
        'primary': '#667eea',
        'secondary': '#764ba2',
        'success': '#16b981',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'info': '#3b82f6',
        'purple': '#8b5cf6',
        'pink': '#ec4899'
    }
    
    CHART_COLORS = [
        'rgba(102, 126, 234, 0.8)',
        'rgba(118, 75, 162, 0.8)',
        'rgba(59, 130, 246, 0.8)',
        'rgba(16, 185, 129, 0.8)',
        'rgba(245, 158, 11, 0.8)',
        'rgba(239, 68, 68, 0.8)',
        'rgba(139, 92, 246, 0.8)',
        'rgba(236, 72, 153, 0.8)'
    ]
    
    CHART_BORDER_COLORS = [
        'rgba(102, 126, 234, 1)',
        'rgba(118, 75, 162, 1)',
        'rgba(59, 130, 246, 1)',
        'rgba(16, 185, 129, 1)',
        'rgba(245, 158, 11, 1)',
        'rgba(239, 68, 68, 1)',
        'rgba(139, 92, 246, 1)',
        'rgba(236, 72, 153, 1)'
    ]
    
    FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    FONT_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    
    MAX_CONTAINER_WIDTH = "1400px"
    CARD_MIN_WIDTH = "400px"
    CHART_MIN_WIDTH = "350px"
    
    ANIMATION_DURATION = 1000
    ANIMATION_EASING = "easeOutQuart"
    
    # Removed REQUIRED_FIELDS and EXCLUDED_FIELDS - no longer needed for Excel parsing
    
    @classmethod
    def get_output_path(cls, filename: str) -> str:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    @classmethod
    def get_docs_dir(cls) -> str:
        return os.path.join(cls.PROJECT_ROOT, cls.DOCS_DIR_NAME)

    @classmethod
    def get_docs_output_path(cls, extension_without_dot: str) -> str:
        return os.path.join(cls.get_docs_dir(), f"{cls.OUTPUT_BASE_NAME}.{extension_without_dot}")
    
    @classmethod
    def get_chart_config(cls) -> Dict[str, Any]:
        return {
            'type': cls.CHART_TYPE,
            'height': cls.CHART_HEIGHT,
            'colors': cls.CHART_COLORS,
            'border_colors': cls.CHART_BORDER_COLORS,
            'animation_duration': cls.ANIMATION_DURATION,
            'animation_easing': cls.ANIMATION_EASING
        }
    
    @classmethod
    def get_html_config(cls) -> Dict[str, Any]:
        return {
            'title': cls.HTML_TITLE,
            'font_family': cls.FONT_FAMILY,
            'font_url': cls.FONT_URL,
            'max_width': cls.MAX_CONTAINER_WIDTH,
            'card_min_width': cls.CARD_MIN_WIDTH,
            'chart_min_width': cls.CHART_MIN_WIDTH,
            'colors': cls.COLORS
        }
    
    @classmethod
    def get_excel_input_path(cls) -> str:
        """Get the Excel input file path."""
        return os.path.join(cls.PROJECT_ROOT, cls.EXCEL_INPUT_FILE)
    
    @classmethod
    def get_json_output_path(cls) -> str:
        """Get the JSON output file path."""
        return os.path.join(cls.PROJECT_ROOT, cls.JSON_OUTPUT_FILE)
    
    @classmethod
    def get_image_mappings_path(cls) -> str:
        """Get the image mappings file path."""
        return os.path.join(cls.PROJECT_ROOT, cls.IMAGE_MAPPINGS_FILE)
    
    @classmethod
    def get_image_source_path(cls) -> str:
        """Get the image source directory path."""
        return cls.IMAGE_SOURCE_DIR
    
    @classmethod
    def get_image_target_path(cls) -> str:
        """Get the image target directory path."""
        return os.path.join(cls.PROJECT_ROOT, cls.IMAGE_TARGET_DIR)
    
    @classmethod
    def get_website_output_path(cls) -> str:
        """Get the website output directory path."""
        return os.path.join(cls.PROJECT_ROOT, cls.WEBSITE_OUTPUT_DIR)
    
    @classmethod
    def get_data_dir_path(cls) -> str:
        """Get the data directory path."""
        return os.path.join(cls.PROJECT_ROOT, cls.DATA_DIR)
    
    @classmethod
    def get_assets_dir_path(cls) -> str:
        """Get the assets directory path."""
        return os.path.join(cls.PROJECT_ROOT, cls.ASSETS_DIR)
    
    @classmethod
    def ensure_directory_exists(cls, directory_path: str) -> bool:
        """Ensure a directory exists, create if it doesn't."""
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception:
            return False
    
    @classmethod
    def get_default_avatar_path(cls) -> str:
        """Get the default avatar image path."""
        return cls.DEFAULT_AVATAR_PATH
    
    @classmethod
    def get_supported_image_extensions(cls) -> list:
        """Get list of supported image file extensions."""
        return cls.SUPPORTED_IMAGE_EXTENSIONS
    
    @classmethod
    def is_supported_image_file(cls, filename: str) -> bool:
        """Check if a file is a supported image format."""
        return any(filename.lower().endswith(ext) for ext in cls.SUPPORTED_IMAGE_EXTENSIONS)
    
    @classmethod
    def get_company_name(cls) -> str:
        """Get the company name."""
        return cls.COMPANY_NAME
    
    @classmethod
    def get_copyright_year(cls) -> str:
        """Get the copyright year."""
        return cls.COPYRIGHT_YEAR
    
    @classmethod
    def get_system_name(cls) -> str:
        """Get the system name."""
        return cls.SYSTEM_NAME
    
    @classmethod
    def get_background_image_url(cls) -> str:
        """Get the background image URL."""
        return cls.BACKGROUND_IMAGE_URL
