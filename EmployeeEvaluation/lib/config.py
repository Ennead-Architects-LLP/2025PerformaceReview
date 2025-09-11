"""
Configuration Settings

This module contains configuration settings for the Employee Evaluation system.
"""

import os
from typing import Dict, Any


class Config:
    """Configuration class for Employee Evaluation system."""
    
    # File settings
    INPUT_FILE_PATTERN = "INPUT*.txt"
    OUTPUT_HTML_FILENAME = "OUTPUT.html"
    OUTPUT_EXCEL_FILENAME = "OUTPUT.xlsx"
    OUTPUT_CSV_FILENAME = "OUTPUT.csv"
    
    # HTML settings
    HTML_TITLE = "Employee Evaluation Report"
    CHART_TYPE = "doughnut"
    CHART_HEIGHT = 300
    
    # Color scheme
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
    
    # Chart colors
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
    
    # Font settings
    FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    FONT_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    
    # Layout settings
    MAX_CONTAINER_WIDTH = "1400px"
    CARD_MIN_WIDTH = "400px"
    CHART_MIN_WIDTH = "350px"
    
    # Animation settings
    ANIMATION_DURATION = 1000
    ANIMATION_EASING = "easeOutQuart"
    
    # Required fields
    REQUIRED_FIELDS = ['name']
    EXCLUDED_FIELDS = ['name', 'time']
    
    @classmethod
    def get_output_path(cls, filename: str) -> str:
        """
        Get full output path for a file.
        
        Args:
            filename: Name of the output file
            
        Returns:
            Full path to the output file
        """
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    @classmethod
    def get_chart_config(cls) -> Dict[str, Any]:
        """
        Get chart configuration.
        
        Returns:
            Dictionary containing chart configuration
        """
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
        """
        Get HTML configuration.
        
        Returns:
            Dictionary containing HTML configuration
        """
        return {
            'title': cls.HTML_TITLE,
            'font_family': cls.FONT_FAMILY,
            'font_url': cls.FONT_URL,
            'max_width': cls.MAX_CONTAINER_WIDTH,
            'card_min_width': cls.CARD_MIN_WIDTH,
            'chart_min_width': cls.CHART_MIN_WIDTH,
            'colors': cls.COLORS
        }
