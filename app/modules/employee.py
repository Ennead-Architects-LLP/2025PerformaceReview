"""
Employee Data Model

Centralized Employee class to manage data from different sources including
Excel parsing, image matching, and other data sources.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from .config import Config


# Employee class no longer uses these dataclasses - all data is stored dynamically


class Employee:
    """Simple Employee class that dynamically generates attributes based on mapped headers."""

    def __init__(self, data: Dict[str, Any] = None):
        """Initialize Employee with dynamic attributes from parsed Excel data."""
        # Initialize with empty data if none provided
        if data is None:
            data = {}

        # Dynamically assign all attributes from the input data
        for key, value in data.items():
            setattr(self, key, value)

        # Ensure basic metadata exists
        if not hasattr(self, 'data_sources'):
            self.data_sources: List[str] = []
        if not hasattr(self, 'last_updated'):
            self.last_updated: Optional[str] = None
    
    def add_data_source(self, source: str):
        """Add a data source to track where data came from."""
        if not hasattr(self, 'data_sources'):
            self.data_sources = []
        if source not in self.data_sources:
            self.data_sources.append(source)

    def has_profile_image(self) -> bool:
        """Check if employee has a profile image."""
        return getattr(self, 'profile_image_filename', None) is not None

    def get_image_display_path(self) -> str:
        """Get the path to display the profile image."""
        profile_image_path = getattr(self, 'profile_image_path', None)
        if profile_image_path:
            return profile_image_path
        return Config.get_default_avatar_path()  # Default fallback
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert employee data to dictionary for JSON serialization."""
        # Start with all dynamic attributes
        result = {}
        for attr_name in dir(self):
            if not attr_name.startswith('_'):  # Skip private attributes
                value = getattr(self, attr_name)
                if not callable(value):  # Skip methods
                    result[attr_name] = value

        return result
    
    @classmethod
    def from_excel_data(cls, excel_data: Dict[str, Any]) -> 'Employee':
        """Create Employee instance from Excel data dictionary."""
        # Create employee with all the Excel data
        employee = cls(excel_data)

        # Add data source
        employee.add_data_source('excel_parser')

        return employee
    
    def __str__(self) -> str:
        """String representation of employee."""
        name = getattr(self, 'employee_name', 'Unknown')
        role = getattr(self, 'employee_role', 'Unknown')
        return f"Employee(name='{name}', role='{role}', has_image={self.has_profile_image()})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        employee_id = getattr(self, 'id', 'Unknown')
        name = getattr(self, 'employee_name', 'Unknown')
        title = getattr(self, 'title_FOR_EXAMPLE', 'Unknown')
        role = getattr(self, 'employee_role', 'Unknown')
        return f"Employee(id='{employee_id}', name='{name}', title='{title}', role='{role}')"


class EmployeeManager:
    """Manager class to handle multiple employees and data operations."""
    
    def __init__(self):
        self.employees: List[Employee] = []
    
    def add_employee(self, employee: Employee):
        """Add an employee to the manager."""
        self.employees.append(employee)
    
    def get_employee_by_name(self, name: str) -> Optional[Employee]:
        """Get employee by name (case-insensitive)."""
        for emp in self.employees:
            emp_name = getattr(emp, 'employee_name', '')
            if emp_name and emp_name.lower() == name.lower():
                return emp
        return None
    
    def get_employees_with_images(self) -> List[Employee]:
        """Get all employees that have profile images."""
        return [emp for emp in self.employees if emp.has_profile_image()]
    
    def get_image_statistics(self) -> Dict[str, int]:
        """Get statistics about employee images."""
        total = len(self.employees)
        with_images = len(self.get_employees_with_images())
        return {
            'total_employees': total,
            'employees_with_images': with_images,
            'employees_without_images': total - with_images,
            'image_coverage_percentage': round((with_images / total * 100) if total > 0 else 0, 1)
        }
    
    def to_json_list(self) -> List[Dict[str, Any]]:
        """Convert all employees to JSON-serializable list."""
        return [emp.to_dict() for emp in self.employees]
    
    def save_to_json(self, output_path: str) -> bool:
        """Save all employee data to JSON file."""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.to_json_list(), f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved {len(self.employees)} employees to {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving employee data: {e}")
            return False
