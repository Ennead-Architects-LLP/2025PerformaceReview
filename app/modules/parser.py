"""
Employee Evaluation Data Parser

Parses survey response files and extracts employee evaluation data.
"""

import os
import re
import chardet
from typing import List, Dict, Tuple, Set
from .constants import get_data_source_path, is_data_source_available


def is_valid_survey_filename(filename: str) -> bool:
    pattern = r'^_\d{4}-\d{2}-\d{2}T\d{2}_\d{2}_\d{2}\.\d+Z\.txt$'
    return bool(re.match(pattern, filename))


def detect_file_encoding(filepath: str) -> str:
    try:
        with open(filepath, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result.get('encoding', 'utf-8')
            confidence = result.get('confidence', 0)
            if confidence < 0.7:
                encoding = 'utf-8'
            return encoding
    except Exception:
        return 'utf-8'


def read_file_with_encoding(filepath: str) -> str:
    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1', 'ascii']
    detected_encoding = detect_file_encoding(filepath)
    if detected_encoding and detected_encoding not in encodings_to_try:
        encodings_to_try.insert(0, detected_encoding)

    last_error = None
    for encoding in encodings_to_try:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError) as e:
            last_error = e
            continue
        except Exception as e:
            last_error = e
            continue
    raise UnicodeDecodeError('utf-8', b'', 0, 1, f"Unable to decode file. Last error: {last_error}")


def parse_input_files() -> Tuple[List[Dict[str, str]], List[str]]:
    employees: List[Dict[str, str]] = []
    all_fields: List[str] = []
    seen_fields: Set[str] = set()

    if is_data_source_available():
        data_source_dir = get_data_source_path()
        print(f"Using data source: {data_source_dir}")
    else:
        data_source_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Using local directory: {data_source_dir}")

    try:
        all_txt_files = [f for f in os.listdir(data_source_dir) if f.endswith('.txt')]
        input_files = [f for f in all_txt_files if is_valid_survey_filename(f)]
        if all_txt_files:
            print(f"Found {len(all_txt_files)} .txt files, {len(input_files)} valid survey files")
            if len(all_txt_files) > len(input_files):
                ignored_files = [f for f in all_txt_files if not is_valid_survey_filename(f)]
                print(f"Ignored files: {ignored_files[:5]}{'...' if len(ignored_files) > 5 else ''}")
    except Exception as e:
        print(f"Error accessing directory {data_source_dir}: {e}")
        return [], []

    for filename in sorted(input_files):
        filepath = os.path.join(data_source_dir, filename)
        try:
            employee_data = parse_survey_file(filepath)
            if employee_data and 'employee_name' in employee_data:
                employees.append(employee_data)
                for key in employee_data.keys():
                    if key not in seen_fields:
                        all_fields.append(key)
                        seen_fields.add(key)
        except Exception as e:
            print(f"Error parsing {filename}: {e}")

    return employees, all_fields


def parse_survey_file(filepath: str) -> Dict[str, str]:
    employee_data: Dict[str, str] = {}
    try:
        content = read_file_with_encoding(filepath).strip()
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                if 'Submitted:' in line:
                    employee_data['submitted'] = line.split('Submitted:')[1].strip()
                elif 'Responder:' in line:
                    employee_data['responder'] = line.split('Responder:')[1].strip()
                elif 'Employee Name:' in line:
                    employee_data['employee_name'] = line.split('Employee Name:')[1].strip()
                elif 'Date of Evaluation:' in line:
                    employee_data['date_of_evaluation'] = line.split('Date of Evaluation:')[1].strip()
                elif 'Employee Role:' in line:
                    employee_data['employee_role'] = line.split('Employee Role:')[1].strip()
                elif 'Overall Performance (stars 1–5):' in line:
                    employee_data['overall_performance'] = line.split('Overall Performance (stars 1–5):')[1].strip()
                elif ' – comments:' in line:
                    field_name = line.split(' – comments:')[0].strip()
                    comment_value = line.split(' – comments:')[1].strip()
                    employee_data[f"{field_name}_comments"] = comment_value
                elif ' (rating 1–5):' in line:
                    field_name = line.split(' (rating 1–5):')[0].strip()
                    rating_value = line.split(' (rating 1–5):')[1].strip()
                    employee_data[f"{field_name}_rating"] = rating_value
                elif ' (stars 1–5):' in line:
                    field_name = line.split(' (stars 1–5):')[0].strip()
                    star_value = line.split(' (stars 1–5):')[1].strip()
                    employee_data[f"{field_name}_stars"] = star_value
                elif ' (1–5):' in line:
                    field_name = line.split(' (1–5):')[0].strip()
                    rating_value = line.split(' (1–5):')[1].strip()
                    employee_data[f"{field_name}_rating"] = rating_value
                elif ' – overall comments:' in line:
                    field_name = line.split(' – overall comments:')[0].strip()
                    comment_value = line.split(' – overall comments:')[1].strip()
                    employee_data[f"{field_name}_overall_comments"] = comment_value
                elif ' (' in line and '):' in line:
                    field_name = line.split(' (')[0].strip()
                    value_part = line.split(' (')[1].split('):')[1].strip()
                    employee_data[field_name] = value_part
                else:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_').replace('–', '_').replace('&', 'and')
                    value = value.strip()
                    if value and value != 'N/A':
                        employee_data[key] = value
    except UnicodeDecodeError as e:
        print(f"Encoding error reading file {filepath}: {e}")
        return {}
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return {}
    return employee_data


def parse_single_file(filepath: str) -> Dict[str, str]:
    employee_data: Dict[str, str] = {}
    try:
        content = read_file_with_encoding(filepath).strip()
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line and not line.startswith('<'):
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                if key == 'name':
                    employee_data['name'] = value
                elif key == 'time':
                    employee_data['time'] = value
                else:
                    employee_data[key] = value
    except UnicodeDecodeError as e:
        print(f"Encoding error reading file {filepath}: {e}")
        return {}
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return {}
    return employee_data


def validate_employee_data(employee_data: Dict[str, str]) -> bool:
    return 'name' in employee_data and employee_data['name'].strip()


def get_employee_initials(name: str) -> str:
    return ''.join([word[0].upper() for word in name.split()[:2]])


def clean_field_name(field_name: str) -> str:
    return field_name.replace("_", " ").title()
