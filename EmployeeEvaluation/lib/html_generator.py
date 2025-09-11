"""
HTML Report Generator

This module handles the generation of interactive HTML reports from employee evaluation data.
"""

import os
import json
from collections import defaultdict, Counter
from typing import List, Dict
from parser import get_employee_initials, clean_field_name


def get_excluded_chart_fields() -> set:
    """
    Get the set of fields that should be excluded from chart generation.
    These are comment fields and evaluator name that contain customized text.
    
    Returns:
        Set of field names to exclude from charts
    """
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
        'technical knowledge & expertise_comments'
    }


def create_html_output(employees: List[Dict[str, str]], all_fields: List[str], output_filename: str = 'OUTPUT.html') -> str:
    """
    Create interactive HTML report.
    
    Args:
        employees: List of employee dictionaries
        all_fields: List of all field names
        output_filename: Name of the output HTML file
        
    Returns:
        Path to the created HTML file
    """
    # Prepare data for charts
    chart_data = prepare_chart_data(employees, all_fields)
    
    # Generate HTML content
    html_content = generate_html_template(employees, all_fields, chart_data)
    
    # Write to docs folder for GitHub Pages
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(project_root, 'docs')
    output_path = os.path.join(docs_dir, f"_EvaluationSummary.html")

    # Ensure docs directory exists
    os.makedirs(docs_dir, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML file created: {output_path}")
    return output_path


def prepare_chart_data(employees: List[Dict[str, str]], all_fields: List[str]) -> Dict[str, Dict[str, int]]:
    """
    Prepare chart data by counting field values.
    Excludes comment fields and evaluator name as they contain customized text.
    
    Args:
        employees: List of employee dictionaries
        all_fields: List of all field names
        
    Returns:
        Dictionary containing chart data for each field
    """
    # Fields to exclude from charts (comment fields and evaluator name)
    excluded_fields = get_excluded_chart_fields()
    
    # Log excluded fields for transparency
    excluded_from_charts = [field for field in all_fields if any(excluded.lower() in field.lower() or field.lower() in excluded.lower() for excluded in excluded_fields)]
    if excluded_from_charts:
        print(f"Excluding from charts: {excluded_from_charts}")
    
    field_value_counts = defaultdict(Counter)
    
    for emp in employees:
        for field in all_fields:
            # Skip excluded fields (case-insensitive partial matching)
            if any(excluded.lower() in field.lower() or field.lower() in excluded.lower() for excluded in excluded_fields):
                continue
                
            if field in emp and emp[field]:
                field_value_counts[field][emp[field]] += 1
    
    # Convert to regular dictionaries
    chart_data = {}
    for field, counter in field_value_counts.items():
        chart_data[field] = dict(counter)
    
    return chart_data


def generate_html_template(employees: List[Dict[str, str]], all_fields: List[str], chart_data: Dict[str, Dict[str, int]]) -> str:
    """
    Generate the complete HTML template.
    
    Args:
        employees: List of employee dictionaries
        all_fields: List of all field names
        chart_data: Dictionary containing chart data
        
    Returns:
        Complete HTML content as string
    """
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
    
    <button class="return-to-top" onclick="scrollToTop()" title="Return to top">
        ↑
    </button>
    {generate_javascript(employees, chart_data)}
</body>
</html>
"""


def get_css_styles() -> str:
    """Get the CSS styles for the HTML template."""
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

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            z-index: 1;
        }

        .header-text {
            flex: 1;
        }

        .header-actions {
            display: flex;
            gap: 16px;
        }

        .download-btn {
            background: linear-gradient(135deg, #16b981 0%, #059669 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 12px rgba(22, 185, 129, 0.3);
            position: relative;
            z-index: 2;
        }

        .download-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(22, 185, 129, 0.4);
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
        }

        .download-btn:active {
            transform: translateY(0);
        }

        .btn-icon {
            font-size: 1.2rem;
        }

        .excel-btn {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }

        .excel-btn:hover {
            background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
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
        
        .employee-name {
            font-size: 1.25rem;
            font-weight: 500;
            color: #0F1419;
            margin-bottom: 12px;
        }
        
        .employee-time {
            color: #4A4A4A;
            font-size: 0.875rem;
            margin-bottom: 20px;
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
    """Generate the header section."""
    return f"""
        <div class="header">
            <div class="header-content">
                <div class="header-text">
                    <h1>Employee Evaluation Report</h1>
                    <p>Total Employees: {len(employees)}</p>
                </div>
                <div class="header-actions">
                    <button class="download-btn excel-btn" onclick="downloadExcel()">
                        <span class="btn-icon">📊</span>
                        Download Excel
                    </button>
                </div>
            </div>
        </div>
    """


def generate_tabs() -> str:
    """Generate the tabs navigation."""
    return """
        <div class="tabs">
            <button class="tab active" onclick="showTab('detailed')">Detailed View</button>
            <button class="tab" onclick="showTab('summary')">Summary Charts</button>
        </div>
    """


def generate_detailed_tab(employees: List[Dict[str, str]]) -> str:
    """Generate the detailed view tab."""
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
    """Generate the summary charts tab."""
    return f"""
        <div id="summary" class="tab-content">
            <div class="chart-container">
                {generate_charts_html(all_fields)}
            </div>
        </div>
    """


def generate_footer() -> str:
    """Generate the footer section with copyright notice."""
    return """
        <div class="footer">
            <p>&copy; 2025 <a href="https://ennead-architects-llp.github.io/EnneadTabWiki/index.html" target="_blank">EnneadTab</a>. All rights reserved.</p>
            <p>Employee Evaluation Report System</p>
        </div>
    """


def generate_employee_cards(employees: List[Dict[str, str]]) -> str:
    """Generate HTML for employee cards with grouped fields."""
    cards_html = ""
    for emp in employees:
        name = emp.get('employee_name', emp.get('name', 'Unknown'))
        date = emp.get('date_of_evaluation', emp.get('time', ''))
        initials = get_employee_initials(name)
        
        cards_html += f'<div class="employee-card">'
        cards_html += f'<div class="employee-name">{name}</div>'
        
        if date:
            cards_html += f'<div class="employee-time">{date}</div>'
        
        # Group fields logically
        cards_html += f'<div class="fields-container">'
        
        # 1. Basic Information Group
        basic_info = ['employee_role', 'evaluator_name']
        cards_html += _generate_field_group(emp, basic_info, "Basic Information")
        
        # 2. Performance Ratings Group
        rating_fields = [key for key in emp.keys() if key.endswith('_rating') and key not in ['overall_performance']]
        cards_html += _generate_field_group(emp, rating_fields, "Performance Ratings")
        
        # 3. Overall Assessment Group
        overall_fields = ['overall_performance', 'employee_strengths', 'employee_areas_for_growth_&_development', 'additional_comments_regarding_performance']
        cards_html += _generate_field_group(emp, overall_fields, "Overall Assessment")
        
        # 4. Software & Tools Group
        software_fields = [key for key in emp.keys() if key in ['revit', 'rhino', 'enscape', 'd5', 'vantage_point', 'deltek/adp', 'newforma', 'bluebeam', 'grasshopper', 'word', 'powerpoint', 'excel', 'illustrator', 'photoshop', 'indesign']]
        if software_fields:
            cards_html += _generate_field_group(emp, software_fields, "Software & Tools")
        
        # 5. Comments Group
        comment_fields = [key for key in emp.keys() if key.endswith('_comments') or key == 'software_&_tools_overall_comments']
        cards_html += _generate_field_group(emp, comment_fields, "Comments & Feedback")
        
        cards_html += f'</div>'
        cards_html += '</div>'
    
    return cards_html


def _generate_field_group(emp: Dict[str, str], fields: List[str], group_title: str) -> str:
    """Generate HTML for a group of related fields."""
    # Filter fields that exist and have values
    valid_fields = [field for field in fields if field in emp and emp[field] and emp[field].strip()]
    
    if not valid_fields:
        return ""
    
    # Check if this is the Software & Tools group for special layout
    is_software_tools = group_title.lower() == "software & tools"
    
    group_html = f'<div class="field-group">'
    group_html += f'<div class="group-title">{group_title}</div>'
    
    if is_software_tools:
        # Use two-column grid layout for Software & Tools
        group_html += f'<div class="software-tools-grid">'
        for field in valid_fields:
            group_html += f'<div class="field">'
            group_html += f'<div class="field-label">{clean_field_name(field)}</div>'
            
            # Parse rating value to separate number and description
            field_value = emp[field]
            if '(' in field_value and ')' in field_value:
                # Extract number and description from format like "3 (Meets Expectations)"
                parts = field_value.split('(', 1)
                if len(parts) == 2:
                    number = parts[0].strip()
                    description = '(' + parts[1].strip()
                    group_html += f'<div class="field-value">'
                    group_html += f'<span class="rating-number">{number}</span>'
                    group_html += f'<span class="rating-description">{description}</span>'
                    group_html += f'</div>'
                else:
                    group_html += f'<div class="field-value">{field_value}</div>'
            else:
                group_html += f'<div class="field-value">{field_value}</div>'
            
            group_html += f'</div>'
        group_html += f'</div>'
    else:
        # Use regular single-column layout for other groups
        for field in valid_fields:
            group_html += f'<div class="field">'
            group_html += f'<div class="field-label">{clean_field_name(field)}</div>'
            
            # Parse rating value to separate number and description for all groups
            field_value = emp[field]
            if '(' in field_value and ')' in field_value:
                # Extract number and description from format like "3 (Meets Expectations)"
                parts = field_value.split('(', 1)
                if len(parts) == 2:
                    number = parts[0].strip()
                    description = '(' + parts[1].strip()
                    group_html += f'<div class="field-value">'
                    group_html += f'<span class="rating-number">{number}</span>'
                    group_html += f'<span class="rating-description">{description}</span>'
                    group_html += f'</div>'
                else:
                    group_html += f'<div class="field-value">{field_value}</div>'
            else:
                group_html += f'<div class="field-value">{field_value}</div>'
            
            group_html += f'</div>'
    
    group_html += f'</div>'
    return group_html


def generate_charts_html(all_fields: List[str]) -> str:
    """Generate HTML for chart containers, excluding comment fields."""
    # Fields to exclude from charts (comment fields and evaluator name)
    excluded_fields = get_excluded_chart_fields()
    
    charts_html = ""
    for field in all_fields:
        # Skip excluded fields (case-insensitive partial matching)
        if any(excluded.lower() in field.lower() or field.lower() in excluded.lower() for excluded in excluded_fields):
            continue
            
        charts_html += f'''
        <div class="chart">
            <h3>{clean_field_name(field)}</h3>
            <div style="position: relative; height: 300px;">
                <canvas id="chart-{field}"></canvas>
            </div>
        </div>
        '''
    return charts_html


def generate_javascript(employees: List[Dict[str, str]], chart_data: Dict[str, Dict[str, int]]) -> str:
    """Generate the JavaScript code for interactivity."""
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

        // Download Excel file function
        function downloadExcel() {{
            const link = document.createElement('a');
            link.href = '_EvaluationSummary.xlsx';
            link.download = '_EvaluationSummary.xlsx';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }}
    </script>
    """
