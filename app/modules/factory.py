"""
Factory Module

Factory functions for creating different types of reports and handling various formats.
"""

from typing import List, Dict, Optional
from enum import Enum

from .excel_generator import create_excel_output, export_to_csv
from .html_generator import create_html_output
from .utils import log_info, log_error


class ReportType(Enum):
    EXCEL = "excel"
    HTML = "html"
    CSV = "csv"
    ALL = "all"


class ReportFactory:
    @staticmethod
    def create_report(
        report_type: 'ReportType',
        employees: List[Dict[str, str]],
        all_fields: List[str],
        output_filename: Optional[str] = None
    ) -> str:
        if report_type == ReportType.EXCEL:
            return ReportFactory._create_excel_report(employees, all_fields, output_filename)
        elif report_type == ReportType.HTML:
            return ReportFactory._create_html_report(employees, all_fields, output_filename)
        elif report_type == ReportType.CSV:
            return ReportFactory._create_csv_report(employees, all_fields, output_filename)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")

    @staticmethod
    def _create_excel_report(
        employees: List[Dict[str, str]],
        all_fields: List[str],
        output_filename: Optional[str] = None
    ) -> str:
        filename = output_filename or "employee_evaluation.xlsx"
        log_info(f"Creating Excel report: {filename}")
        return create_excel_output(employees, all_fields, filename)

    @staticmethod
    def _create_html_report(
        employees: List[Dict[str, str]],
        all_fields: List[str],
        output_filename: Optional[str] = None
    ) -> str:
        filename = output_filename or "employee_evaluation.html"
        log_info(f"Creating HTML report: {filename}")
        return create_html_output(employees, all_fields, filename)

    @staticmethod
    def _create_csv_report(
        employees: List[Dict[str, str]],
        all_fields: List[str],
        output_filename: Optional[str] = None
    ) -> str:
        filename = output_filename or "employee_evaluation.csv"
        log_info(f"Creating CSV report: {filename}")
        return export_to_csv(employees, all_fields, filename)

    @staticmethod
    def create_all_reports(
        employees: List[Dict[str, str]],
        all_fields: List[str],
        base_filename: Optional[str] = None
    ) -> List[str]:
        base = base_filename or "employee_evaluation"
        created_files = []
        try:
            excel_path = ReportFactory._create_excel_report(employees, all_fields, f"{base}.xlsx")
            created_files.append(excel_path)
            html_path = ReportFactory._create_html_report(employees, all_fields, f"{base}.html")
            created_files.append(html_path)
            csv_path = ReportFactory._create_csv_report(employees, all_fields, f"{base}.csv")
            created_files.append(csv_path)
            log_info(f"Created {len(created_files)} report files")
            return created_files
        except Exception as e:
            log_error(f"Error creating reports: {e}")
            return created_files


def create_custom_report(
    report_type: str,
    employees: List[Dict[str, str]],
    all_fields: List[str],
    output_filename: Optional[str] = None
) -> str:
    try:
        report_enum = ReportType(report_type.lower())
        return ReportFactory.create_report(report_enum, employees, all_fields, output_filename)
    except ValueError:
        raise ValueError("Invalid report type: {report_type}. Valid types are: excel, html, csv")


def get_supported_formats() -> List[str]:
    return [report_type.value for report_type in ReportType if report_type != ReportType.ALL]
