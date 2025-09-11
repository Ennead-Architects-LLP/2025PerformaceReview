"""
Excel Parser for Employee Self-Evaluation Data

Parses the Excel file exported from MS Form and converts it to structured JSON format.
"""

import pandas as pd
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from .image_manager import ImageManager
from .employee import Employee, EmployeeManager
from .config import Config


class ExcelEmployeeParser:
    """Parser for Excel-based employee evaluation data."""
    
    def __init__(self, excel_path: str):
        """
        Initialize the parser with the Excel file path.
        
        Args:
            excel_path: Path to the Excel file
        """
        self.excel_path = Path(excel_path)
        self.df: Optional[pd.DataFrame] = None
        self.employees_data: List[Dict[str, Any]] = []
        
    def load_excel(self) -> bool:
        """
        Load the Excel file into a pandas DataFrame.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.excel_path.exists():
                print(f"Error: Excel file not found at {self.excel_path}")
                return False
                
            self.df = pd.read_excel(self.excel_path)
            print(f"✅ Successfully loaded Excel file: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            return True
            
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            return False
    
    def clean_column_name(self, col_name: str) -> str:
        """
        Clean and standardize column names.
        
        Args:
            col_name: Raw column name from Excel
            
        Returns:
            Cleaned column name
        """
        if pd.isna(col_name):
            return "unknown_column"
            
        # Remove newlines and extra whitespace
        cleaned = re.sub(r'\n+', ' ', str(col_name))
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Convert to snake_case
        cleaned = cleaned.lower()
        cleaned = re.sub(r'[^a-z0-9\s]', '', cleaned)
        cleaned = re.sub(r'\s+', '_', cleaned)
        
        return cleaned
    
    def extract_employee_data(self, row: pd.Series) -> Dict[str, Any]:
        """
        Extract employee data from a single row.
        
        Args:
            row: Pandas Series representing one row of data
            
        Returns:
            Dictionary containing structured employee data
        """
        employee = {}
        
        # Basic employee information
        employee['id'] = str(row.get('ID', ''))
        employee['name'] = str(row.get('Employee Name', ''))
        employee['title'] = str(row.get('Title', ''))
        employee['role'] = str(row.get('Role', ''))
        employee['email'] = str(row.get('Email', ''))
        employee['start_time'] = str(row.get('Start time', ''))
        employee['completion_time'] = str(row.get('Completion time', ''))
        employee['date'] = str(row.get('Date', ''))
        
        # Performance ratings (1-5 scale)
        performance_ratings = {}
        rating_columns = [
            'Communication', 'Collaboration', 'Professionalism', 
            'Technical Knowledge & Expertise', 'Workflow Implementation, Management, Execution'
        ]
        
        for col in rating_columns:
            # Try exact match first
            if col in row.index:
                value = row[col]
                if pd.notna(value) and str(value).strip():
                    performance_ratings[col.lower().replace(' ', '_')] = str(value).strip()
            
            # Try variations with newlines
            for alt_col in row.index:
                if col in str(alt_col):
                    value = row[alt_col]
                    if pd.notna(value) and str(value).strip() and col.lower().replace(' ', '_') not in performance_ratings:
                        performance_ratings[col.lower().replace(' ', '_')] = str(value).strip()
        
        employee['performance_ratings'] = performance_ratings
        
        # Performance comments
        performance_comments = {}
        comment_columns = [
            'Communication2', 'Collaboration', 'Professionalism', 
            'Technical Knowledge & Expertise', 'Workflow Implementation, Management, Execution'
        ]
        
        for col in comment_columns:
            # Look for comment columns (usually with '2' suffix or variations)
            for alt_col in row.index:
                if col in str(alt_col) and alt_col != col:
                    value = row[alt_col]
                    if pd.notna(value) and str(value).strip():
                        # Skip if it's a rating (numeric)
                        if not str(value).strip().isdigit():
                            comment_key = col.lower().replace(' ', '_') + '_comments'
                            performance_comments[comment_key] = str(value).strip()
                            break
        
        employee['performance_comments'] = performance_comments
        
        # Software proficiency ratings
        software_ratings = {}
        software_columns = [
            'Revit', 'Rhino', 'Enscape', 'D5', 'Vantage Point', 'Deltek/ADP',
            'Newforma', 'Bluebeam', 'Grasshopper', 'Word', 'Powerpoint', 'Excel',
            'Illustrator', 'Photoshop', 'Indesign'
        ]
        
        for software in software_columns:
            if software in row.index:
                value = row[software]
                if pd.notna(value) and str(value).strip():
                    software_ratings[software.lower().replace(' ', '_').replace('/', '_')] = str(value).strip()
        
        employee['software_proficiency'] = software_ratings
        
        # Additional evaluation data
        additional_data = {}
        
        # Overall performance rating
        overall_perf_col = 'Rate Your Overall Performance This Year'
        if overall_perf_col in row.index:
            value = row[overall_perf_col]
            if pd.notna(value) and str(value).strip():
                additional_data['overall_performance_rating'] = str(value).strip()
        
        # Additional performance examples
        examples_col = 'Are there specific examples of your performance you\'d like to share that weren\'t captured in earlier questions?'
        if examples_col in row.index:
            value = row[examples_col]
            if pd.notna(value) and str(value).strip():
                additional_data['performance_examples'] = str(value).strip()
        
        # Additional resources
        resources_col = 'What additional resources would help you do your job more effectively?'
        if resources_col in row.index:
            value = row[resources_col]
            if pd.notna(value) and str(value).strip():
                additional_data['additional_resources'] = str(value).strip()
        
        # Employee strengths
        strengths_col = 'Employee Strengths'
        if strengths_col in row.index:
            value = row[strengths_col]
            if pd.notna(value) and str(value).strip():
                additional_data['employee_strengths'] = str(value).strip()
        
        # Areas for growth
        growth_col = 'Areas for Growth / Development Goals'
        if growth_col in row.index:
            value = row[growth_col]
            if pd.notna(value) and str(value).strip():
                additional_data['areas_for_growth'] = str(value).strip()
        
        # Studio culture feedback
        culture_col = 'Please share your thoughts about the character and culture of our studio and practice.'
        if culture_col in row.index:
            value = row[culture_col]
            if pd.notna(value) and str(value).strip():
                additional_data['studio_culture_feedback'] = str(value).strip()
        
        # Software tools feedback
        tools_col = 'Software & Tools2'
        if tools_col in row.index:
            value = row[tools_col]
            if pd.notna(value) and str(value).strip():
                additional_data['software_tools_feedback'] = str(value).strip()
        
        employee['additional_evaluation_data'] = additional_data
        
        return employee
    
    def parse_all_employees(self) -> List[Employee]:
        """
        Parse all employee data from the Excel file.
        
        Returns:
            List of Employee objects
        """
        if self.df is None:
            print("Error: Excel file not loaded. Call load_excel() first.")
            return []
        
        employees = []
        
        print(f"📊 Parsing {len(self.df)} employee records...")
        
        for index, row in self.df.iterrows():
            try:
                employee_data = self.extract_employee_data(row)
                
                # Only add if we have essential data
                if employee_data.get('name') and employee_data.get('name').strip():
                    # Create Employee object from data
                    employee = Employee.from_excel_data(employee_data)
                    employees.append(employee)
                    print(f"✅ Parsed employee: {employee.name}")
                else:
                    print(f"⚠️  Skipped row {index}: Missing employee name")
                    
            except Exception as e:
                print(f"❌ Error parsing row {index}: {e}")
                continue
        
        print(f"🎉 Successfully parsed {len(employees)} employee records")
        return employees
    
    def save_to_json(self, employees: List[Employee], output_path: str = None) -> bool:
        """
        Save the parsed employee data to a JSON file.
        
        Args:
            employees: List of Employee objects
            output_path: Path to save the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        if not employees:
            print("Error: No employee data to save.")
            return False
        
        try:
            output_file = Path(output_path)
            
            # Create output directory if it doesn't exist
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert employees to JSON-serializable format
            json_data = [emp.to_dict() for emp in employees]
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Successfully saved employee data to {output_file}")
            print(f"   Records saved: {len(employees)}")
            print(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")
            
            return True
            
        except Exception as e:
            print(f"Error saving JSON file: {e}")
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the parsed data.
        
        Returns:
            Dictionary containing summary statistics
        """
        if not self.employees_data:
            return {"error": "No data available"}
        
        summary = {
            "total_employees": len(self.employees_data),
            "employees_with_ratings": sum(1 for emp in self.employees_data if emp.get('performance_ratings')),
            "employees_with_comments": sum(1 for emp in self.employees_data if emp.get('performance_comments')),
            "employees_with_software_data": sum(1 for emp in self.employees_data if emp.get('software_proficiency')),
            "unique_roles": list(set(emp.get('role', '') for emp in self.employees_data if emp.get('role'))),
            "date_range": {
                "earliest": min(emp.get('start_time', '') for emp in self.employees_data if emp.get('start_time')),
                "latest": max(emp.get('start_time', '') for emp in self.employees_data if emp.get('start_time'))
            }
        }
        
        return summary


def parse_excel_to_json(excel_path: str, output_path: str = None, 
                       copy_images: bool = True, image_source_dir: str = None) -> bool:
    """
    Convenience function to parse Excel file and save to JSON.
    
    Args:
        excel_path: Path to the Excel file
        output_path: Path to save the JSON file
        copy_images: Whether to copy employee profile images
        image_source_dir: Source directory for employee images
        
    Returns:
        True if successful, False otherwise
    """
    parser = ExcelEmployeeParser(excel_path)
    
    if not parser.load_excel():
        return False
    
    employees = parser.parse_all_employees()
    if not employees:
        return False
    
    # Copy employee images if requested
    if copy_images:
        print("\n🖼️  Processing employee profile images...")
        try:
            # Set default image source directory
            if not image_source_dir:
                image_source_dir = Config.get_image_source_path()
            
            image_manager = ImageManager(image_source_dir, Config.IMAGE_TARGET_DIR)
            image_mappings = image_manager.copy_employee_images(employees)
            
            # Update employee objects with image information
            for employee in employees:
                if employee.name in image_mappings:
                    image_info = image_mappings[employee.name]
                    if image_info['filename'] and image_info['copied']:
                        employee.set_profile_image(
                            image_info['filename'], 
                            image_info['confidence']
                        )
                    else:
                        employee.set_profile_image(None)
                else:
                    employee.set_profile_image(None)
                    
            # Save image mappings for reference
            image_manager.save_image_mappings(Config.get_image_mappings_path())
            
            # Show asset library statistics
            asset_stats = image_manager.get_asset_library_stats()
            print(f"📚 Asset Library: {asset_stats['total_images']} total images")
            print(f"   Matched: {asset_stats['matched_images']}")
            print(f"   Available: {asset_stats['unmatched_images']}")
                    
        except Exception as e:
            print(f"⚠️  Warning: Could not process images: {e}")
            for employee in employees:
                employee.set_profile_image(None)
    
    # Create employee manager and save to JSON
    employee_manager = EmployeeManager()
    for employee in employees:
        employee_manager.add_employee(employee)
    
    if not employee_manager.save_to_json(output_path):
        return False
    
    # Print summary
    print("\n📈 Parsing Summary:")
    print(f"   Total employees: {len(employees)}")
    print(f"   Employees with ratings: {sum(1 for emp in employees if emp.performance_ratings.communication)}")
    print(f"   Employees with comments: {sum(1 for emp in employees if emp.performance_comments.communication_comments)}")
    print(f"   Employees with software data: {sum(1 for emp in employees if emp.software_proficiency.word)}")
    
    unique_roles = list(set(emp.role for emp in employees if emp.role))
    print(f"   Unique roles: {len(unique_roles)}")
    
    if copy_images:
        image_stats = employee_manager.get_image_statistics()
        print(f"   Employees with profile images: {image_stats['employees_with_images']}")
        print(f"   Image coverage: {image_stats['image_coverage_percentage']}%")
    
    return True


if __name__ == "__main__":
    # Example usage
    excel_file = Config.get_excel_input_path()
    json_file = Config.get_json_output_path()
    
    success = parse_excel_to_json(excel_file, json_file)
    if success:
        print(f"\n🎉 Pipeline completed successfully!")
        print(f"   Excel file: {excel_file}")
        print(f"   JSON output: {json_file}")
    else:
        print(f"\n❌ Pipeline failed!")
