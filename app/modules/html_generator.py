"""
HTML Report Generator

This module handles the generation of interactive HTML reports from employee evaluation data.
"""

import os
import json
from collections import defaultdict, Counter
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
# Removed parser import - functions moved to this module
from .config import Config


def get_employee_initials(name: str) -> str:
    """Get employee initials from name."""
    return ''.join([word[0].upper() for word in name.split()[:2]])


def clean_field_name(field_name: str) -> str:
    """Clean field name for display."""
    return field_name.replace("_", " ").title()


def get_excluded_chart_fields() -> set:
    """Return a set of fields to exclude from charts."""
    return {
        'professionalism_comments',
        'communication_comments',
        'collaboration_comments',
        'workflow implementation, management, execution_comments',
        'software & tools_overall_comments',
        'employee strengths',
        'employee areas for growth & development',
        'additional_comments_regarding_performance',
        'evaluator_name',
        'technical knowledge & expertise_comments',
        'responder',
        'submitted',
        'employee name',
        'employee_name',
        'name'
    }


def create_html_output_from_json(data_file: str = None, output_dir: str = None) -> str:
    """Create HTML output from JSON employee data file."""
    try:
        # Use config defaults if not provided
        if data_file is None:
            data_file = Config.get_json_output_path()
        if output_dir is None:
            output_dir = Config.get_website_output_path()
        
        # Load employee data from JSON
        with open(data_file, 'r', encoding='utf-8') as f:
            employees = json.load(f)
        
        print(f"✅ Loaded {len(employees)} employee records from JSON")
        
        # Convert to flat structure for the new format
        flat_employees = convert_to_flat_structure(employees)
        
        # Extract all fields from the flat structure
        all_fields = extract_all_fields_from_flat(flat_employees)
        
        chart_data = prepare_chart_data_from_flat(flat_employees)
        html_content = generate_html_template(flat_employees, all_fields, chart_data)

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (output_path / "css").mkdir(exist_ok=True)
        (output_path / "js").mkdir(exist_ok=True)
        (output_path / "assets").mkdir(exist_ok=True)
        (output_path / "assets" / "images").mkdir(parents=True, exist_ok=True)

        # Write main HTML file
        with open(output_path / "index.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Write CSS file
        with open(output_path / "css" / "styles.css", 'w', encoding='utf-8') as f:
            f.write(get_css_styles())
        
        # Write JavaScript file
        with open(output_path / "js" / "script.js", 'w', encoding='utf-8') as f:
            f.write(generate_javascript_content(flat_employees, chart_data))
        
        # Copy images to website assets
        copy_images_to_website(output_path)

        print(f"🌐 Website generated successfully!")
        print(f"   📁 Output directory: {output_path}")
        print(f"   📄 Main page: {output_path / 'index.html'}")
        
        return str(output_path / "index.html")

    except Exception as e:
        print(f"❌ Error creating HTML output: {e}")
        return ""


def convert_to_flat_structure(employees: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Convert nested employee data to flat structure for the new HTML format."""
    flat_employees = []
    
    for employee in employees:
        flat_emp = {}
        
        # Basic information
        flat_emp['employee_name'] = employee.get('name', '')
        flat_emp['title'] = employee.get('title', '')
        flat_emp['employee_role'] = employee.get('role', '')
        flat_emp['email'] = employee.get('email', '')
        flat_emp['evaluator_name'] = employee.get('evaluator_name', '')
        flat_emp['date_of_evaluation'] = employee.get('date', '').split(' ')[0] if employee.get('date') else ''
        flat_emp['submitted'] = employee.get('completion_time', '')
        flat_emp['responder'] = employee.get('email', '')
        
        # Profile image information - keep as dict for HTML generation
        profile_image = employee.get('profile_image', {})
        flat_emp['profile_image'] = profile_image
        
        # Performance ratings
        performance_ratings = employee.get('performance_ratings', {})
        for key, value in performance_ratings.items():
            if key == 'overall_performance':
                flat_emp['overall_performance'] = str(value) if value else ''
            else:
                # Convert key to match expected format
                clean_key = key.replace('_', ' ').title().replace(' ', ' & ').replace('&', '&')
                if 'Technical' in clean_key:
                    clean_key = 'Technical Knowledge & Expertise'
                elif 'Workflow' in clean_key:
                    clean_key = 'Workflow Implementation, Management, Execution'
                flat_emp[f'{clean_key}_rating'] = str(value) if value else ''
        
        # Performance comments
        performance_comments = employee.get('performance_comments', {})
        for key, value in performance_comments.items():
            # Convert key to match expected format
            clean_key = key.replace('_comments', '').replace('_', ' ').title()
            if 'Technical' in clean_key:
                clean_key = 'Technical Knowledge & Expertise'
            elif 'Workflow' in clean_key:
                clean_key = 'Workflow Implementation, Management, Execution'
            flat_emp[f'{clean_key}_comments'] = str(value) if value else ''
        
        # Software proficiency
        software_proficiency = employee.get('software_proficiency', {})
        for key, value in software_proficiency.items():
            # Handle special case for deltek_adp
            if key == 'deltek_adp':
                key = 'deltek/adp'
            flat_emp[key] = str(value) if value else ''
        
        # Additional evaluation data
        additional_data = employee.get('additional_evaluation_data', {})
        for key, value in additional_data.items():
            flat_emp[key] = str(value) if value else ''
        
        flat_employees.append(flat_emp)
    
    return flat_employees


def extract_all_fields_from_flat(employees: List[Dict[str, str]]) -> List[str]:
    """Extract all field names from flat employee data."""
    all_fields = set()
    
    for employee in employees:
        for key in employee.keys():
            all_fields.add(key)
    
    return list(all_fields)


def prepare_chart_data_from_flat(employees: List[Dict[str, str]]) -> Dict[str, Dict[str, int]]:
    """Prepare chart data from flat employee data."""
    excluded_fields = get_excluded_chart_fields()
    field_value_counts = defaultdict(Counter)
    
    for emp in employees:
        for field, value in emp.items():
            if field.lower() not in excluded_fields and value and value.strip():
                field_value_counts[field][value] += 1
    
    return {field: dict(counter) for field, counter in field_value_counts.items()}


def copy_images_to_website(output_path: Path):
    """Copy images to website assets directory."""
    source_images_dir = Path(Config.get_image_target_path())
    target_images_dir = output_path / "assets" / "images"
    
    if source_images_dir.exists():
        import shutil
        for image_file in source_images_dir.iterdir():
            if image_file.is_file():
                shutil.copy2(image_file, target_images_dir / image_file.name)
        print(f"📸 Copied images to {target_images_dir}")


def create_html_output(employees: List[Dict[str, str]], all_fields: List[str], output_filename: str = 'OUTPUT.html') -> str:
    """Legacy function for backward compatibility."""
    chart_data = prepare_chart_data_from_flat(employees)
    html_content = generate_html_template(employees, all_fields, chart_data)

    docs_dir = Config.get_docs_dir()
    output_path = Config.get_docs_output_path('html')
    os.makedirs(docs_dir, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML file created: {output_path}")
    return output_path


def generate_html_template(employees: List[Dict[str, str]], all_fields: List[str], chart_data: Dict[str, Dict[str, int]]) -> str:
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Employee Evaluation Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    {get_css_styles()}
</head>
<body>
    <div class="background-container"></div>
    <div class="container">
        {generate_header(employees)}
        {generate_tabs()}
        {generate_detailed_tab(employees)}
        {generate_summary_tab(employees, all_fields)}
        {generate_footer()}
    </div>
    <button class="return-to-top" onclick="scrollToTop()" title="Return to top">↑</button>
    {generate_javascript(employees, chart_data)}
</body>
</html>
"""


def get_css_styles() -> str:
    """Generate CSS styles for the website."""
    return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            color: #1A1A1A;
            position: relative;
            overflow-x: hidden;
        }
        
        .background-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: linear-gradient(135deg, rgba(58, 175, 169, 0.9) 0%, rgba(43, 122, 120, 0.9) 100%), 
                        url('https://image-cdn.hypb.st/https%3A%2F%2Fhypebeast.com%2Fimage%2F2021%2F08%2Fshanghai-astronomy-museum-ennead-architects-china-6.jpg?q=75&w=800&cbr=1&fit=max');
            background-size: 120%;
            background-position: center;
            background-attachment: fixed;
            animation: rotateBackground 30s linear infinite;
        }
        
        @keyframes rotateBackground {
            0% {
                background-size: 120%;
                transform: rotate(0deg);
            }
            25% {
                background-size: 125%;
            }
            50% {
                background-size: 120%;
                transform: rotate(0.5deg);
            }
            75% {
                background-size: 125%;
            }
            100% {
                background-size: 120%;
                transform: rotate(0deg);
            }
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .header {
            background: linear-gradient(135deg, #0F1419 0%, #1A5A58 100%);
            color: #FFFFFF;
            padding: 40px 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.3;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 8px;
            position: relative;
            z-index: 1;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }
        
        .tabs {
            display: flex;
            background: #F0F8F7;
            border-bottom: 1px solid #1A5A58;
        }
        
        .tab {
            flex: 1;
            padding: 20px 30px;
            text-align: center;
            background: transparent;
            color: #1A5A58;
            cursor: pointer;
            border: none;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }
        
        .tab:hover {
            color: #0F1419;
            background: rgba(26, 90, 88, 0.1);
        }
        
        .tab.active {
            color: #0F1419;
            background: white;
            box-shadow: 0 -2px 0 #2B7A78 inset;
        }
        
        .tab-content {
            display: none;
            padding: 40px 30px;
            min-height: 500px;
        }
        
        .tab-content.active {
            display: block;
            animation: fadeInUp 0.5s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .search-container {
            margin-bottom: 30px;
            position: relative;
        }
        
        .search-box {
            width: 100%;
            padding: 16px 20px 16px 50px;
            border: 1px solid #E0E8E7;
            border-radius: 8px;
            font-size: 1rem;
            background: white;
            transition: all 0.2s ease;
            color: #1A1A1A;
        }
        
        .search-box:focus {
            outline: none;
            border-color: #2B7A78;
            box-shadow: 0 0 0 2px rgba(43, 122, 120, 0.1);
        }
        
        .search-icon {
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            width: 20px;
            height: 20px;
            opacity: 0.5;
            pointer-events: none;
            transition: opacity 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: searchPulse 2s ease-in-out infinite;
        }
        
        .search-icon img {
            width: 100%;
            height: 100%;
            object-fit: contain;
            filter: opacity(0.7);
            transition: filter 0.2s ease;
        }
        
        @keyframes searchPulse {
            0%, 100% {
                transform: translateY(-50%) scale(1);
                opacity: 0.5;
            }
            50% {
                transform: translateY(-50%) scale(1.1);
                opacity: 0.7;
            }
        }
        
        .search-container:focus-within .search-icon {
            opacity: 0.7;
        }
        
        .search-box:not(:placeholder-shown) + .search-icon {
            opacity: 0.3;
        }
        
        .employee-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 24px;
        }
        
        .employee-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #E0E8E7;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .employee-card:hover {
            border-color: #2B7A78;
            box-shadow: 0 4px 12px rgba(43, 122, 120, 0.1);
        }
        
        .employee-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            gap: 20px;
        }
        
        .profile-image {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
            border: 4px solid #2B7A78;
            flex-shrink: 0;
        }
        
        .default-avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, #2B7A78, #1A5A58);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 2rem;
            font-weight: bold;
            border: 4px solid #2B7A78;
            flex-shrink: 0;
        }
        
        .employee-info {
            flex: 1;
        }
        
        .employee-name {
            font-size: 1.25rem;
            font-weight: 500;
            color: #0F1419;
            margin-bottom: 8px;
        }
        
        .employee-time {
            color: #4A4A4A;
            font-size: 0.875rem;
        }
        
        .fields-container {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .field {
            display: flex;
            flex-direction: column;
            gap: 6px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(45, 122, 120, 0.08);
            margin-bottom: 12px;
        }
        
        .field:last-child {
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }
        
        .field:hover {
            border-bottom-color: rgba(45, 122, 120, 0.15);
            transition: border-bottom-color 0.2s ease;
        }
        
        .field-group {
            margin-bottom: 24px;
            padding: 16px;
            background: rgba(240, 248, 247, 0.5);
            border-radius: 8px;
            border: 2px solid #2B7A78;
        }
        
        .group-title {
            font-size: 1rem;
            font-weight: 600;
            color: #0F1419;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(43, 122, 120, 0.3);
        }
        
        .field-group .field {
            margin-bottom: 8px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(45, 122, 120, 0.1);
        }
        
        .field-group .field:last-child {
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }
        
        .software-tools-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        
        .software-tools-grid .field {
            margin-bottom: 8px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(45, 122, 120, 0.1);
        }
        
        .software-tools-grid .field:last-child {
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }
        
        @media (max-width: 768px) {
            .software-tools-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .return-to-top {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #3AAFA9, #2B7A78);
            border: none;
            border-radius: 50%;
            color: white;
            font-size: 20px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(45, 122, 120, 0.3);
            transition: all 0.3s ease;
            z-index: 1000;
            display: none;
            align-items: center;
            justify-content: center;
        }
        
        .return-to-top:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(45, 122, 120, 0.4);
            background: linear-gradient(135deg, #2B7A78, #1A5A58);
        }
        
        .return-to-top:active {
            transform: translateY(0);
        }
        
        .return-to-top.show {
            display: flex;
        }
        
        .field-label {
            font-weight: 500;
            color: #1A5A58;
            font-size: 0.875rem;
            margin-bottom: 4px;
        }
        
        .field-value {
            color: #1A1A1A;
            font-size: 1rem;
            line-height: 1.5;
        }
        
        .software-tools-grid .field-value {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .rating-number {
            font-weight: 600;
            color: #1A1A1A;
            font-size: 1rem;
        }
        
        .rating-description {
            font-size: 0.8rem;
            color: #6B7280;
            font-weight: 400;
        }
        
        .field-group .field-value {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .chart-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }
        
        .chart {
            background: white;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #E0E8E7;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .chart h3 {
            margin: 0 0 20px 0;
            color: #0F1419;
            text-align: center;
            font-size: 1.125rem;
            font-weight: 500;
        }
        
        .no-results {
            text-align: center;
            color: #4A4A4A;
            padding: 40px 20px;
            font-size: 1rem;
        }
        
        
        .footer {
            background: #F0F8F7;
            border-top: 1px solid #1A5A58;
            padding: 20px 30px;
            text-align: center;
            color: #4A4A4A;
            font-size: 0.9rem;
        }
        
        .footer a {
            color: #2B7A78;
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 16px;
            }
            
            .header {
                padding: 30px 20px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .tab-content {
                padding: 30px 20px;
            }
            
            .employee-grid {
                grid-template-columns: 1fr;
            }
            
            .chart-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """


def generate_header(employees: List[Dict[str, str]]) -> str:
    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    return f"""
        <div class="header">
            <h1>Employee Evaluation Report</h1>
            <p>Total Employees: {len(employees)}</p>
        </div>
    """


def generate_tabs() -> str:
    return """
        <div class="tabs">
            <button class="tab active" onclick="showTab('detailed')">Detailed View</button>
            <button class="tab" onclick="showTab('summary')">Summary Charts</button>
        </div>
    """


def generate_detailed_tab(employees: List[Dict[str, str]]) -> str:
    return f"""
        <div id="detailed" class="tab-content active">
            <div class="search-container">
                <input type="text" class="search-box" placeholder="Search by employee name..." onkeyup="filterEmployees()">
                <div class="search-icon">
                    <img src="https://img.icons8.com/?size=100&id=e4NkZ7kWAD7f&format=png&color=000000" alt="Search" style="width: 20px; height: 20px;">
                </div>
            </div>
            <div id="employee-list" class="employee-grid">
                {generate_employee_cards(employees)}
            </div>
        </div>
    """


def generate_summary_tab(employees: List[Dict[str, str]], all_fields: List[str]) -> str:
    return f"""
        <div id="summary" class="tab-content">
            <div class="chart-container">
                {generate_charts_html(all_fields)}
            </div>
        </div>
    """


def generate_footer() -> str:
    return """
        <div class="footer">
            <p>&copy; 2025 <a href="https://ennead-architects-llp.github.io/EnneadTabWiki/index.html" target="_blank">EnneadTab</a>. All rights reserved.</p>
            <p>Employee Evaluation Report System</p>
        </div>
    """


def generate_employee_cards(employees: List[Dict[str, str]]) -> str:
    """Generate HTML for employee cards from flat data."""
    cards_html = ""
    
    for employee in employees:
        name = employee.get('employee_name', 'Unknown')
        role = employee.get('employee_role', '')
        title = employee.get('title', '')
        email = employee.get('email', '')
        evaluator = employee.get('evaluator_name', '')
        date = employee.get('date_of_evaluation', '')
        submitted = employee.get('submitted', '')
        
        # Profile Image
        profile_image_html = ""
        profile_image = employee.get('profile_image', {})
        if isinstance(profile_image, dict) and profile_image.get('has_image'):
            image_path = profile_image.get('display_path', 'assets/images/default-avatar.png')
            profile_image_html = f'<img src="{image_path}" alt="{name}" class="profile-image">'
        else:
            # Generate initials for default avatar
            initials = ''.join([word[0].upper() for word in name.split()[:2]])
            profile_image_html = f'<div class="default-avatar">{initials}</div>'
        
        # Basic Information
        basic_info_html = ""
        if title:
            basic_info_html += f'<div class="field"><div class="field-label">Title</div><div class="field-value">{title}</div></div>'
        if role:
            basic_info_html += f'<div class="field"><div class="field-label">Role</div><div class="field-value">{role}</div></div>'
        if email:
            basic_info_html += f'<div class="field"><div class="field-label">Email</div><div class="field-value">{email}</div></div>'
        if evaluator:
            basic_info_html += f'<div class="field"><div class="field-label">Evaluator</div><div class="field-value">{evaluator}</div></div>'
        if submitted:
            basic_info_html += f'<div class="field"><div class="field-label">Submitted</div><div class="field-value">{submitted}</div></div>'
        
        # Performance Ratings
        ratings_html = ""
        rating_fields = ['Communication_rating', 'Collaboration_rating', 'Professionalism_rating', 
                        'Technical Knowledge & Expertise_rating', 'Workflow Implementation, Management, Execution_rating']
        
        for field in rating_fields:
            if field in employee and employee[field]:
                value = employee[field]
                if value and value != '0 (Not Applicable)':
                    clean_name = field.replace('_rating', ' Rating')
                    if '(' in value and ')' in value:
                        rating_num = value.split('(')[0].strip()
                        rating_desc = '(' + value.split('(')[1]
                        ratings_html += f'<div class="field"><div class="field-label">{clean_name}</div><div class="field-value"><span class="rating-number">{rating_num}</span><span class="rating-description">{rating_desc}</span></div></div>'
                    else:
                        ratings_html += f'<div class="field"><div class="field-label">{clean_name}</div><div class="field-value">{value}</div></div>'
        
        # Performance Comments
        comments_html = ""
        comment_fields = ['Communication_comments', 'Collaboration_comments', 'Professionalism_comments',
                         'Technical Knowledge & Expertise_comments', 'Workflow Implementation, Management, Execution_comments']
        
        for field in comment_fields:
            if field in employee and employee[field]:
                clean_name = field.replace('_comments', ' Comments').replace('_', ' ')
                comments_html += f'<div class="field"><div class="field-label">{clean_name}</div><div class="field-value">{employee[field]}</div></div>'
        
        # Overall Assessment
        overall_html = ""
        if employee.get('overall_performance'):
            overall_html += f'<div class="field"><div class="field-label">Overall Performance</div><div class="field-value">{employee["overall_performance"]}</div></div>'
        if employee.get('performance_examples'):
            overall_html += f'<div class="field"><div class="field-label">Performance Examples</div><div class="field-value">{employee["performance_examples"]}</div></div>'
        if employee.get('additional_resources'):
            overall_html += f'<div class="field"><div class="field-label">Additional Resources Needed</div><div class="field-value">{employee["additional_resources"]}</div></div>'
        
        # Employee Development
        development_html = ""
        if employee.get('employee_strengths'):
            development_html += f'<div class="field"><div class="field-label">Employee Strengths</div><div class="field-value">{employee["employee_strengths"]}</div></div>'
        if employee.get('areas_for_growth'):
            development_html += f'<div class="field"><div class="field-label">Areas for Growth & Development</div><div class="field-value">{employee["areas_for_growth"]}</div></div>'
        if employee.get('studio_culture_feedback'):
            development_html += f'<div class="field"><div class="field-label">Studio Culture Feedback</div><div class="field-value">{employee["studio_culture_feedback"]}</div></div>'
        
        # Software & Tools
        software_html = ""
        software_fields = ['revit', 'rhino', 'enscape', 'd5', 'vantage_point', 'deltek/adp', 'newforma', 
                          'bluebeam', 'grasshopper', 'word', 'powerpoint', 'excel', 'illustrator', 'photoshop', 'indesign']
        
        for field in software_fields:
            if field in employee and employee[field]:
                value = employee[field]
                if value and value != '0 (Not Applicable)':
                    clean_name = field.replace('_', ' ').title()
                    if '(' in value and ')' in value:
                        rating_num = value.split('(')[0].strip()
                        rating_desc = '(' + value.split('(')[1]
                        software_html += f'<div class="field"><div class="field-label">{clean_name}</div><div class="field-value"><span class="rating-number">{rating_num}</span><span class="rating-description">{rating_desc}</span></div></div>'
                    else:
                        software_html += f'<div class="field"><div class="field-label">{clean_name}</div><div class="field-value">{value}</div></div>'
        
        # Software Tools Feedback
        if employee.get('software_tools_feedback'):
            software_html += f'<div class="field"><div class="field-label">Software & Tools Feedback</div><div class="field-value">{employee["software_tools_feedback"]}</div></div>'
        
        card_html = f"""
        <div class="employee-card">
            <div class="employee-header">
                {profile_image_html}
                <div class="employee-info">
                    <div class="employee-name">{name}</div>
                    <div class="employee-time">{date}</div>
                </div>
            </div>
            <div class="fields-container">
                {f'<div class="field-group"><div class="group-title">Basic Information</div>{basic_info_html}</div>' if basic_info_html else ''}
                {f'<div class="field-group"><div class="group-title">Performance Ratings</div>{ratings_html}</div>' if ratings_html else ''}
                {f'<div class="field-group"><div class="group-title">Performance Comments</div>{comments_html}</div>' if comments_html else ''}
                {f'<div class="field-group"><div class="group-title">Overall Assessment</div>{overall_html}</div>' if overall_html else ''}
                {f'<div class="field-group"><div class="group-title">Employee Development</div>{development_html}</div>' if development_html else ''}
                {f'<div class="field-group"><div class="group-title">Software & Tools</div><div class="software-tools-grid">{software_html}</div></div>' if software_html else ''}
            </div>
        </div>
        """
        
        cards_html += card_html
    
    return cards_html


def generate_charts_html(all_fields: List[str]) -> str:
    """Generate HTML for charts."""
    charts_html = ""
    excluded_fields = get_excluded_chart_fields()
    
    for field in all_fields:
        if field.lower() not in excluded_fields:
            clean_name = field.replace('_', ' ').title()
            charts_html += f"""
        <div class="chart">
            <h3>{clean_name}</h3>
            <div style="position: relative; height: 300px;">
                <canvas id="chart-{field}"></canvas>
            </div>
        </div>
        """
    
    return charts_html


def generate_javascript_content(employees: List[Dict[str, str]], chart_data: Dict[str, Dict[str, int]]) -> str:
    """Generate JavaScript content for the website."""
    return f"""
// Employee Performance Review Website JavaScript

document.addEventListener('DOMContentLoaded', function() {{
    // Add smooth scrolling for any anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
        anchor.addEventListener('click', function (e) {{
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {{
                target.scrollIntoView({{
                    behavior: 'smooth'
                }});
            }}
        }});
    }});
    
    // Add animation on scroll
    const observerOptions = {{
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    }};
    
    const observer = new IntersectionObserver(function(entries) {{
        entries.forEach(entry => {{
            if (entry.isIntersecting) {{
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }}
        }});
    }}, observerOptions);
    
    // Observe employee cards for animation
    const employeeCards = document.querySelectorAll('.employee-card');
    employeeCards.forEach(card => {{
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    }});
    
    // Statistics
    console.log('Employee Performance Review Dashboard');
    console.log('Total Employees: {len(employees)}');
}});

// Utility functions
function scrollToTop() {{
    window.scrollTo({{
        top: 0,
        behavior: 'smooth'
    }});
}}

function downloadExcel() {{
    // Placeholder for Excel download functionality
    alert('Excel download functionality would be implemented here');
}}
"""


def generate_javascript(employees: List[Dict[str, str]], chart_data: Dict[str, Dict[str, int]]) -> str:
    """Generate JavaScript for the HTML template."""
    return f"""
    <script>
        const employees = {json.dumps(employees)};
        const chartData = {json.dumps(chart_data)};
        
        function showTab(tabName) {{
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
            
            // Initialize charts if summary tab is selected
            if (tabName === 'summary') {{
                setTimeout(initializeCharts, 100);
            }}
        }}
        
        function filterEmployees() {{
            const searchBox = document.querySelector('.search-box');
            const searchIcon = document.querySelector('.search-icon');
            const searchTerm = searchBox.value.toLowerCase();
            const employeeCards = document.querySelectorAll('.employee-card');
            
            // Show/hide search icon based on input content
            const searchIconImg = searchIcon.querySelector('img');
            if (searchTerm.length > 0) {{
                searchIcon.style.opacity = '0.3';
                searchIcon.style.animation = 'none';
                if (searchIconImg) {{
                    searchIconImg.style.filter = 'opacity(0.5)';
                }}
            }} else {{
                searchIcon.style.opacity = '0.5';
                searchIcon.style.animation = 'searchPulse 2s ease-in-out infinite';
                if (searchIconImg) {{
                    searchIconImg.style.filter = 'opacity(0.7)';
                }}
            }}
            
            employeeCards.forEach(card => {{
                const name = card.querySelector('.employee-name').textContent.toLowerCase();
                if (name.includes(searchTerm)) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
            
            // Show no results message if no cards are visible
            const visibleCards = Array.from(employeeCards).filter(card => card.style.display !== 'none');
            let noResults = document.getElementById('no-results');
            if (visibleCards.length === 0 && searchTerm) {{
                if (!noResults) {{
                    noResults = document.createElement('div');
                    noResults.id = 'no-results';
                    noResults.className = 'no-results';
                    noResults.innerHTML = `
                        <div class="no-results-message">
                            <div>No employees found matching "` + searchTerm + `"</div>
                            <div style="font-size: 0.9rem; margin-top: 8px; opacity: 0.7;">Try adjusting your search terms</div>
                        </div>
                    `;
                    document.getElementById('employee-list').appendChild(noResults);
                }}
            }} else if (noResults) {{
                noResults.remove();
            }}
        }}
        
        function initializeCharts() {{
            Object.keys(chartData).forEach(field => {{
                const canvas = document.getElementById(`chart-${{field}}`);
                if (canvas) {{
                    const ctx = canvas.getContext('2d');
                    const data = chartData[field];
                    
                    new Chart(ctx, {{
                        type: 'doughnut',
                        data: {{
                            labels: Object.keys(data),
                            datasets: [{{
                                data: Object.values(data),
                                backgroundColor: [
                                    'rgba(43, 122, 120, 0.8)',    // Primary teal
                                    'rgba(26, 90, 88, 0.8)',      // Darker teal
                                    'rgba(15, 20, 25, 0.8)',      // Dark text
                                    'rgba(58, 175, 169, 0.8)',    // Accent teal
                                    'rgba(74, 74, 74, 0.8)',      // Secondary text
                                    'rgba(240, 248, 247, 0.8)',   // Light background
                                    'rgba(224, 232, 231, 0.8)',   // Border color
                                    'rgba(43, 122, 120, 0.6)'     // Lighter primary
                                ],
                                borderColor: [
                                    'rgba(43, 122, 120, 1)',
                                    'rgba(26, 90, 88, 1)',
                                    'rgba(15, 20, 25, 1)',
                                    'rgba(58, 175, 169, 1)',
                                    'rgba(74, 74, 74, 1)',
                                    'rgba(240, 248, 247, 1)',
                                    'rgba(224, 232, 231, 1)',
                                    'rgba(43, 122, 120, 1)'
                                ],
                                borderWidth: 2,
                                hoverOffset: 10
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {{
                                legend: {{
                                    position: 'bottom',
                                    labels: {{
                                        padding: 20,
                                        usePointStyle: true,
                                        font: {{
                                            family: 'Inter',
                                            size: 12
                                        }}
                                    }}
                                }},
                                tooltip: {{
                                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                    titleColor: 'white',
                                    bodyColor: 'white',
                                    borderColor: 'rgba(255, 255, 255, 0.1)',
                                    borderWidth: 1,
                                    cornerRadius: 8,
                                    displayColors: true
                                }}
                            }},
                            cutout: '60%',
                            animation: {{
                                animateRotate: true,
                                animateScale: true,
                                duration: 1000,
                                easing: 'easeOutQuart'
                            }}
                        }}
                    }});
                }}
            }});
        }}
        
        // Return to top functionality
        function scrollToTop() {{
            window.scrollTo({{
                top: 0,
                behavior: 'smooth'
            }});
        }}
        
        // Show/hide return to top button based on scroll position
        window.addEventListener('scroll', function() {{
            const returnToTop = document.querySelector('.return-to-top');
            if (window.pageYOffset > 300) {{
                returnToTop.classList.add('show');
            }} else {{
                returnToTop.classList.remove('show');
            }}
        }});
    </script>
    """
