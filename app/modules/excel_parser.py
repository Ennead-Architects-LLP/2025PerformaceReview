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
from .header_mapper import HeaderMapper, CardGroup


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
        self.header_mapper = HeaderMapper()
        self.header_mappings: Dict[str, Any] = {}
        
    def load_excel(self) -> bool:
        """
        Load the Excel file into a pandas DataFrame and create header mappings.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.excel_path.exists():
                print(f"Error: Excel file not found at {self.excel_path}")
                return False
                
            self.df = pd.read_excel(self.excel_path)
            print(f"✅ Successfully loaded Excel file: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            
            # Create header mappings
            self.header_mappings = self.header_mapper.map_excel_headers(self.df)
            print(f"📋 Created {len(self.header_mappings)} header mappings")
            
            # Print mapping summary for inspection
            self._print_mapping_summary()

            # Save header mappings to JSON
            self._save_header_mappings_json()

            return True
            
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            return False
    
    def _print_mapping_summary(self):
        """Print a summary of header mappings for inspection."""
        summary = self.header_mapper.get_mapping_summary()
        
        print(f"\n📊 Header Mapping Summary:")
        print(f"   Total mappings: {summary['total_mappings']}")
        print(f"   Card group order: {' → '.join(summary['card_group_order'])}")
        
        for group_name, group_info in summary['groups'].items():
            if group_info['count'] > 0:
                print(f"\n   📁 {group_name.replace('_', ' ').title()} ({group_info['count']} fields):")
                for field in group_info['fields']:
                    visibility = "👁️" if field['data_type_in_card'] != 'noshow' else "🙈"
                    chart_type = "📊" if field['data_type_in_chart'] != 'noshow' else "🚫"
                    print(f"      {visibility}{chart_type} {field['column_index']}: {field['original_header']} → {field['mapped_header']} ({field['data_type_in_card']})")

    def _save_header_mappings_json(self):
        """Save header mappings to a JSON file for debugging and reference."""
        import json
        from pathlib import Path

        # Create header mappings list
        header_data = []
        for col_index, mapping in self.header_mappings.items():
            header_entry = {
                "index_column": mapping.column_index,
                "index_letter": mapping.column_letter,
                "header_text": mapping.original_header,
                "mapped_header": mapping.mapped_header,
                "group_under": mapping.group_under.value,
                "data_type_in_card": mapping.data_type_in_card.value,
                "data_type_in_chart": mapping.data_type_in_chart.value,
                "display_order": mapping.display_order
            }
            header_data.append(header_entry)

        # Sort by column index
        header_data.sort(key=lambda x: x['index_column'])

        # Save to JSON file
        output_path = Path("assets/data/header_mappings.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(header_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved header mappings to {output_path}")

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
        Extract employee data from a single row using header mappings.
        
        Args:
            row: Pandas Series representing one row of data
            
        Returns:
            Dictionary containing structured employee data
        """
        employee = {}
        
        # Group data by card groups
        grouped_data = {}
        for group in CardGroup:
            grouped_data[group] = {}
        
        # Process each column using header mappings
        for col_index, mapping in self.header_mappings.items():
            # Use column index to get value (safer than header name)
            try:
                value = row.iloc[col_index]
            except IndexError:
                continue

            # Skip empty values
            if pd.isna(value) or not str(value).strip():
                continue

            # Clean the value
            clean_value = str(value).strip()

            # Store in appropriate group using mapped header as key
            group = mapping.group_under
            grouped_data[group][mapping.mapped_header] = clean_value
        
        
        # Create a flat employee data dict without grouping subdicts
        # All mapped headers are at the top level
        employee = {}

        # Flatten all grouped data into a single level
        for group in CardGroup:
            employee.update(grouped_data[group])

        # Also add the grouped data for backward compatibility (optional)
        # Comment out or remove these lines to make it completely flat
        # employee['performance_ratings'] = grouped_data[CardGroup.PERFORMANCE_RATINGS]
        # employee['performance_comments'] = grouped_data[CardGroup.PERFORMANCE_COMMENTS]
        # employee['software_proficiency'] = grouped_data[CardGroup.SOFTWARE_TOOLS]
        # employee['employee_development'] = grouped_data[CardGroup.EMPLOYEE_DEVELOPMENT]
        # employee['overall_assessment'] = grouped_data[CardGroup.OVERALL_ASSESSMENT]
        # employee['additional_data'] = grouped_data[CardGroup.ADDITIONAL_DATA]
        
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
                
                # Only add if we have essential data - check for any employee name field
                employee_name = None
                # Check common employee name field names
                for possible_name in ['employee_name', 'Employee Name_FOR_EXAMPLE', 'Employee Name Alt_FOR_EXAMPLE', 'name']:
                    if employee_data.get(possible_name):
                        employee_name = employee_data[possible_name].strip()
                        break

                if employee_name:
                    # Create Employee object from data
                    employee = Employee.from_excel_data(employee_data)
                    employees.append(employee)
                    emp_name = getattr(employee, 'employee_name', 'Unknown')
                    print(f"✅ Parsed employee: {emp_name}")
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
    
    def get_header_mappings(self) -> Dict[str, Any]:
        """Get the current header mappings for inspection."""
        return self.header_mapper.get_mapping_summary()
    
    def update_card_group_order(self, new_order: List[CardGroup]):
        """Update the card group display order."""
        self.header_mapper.update_card_group_order(new_order)
    
    def hide_field(self, original_header: str):
        """Hide a field from display."""
        self.header_mapper.hide_field(original_header)
    
    def show_field(self, original_header: str):
        """Show a field in display."""
        self.header_mapper.show_field(original_header)


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
                emp_name = getattr(employee, 'employee_name', '')
                if emp_name in image_mappings:
                    image_info = image_mappings[emp_name]
                    if image_info['filename'] and image_info['copied']:
                        setattr(employee, 'profile_image_filename', image_info['filename'])
                        setattr(employee, 'profile_image_path', f"{Config.IMAGE_TARGET_DIR}/{image_info['filename']}")
                        setattr(employee, 'image_match_confidence', image_info['confidence'])
                    else:
                        setattr(employee, 'profile_image_filename', None)
                        setattr(employee, 'profile_image_path', None)
                        setattr(employee, 'image_match_confidence', None)
                else:
                    setattr(employee, 'profile_image_filename', None)
                    setattr(employee, 'profile_image_path', None)
                    setattr(employee, 'image_match_confidence', None)
                    
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
                setattr(employee, 'profile_image_filename', None)
                setattr(employee, 'profile_image_path', None)
                setattr(employee, 'image_match_confidence', None)
    
    # Create employee manager and save to JSON
    employee_manager = EmployeeManager()
    for employee in employees:
        employee_manager.add_employee(employee)
    
    if not employee_manager.save_to_json(output_path):
        return False
    
    # Print summary
    print("\n📈 Parsing Summary:")
    print(f"   Total employees: {len(employees)}")
    # Count employees with ratings (any non-empty rating)
    ratings_count = sum(1 for emp in employees
                       if getattr(emp, 'performance_ratings', {}).get('communication'))
    print(f"   Employees with ratings: {ratings_count}")

    # Count employees with comments (any non-empty comment)
    comments_count = sum(1 for emp in employees
                        if getattr(emp, 'performance_comments', {}).get('communication_comments'))
    print(f"   Employees with comments: {comments_count}")

    # Count employees with software data (any non-empty software rating)
    software_count = sum(1 for emp in employees
                        if getattr(emp, 'software_proficiency', {}).get('word'))
    print(f"   Employees with software data: {software_count}")
    
    unique_roles = list(set(getattr(emp, 'employee_role', '') for emp in employees
                           if getattr(emp, 'employee_role', '')))
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
