"""
Employee Data Model

Centralized Employee class to manage data from different sources including
Excel parsing, image matching, and other data sources.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field as dc_field
from pathlib import Path
from .config import Config


@dataclass
class PerformanceRatings:
    """Performance ratings data structure."""
    communication: Optional[str] = None
    collaboration: Optional[str] = None
    professionalism: Optional[str] = None
    technical_knowledge_expertise: Optional[str] = None
    workflow_implementation_management_execution: Optional[str] = None
    overall_performance: Optional[str] = None


@dataclass
class PerformanceComments:
    """Performance comments data structure."""
    communication_comments: Optional[str] = None
    collaboration_comments: Optional[str] = None
    professionalism_comments: Optional[str] = None
    technical_knowledge_expertise_comments: Optional[str] = None
    workflow_implementation_management_execution_comments: Optional[str] = None


@dataclass
class SoftwareProficiency:
    """Software proficiency ratings data structure."""
    revit: Optional[str] = None
    rhino: Optional[str] = None
    enscape: Optional[str] = None
    d5: Optional[str] = None
    vantage_point: Optional[str] = None
    deltek_adp: Optional[str] = None
    newforma: Optional[str] = None
    bluebeam: Optional[str] = None
    grasshopper: Optional[str] = None
    word: Optional[str] = None
    powerpoint: Optional[str] = None
    excel: Optional[str] = None
    illustrator: Optional[str] = None
    photoshop: Optional[str] = None
    indesign: Optional[str] = None


@dataclass
class AdditionalEvaluationData:
    """Additional evaluation data structure."""
    performance_examples: Optional[str] = None
    additional_resources: Optional[str] = None
    employee_strengths: Optional[str] = None
    areas_for_growth: Optional[str] = None
    studio_culture_feedback: Optional[str] = None
    software_tools_feedback: Optional[str] = None


class Employee:
    """Central Employee class to manage all employee data from different sources."""
    
    def __init__(self):
        # Basic employee information
        self.id: Optional[str] = None
        self.name: Optional[str] = None
        self.title: Optional[str] = None
        self.role: Optional[str] = None
        self.email: Optional[str] = None
        self.start_time: Optional[str] = None
        self.completion_time: Optional[str] = None
        self.date: Optional[str] = None
        
        # Profile image information
        self.profile_image_filename: Optional[str] = None
        self.profile_image_path: Optional[str] = None
        self.image_match_confidence: Optional[float] = None
        
        # Performance data structures
        self.performance_ratings = PerformanceRatings()
        self.performance_comments = PerformanceComments()
        self.software_proficiency = SoftwareProficiency()
        self.additional_data = AdditionalEvaluationData()
        
        # Additional metadata
        self.data_sources: List[str] = []
        self.last_updated: Optional[str] = None
    
    def set_basic_info(self, id: str = None, name: str = None, title: str = None, 
                      role: str = None, email: str = None, start_time: str = None,
                      completion_time: str = None, date: str = None):
        """Set basic employee information."""
        if id is not None:
            self.id = str(id)
        if name is not None:
            self.name = name
        if title is not None:
            self.title = title
        if role is not None:
            self.role = role
        if email is not None:
            self.email = email
        if start_time is not None:
            self.start_time = start_time
        if completion_time is not None:
            self.completion_time = completion_time
        if date is not None:
            self.date = date
    
    def set_profile_image(self, filename: str, confidence: float = None):
        """Set profile image information."""
        self.profile_image_filename = filename
        self.profile_image_path = f"{Config.IMAGE_TARGET_DIR}/{filename}" if filename else None
        self.image_match_confidence = confidence
    
    def set_performance_ratings(self, ratings: Dict[str, str]):
        """Set performance ratings from dictionary."""
        for key, value in ratings.items():
            if key == 'communication':
                self.performance_ratings.communication = value
            elif key == 'collaboration':
                self.performance_ratings.collaboration = value
            elif key == 'professionalism':
                self.performance_ratings.professionalism = value
            elif key == 'technical_knowledge_&_expertise':
                self.performance_ratings.technical_knowledge_expertise = value
            elif key == 'workflow_implementation,_management,_execution':
                self.performance_ratings.workflow_implementation_management_execution = value
            elif key == 'overall_performance_rating':
                self.performance_ratings.overall_performance = value
    
    def set_performance_comments(self, comments: Dict[str, str]):
        """Set performance comments from dictionary."""
        for key, value in comments.items():
            if key == 'communication_comments':
                self.performance_comments.communication_comments = value
            elif key == 'collaboration_comments':
                self.performance_comments.collaboration_comments = value
            elif key == 'professionalism_comments':
                self.performance_comments.professionalism_comments = value
            elif key == 'technical_knowledge_&_expertise_comments':
                self.performance_comments.technical_knowledge_expertise_comments = value
            elif key == 'workflow_implementation,_management,_execution_comments':
                self.performance_comments.workflow_implementation_management_execution_comments = value
    
    def set_software_proficiency(self, proficiency: Dict[str, str]):
        """Set software proficiency from dictionary."""
        for key, value in proficiency.items():
            if key == 'revit':
                self.software_proficiency.revit = value
            elif key == 'rhino':
                self.software_proficiency.rhino = value
            elif key == 'enscape':
                self.software_proficiency.enscape = value
            elif key == 'd5':
                self.software_proficiency.d5 = value
            elif key == 'vantage_point':
                self.software_proficiency.vantage_point = value
            elif key == 'deltek_adp':
                self.software_proficiency.deltek_adp = value
            elif key == 'newforma':
                self.software_proficiency.newforma = value
            elif key == 'bluebeam':
                self.software_proficiency.bluebeam = value
            elif key == 'grasshopper':
                self.software_proficiency.grasshopper = value
            elif key == 'word':
                self.software_proficiency.word = value
            elif key == 'powerpoint':
                self.software_proficiency.powerpoint = value
            elif key == 'excel':
                self.software_proficiency.excel = value
            elif key == 'illustrator':
                self.software_proficiency.illustrator = value
            elif key == 'photoshop':
                self.software_proficiency.photoshop = value
            elif key == 'indesign':
                self.software_proficiency.indesign = value
    
    def set_additional_data(self, data: Dict[str, str]):
        """Set additional evaluation data from dictionary."""
        for key, value in data.items():
            if key == 'performance_examples':
                self.additional_data.performance_examples = value
            elif key == 'additional_resources':
                self.additional_data.additional_resources = value
            elif key == 'employee_strengths':
                self.additional_data.employee_strengths = value
            elif key == 'areas_for_growth':
                self.additional_data.areas_for_growth = value
            elif key == 'studio_culture_feedback':
                self.additional_data.studio_culture_feedback = value
            elif key == 'software_tools_feedback':
                self.additional_data.software_tools_feedback = value
    
    def add_data_source(self, source: str):
        """Add a data source to track where data came from."""
        if source not in self.data_sources:
            self.data_sources.append(source)
    
    def has_profile_image(self) -> bool:
        """Check if employee has a profile image."""
        return self.profile_image_filename is not None
    
    def get_image_display_path(self) -> str:
        """Get the path to display the profile image."""
        if self.profile_image_path:
            return self.profile_image_path
        return Config.get_default_avatar_path()  # Default fallback
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert employee data to dictionary for JSON serialization."""
        result = {
            # Basic information
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'role': self.role,
            'email': self.email,
            'start_time': self.start_time,
            'completion_time': self.completion_time,
            'date': self.date,
            
            # Profile image information
            'profile_image': {
                'filename': self.profile_image_filename,
                'path': self.profile_image_path,
                'has_image': self.has_profile_image(),
                'display_path': self.get_image_display_path(),
                'match_confidence': self.image_match_confidence
            },
            
            # Performance data
            'performance_ratings': {
                'communication': self.performance_ratings.communication,
                'collaboration': self.performance_ratings.collaboration,
                'professionalism': self.performance_ratings.professionalism,
                'technical_knowledge_expertise': self.performance_ratings.technical_knowledge_expertise,
                'workflow_implementation_management_execution': self.performance_ratings.workflow_implementation_management_execution,
                'overall_performance': self.performance_ratings.overall_performance
            },
            
            'performance_comments': {
                'communication_comments': self.performance_comments.communication_comments,
                'collaboration_comments': self.performance_comments.collaboration_comments,
                'professionalism_comments': self.performance_comments.professionalism_comments,
                'technical_knowledge_expertise_comments': self.performance_comments.technical_knowledge_expertise_comments,
                'workflow_implementation_management_execution_comments': self.performance_comments.workflow_implementation_management_execution_comments
            },
            
            'software_proficiency': {
                'revit': self.software_proficiency.revit,
                'rhino': self.software_proficiency.rhino,
                'enscape': self.software_proficiency.enscape,
                'd5': self.software_proficiency.d5,
                'vantage_point': self.software_proficiency.vantage_point,
                'deltek_adp': self.software_proficiency.deltek_adp,
                'newforma': self.software_proficiency.newforma,
                'bluebeam': self.software_proficiency.bluebeam,
                'grasshopper': self.software_proficiency.grasshopper,
                'word': self.software_proficiency.word,
                'powerpoint': self.software_proficiency.powerpoint,
                'excel': self.software_proficiency.excel,
                'illustrator': self.software_proficiency.illustrator,
                'photoshop': self.software_proficiency.photoshop,
                'indesign': self.software_proficiency.indesign
            },
            
            'additional_evaluation_data': {
                'performance_examples': self.additional_data.performance_examples,
                'additional_resources': self.additional_data.additional_resources,
                'employee_strengths': self.additional_data.employee_strengths,
                'areas_for_growth': self.additional_data.areas_for_growth,
                'studio_culture_feedback': self.additional_data.studio_culture_feedback,
                'software_tools_feedback': self.additional_data.software_tools_feedback
            },
            
            # Metadata
            'data_sources': self.data_sources,
            'last_updated': self.last_updated
        }
        
        return result
    
    @classmethod
    def from_excel_data(cls, excel_data: Dict[str, Any]) -> 'Employee':
        """Create Employee instance from Excel data dictionary."""
        employee = cls()
        
        # Set basic information
        employee.set_basic_info(
            id=excel_data.get('id'),
            name=excel_data.get('name'),
            title=excel_data.get('title'),
            role=excel_data.get('role'),
            email=excel_data.get('email'),
            start_time=excel_data.get('start_time'),
            completion_time=excel_data.get('completion_time'),
            date=excel_data.get('date')
        )
        
        # Set performance data
        if 'performance_ratings' in excel_data:
            employee.set_performance_ratings(excel_data['performance_ratings'])
        
        if 'performance_comments' in excel_data:
            employee.set_performance_comments(excel_data['performance_comments'])
        
        if 'software_proficiency' in excel_data:
            employee.set_software_proficiency(excel_data['software_proficiency'])
        
        if 'additional_evaluation_data' in excel_data:
            employee.set_additional_data(excel_data['additional_evaluation_data'])
        
        # Set profile image if available
        if 'profile_image' in excel_data and excel_data['profile_image']:
            employee.set_profile_image(excel_data['profile_image'])
        
        employee.add_data_source('excel_parser')
        
        return employee
    
    def __str__(self) -> str:
        """String representation of employee."""
        return f"Employee(name='{self.name}', role='{self.role}', has_image={self.has_profile_image()})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Employee(id='{self.id}', name='{self.name}', title='{self.title}', role='{self.role}')"


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
            if emp.name and emp.name.lower() == name.lower():
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
