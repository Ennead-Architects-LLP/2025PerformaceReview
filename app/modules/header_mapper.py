"""
Header Mapping System

This module handles the mapping of Excel headers to structured data fields
with grouping and ordering capabilities for card display.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd


class CardGroup(Enum):
    """Card display groups in order of appearance."""
    BASIC_INFO = "basic_info"
    PERFORMANCE_RATINGS = "performance_ratings"
    PERFORMANCE_COMMENTS = "performance_comments"
    SOFTWARE_TOOLS = "software_tools"
    ADDITIONAL_DATA = "additional_data"
    EMPLOYEE_DEVELOPMENT = "employee_development"
    OVERALL_ASSESSMENT = "overall_assessment"


class CardType(Enum):
    """Types of data display in employee cards."""
    NOSHOW = "noshow"           # Don't show in cards
    RATING_NUM = "rating_num"    # Simple numeric rating (1-5)
    RATING_COMPLEX = "rating_complex"  # Complex rating with multiple aspects
    TEXT = "text"               # Single line text
    MULTILINE_TEXT = "multiline_text"  # Multi-line text/description


class ChartType(Enum):
    """Types of data display in charts."""
    NOSHOW = "noshow"           # Don't show in charts
    DONUT = "donut"             # Donut chart visualization
    PROGRESSION = "progression"  # Line chart showing growth over time


@dataclass
class HeaderMapping:
    """Mapping information for a single Excel header."""
    column_index: int  # Excel column number (0, 1, 2, etc.)
    column_letter: str  # Excel column letter (A, B, C, etc.)
    original_header: str  # Original header from Excel
    mapped_header: str  # Cleaned/standardized header name
    group_under: CardGroup  # Which card group this belongs to
    data_type_in_card: CardType  # How to display in cards
    data_type_in_chart: ChartType  # How to display in charts
    display_order: int  # Order within the group


class HeaderMapper:
    """Maps Excel headers to structured data fields with grouping."""
    
    def __init__(self):
        """Initialize the header mapper with default configurations."""
        self.header_mappings: Dict[int, HeaderMapping] = {}  # Key is column index (0, 1, 2, ...)
        self.header_mappings_by_name: Dict[str, HeaderMapping] = {}  # Key is original header name
        self.card_group_order: List[CardGroup] = [
            CardGroup.BASIC_INFO,
            CardGroup.PERFORMANCE_RATINGS,
            CardGroup.PERFORMANCE_COMMENTS,
            CardGroup.SOFTWARE_TOOLS,
            CardGroup.EMPLOYEE_DEVELOPMENT,
            CardGroup.OVERALL_ASSESSMENT,
            CardGroup.ADDITIONAL_DATA
        ]
        self._initialize_default_mappings()
    
    def _column_number_to_letter(self, col_num: int) -> str:
        """Convert column number (0-based) to Excel column letter."""
        result = ""
        while col_num >= 0:
            result = chr(65 + (col_num % 26)) + result
            col_num = col_num // 26 - 1
        return result
    
    def _initialize_default_mappings(self):
        """Initialize default header mappings based on common Excel structures.
        mn_index, original_header, mapped_header, group_under, data_type_in_card, data_type_in_chart, display_order, is_searchable"""
        
        # Basic Information Group (matching actual Excel column order)
        basic_mappings = [
            (0, "ID", "id", CardGroup.BASIC_INFO, CardType.NOSHOW, ChartType.NOSHOW, 1),
            (1, "Start time", "start_time", CardGroup.BASIC_INFO, CardType.NOSHOW, ChartType.NOSHOW, 6),
            (2, "Completion time", "completion_time", CardGroup.BASIC_INFO, CardType.NOSHOW, ChartType.NOSHOW, 7),
            (3, "Email", "email", CardGroup.BASIC_INFO, CardType.TEXT, ChartType.NOSHOW, 5),
            (4, "Name", "employee_name", CardGroup.BASIC_INFO, CardType.NOSHOW, ChartType.NOSHOW, 2),
            (5, "Last modified time", "last_modified", CardGroup.BASIC_INFO, CardType.NOSHOW, ChartType.NOSHOW, 10),
            (6, "Employee Name", "employee_name_alt", CardGroup.BASIC_INFO, CardType.NOSHOW, ChartType.NOSHOW, 11),  # Alternative name field
            (7, "Title", "title", CardGroup.BASIC_INFO, CardType.TEXT, ChartType.NOSHOW, 3),
            (8, "Role", "employee_role", CardGroup.BASIC_INFO, CardType.TEXT, ChartType.NOSHOW, 4),
            (9, "Date", "date_of_evaluation", CardGroup.BASIC_INFO, CardType.TEXT, ChartType.PROGRESSION, 8),
        ]
        
        # Performance Ratings Group (columns 9-13)
        rating_mappings = [
            (9, "Communication", "communication_rating", CardGroup.PERFORMANCE_RATINGS, CardType.RATING_NUM, ChartType.DONUT, 1),
            (10, "Collaboration", "collaboration_rating", CardGroup.PERFORMANCE_RATINGS, CardType.RATING_NUM, ChartType.DONUT, 2),
            (11, "Professionalism", "professionalism_rating", CardGroup.PERFORMANCE_RATINGS, CardType.RATING_NUM, ChartType.DONUT, 3),
            (12, "Technical Knowledge & Expertise", "technical_knowledge_expertise_rating", CardGroup.PERFORMANCE_RATINGS, CardType.RATING_NUM, ChartType.DONUT, 4),
            (13, "Workflow Implementation, Management, Execution", "workflow_implementation_management_execution_rating", CardGroup.PERFORMANCE_RATINGS, CardType.RATING_NUM, ChartType.DONUT, 5),
        ]
        
        # Performance Comments Group (columns 14-18)
        comment_mappings = [
            (14, "Communication2", "communication_comments", CardGroup.PERFORMANCE_COMMENTS, CardType.MULTILINE_TEXT, ChartType.NOSHOW, 1),
            (15, "Collaboration2", "collaboration_comments", CardGroup.PERFORMANCE_COMMENTS, CardType.MULTILINE_TEXT, ChartType.NOSHOW, 2),
            (16, "Professionalism2", "professionalism_comments", CardGroup.PERFORMANCE_COMMENTS, CardType.MULTILINE_TEXT, ChartType.NOSHOW, 3),
            (17, "Technical Knowledge & Expertise2", "technical_knowledge_expertise_comments", CardGroup.PERFORMANCE_COMMENTS, CardType.MULTILINE_TEXT, ChartType.NOSHOW, 4),
            (18, "Workflow Implementation, Management, Execution2", "workflow_implementation_management_execution_comments", CardGroup.PERFORMANCE_COMMENTS, CardType.MULTILINE_TEXT, ChartType.NOSHOW, 5),
        ]
        
        # Software Tools Group (columns 19-33)
        software_mappings = [
            (19, "Revit", "revit", CardGroup.SOFTWARE_TOOLS, CardType.RATING_NUM, ChartType.DONUT, 1),
            (20, "Rhino", "rhino", CardGroup.SOFTWARE_TOOLS, CardType.RATING_NUM, ChartType.DONUT, 2),
            (21, "Enscape", "enscape", CardGroup.SOFTWARE_TOOLS, CardType.RATING_NUM, ChartType.DONUT, 3),
            (22, "D5", "d5", CardGroup.SOFTWARE_TOOLS, CardType.RATING_NUM, ChartType.DONUT, 4),
            (23, "Vantage Point", "vantage_point", CardGroup.SOFTWARE_TOOLS, CardType.RATING_NUM, ChartType.DONUT, 5),
            (24, "Deltek/ADP", "deltek_adp", CardGroup.SOFTWARE_TOOLS, CardType.RATING_NUM, ChartType.DONUT, 6),
            (25, "Newforma", "newforma", CardGroup.SOFTWARE_TOOLS, CardType.RATING_NUM, ChartType.DONUT, 7),
            (26, "Bluebeam", "bluebeam", CardGroup.SOFTWARE_TOOLS, CardType.RATING_NUM, ChartType.DONUT, 8),
            (27, "Grasshopper", "grasshopper", CardGroup.SOFTWARE_TOOLS, CardType.RATING_NUM, ChartType.DONUT, 9),
            (28, "Word", "word", CardGroup.SOFTWARE_TOOLS, CardType.RATING_NUM, ChartType.DONUT, 10),
            (29, "Powerpoint", "powerpoint", CardGroup.SOFTWARE_TOOLS, CardType.RATING_NUM, ChartType.DONUT, 11),
            (30, "Excel", "excel", CardGroup.SOFTWARE_TOOLS, CardType.RATING_NUM, ChartType.DONUT, 12),
            (31, "Illustrator", "illustrator", CardGroup.SOFTWARE_TOOLS, CardType.RATING_NUM, ChartType.DONUT, 13),
            (32, "Photoshop", "photoshop", CardGroup.SOFTWARE_TOOLS, CardType.RATING_NUM, ChartType.DONUT, 14),
            (33, "Indesign", "indesign", CardGroup.SOFTWARE_TOOLS, CardType.RATING_NUM, ChartType.DONUT, 15),
        ]
        
        # Employee Development Group (columns 34-35)
        development_mappings = [
            (34, "Employee Strengths", "employee_strengths", CardGroup.EMPLOYEE_DEVELOPMENT, CardType.MULTILINE_TEXT, ChartType.NOSHOW, 1),
            (35, "Areas for Growth / Development Goals", "areas_for_growth", CardGroup.EMPLOYEE_DEVELOPMENT, CardType.MULTILINE_TEXT, ChartType.NOSHOW, 2),
        ]
        
        # Overall Assessment Group (columns 36-38)
        assessment_mappings = [
            (36, "Rate Your Overall Performance This Year", "overall_performance", CardGroup.OVERALL_ASSESSMENT, CardType.RATING_NUM, ChartType.DONUT, 1),
            (37, "Are there specific examples of your performance you'd like to share that weren't captured in earlier questions?", "performance_examples", CardGroup.OVERALL_ASSESSMENT, CardType.MULTILINE_TEXT, ChartType.NOSHOW, 2),
            (38, "What additional resources would help you do your job more effectively?", "additional_resources", CardGroup.OVERALL_ASSESSMENT, CardType.MULTILINE_TEXT, ChartType.NOSHOW, 3),
        ]
        
        # Additional Data Group (columns 39-40)
        additional_mappings = [
            (39, "Please share your thoughts about the character and culture of our studio and practice.", "studio_culture_feedback", CardGroup.ADDITIONAL_DATA, CardType.MULTILINE_TEXT, ChartType.NOSHOW, 1),
            (40, "Software & Tools2", "software_tools_feedback", CardGroup.ADDITIONAL_DATA, CardType.MULTILINE_TEXT, ChartType.NOSHOW, 2),
        ]
        
        # Combine all mappings
        all_mappings = (basic_mappings + rating_mappings + comment_mappings + 
                       software_mappings + development_mappings + assessment_mappings + 
                       additional_mappings)
        
        # Create HeaderMapping objects
        for mapping_data in all_mappings:
            if len(mapping_data) == 7:
                column_index, original_header, mapped_header, group_under, data_type_in_card, data_type_in_chart, display_order = mapping_data
            else:
                print(f"Warning: Invalid mapping data length {len(mapping_data)} for {mapping_data}")
                continue
                
            column_letter = self._column_number_to_letter(column_index)
            
            mapping = HeaderMapping(
                column_index=column_index,
                column_letter=column_letter,
                original_header=original_header,
                mapped_header=mapped_header,
                group_under=group_under,
                data_type_in_card=data_type_in_card,
                data_type_in_chart=data_type_in_chart,
                display_order=display_order
            )
            
            # Store by numeric index (primary key) and by name (for lookup)
            self.header_mappings[column_index] = mapping
            self.header_mappings_by_name[original_header] = mapping
    
    def map_excel_headers(self, df: pd.DataFrame) -> Dict[int, HeaderMapping]:
        """
        Map actual Excel headers to our predefined mappings using column indices.
        Handles duplicate column names by preferring numeric data over text data.

        Args:
            df: Pandas DataFrame from Excel file

        Returns:
            Dictionary mapping column indices to HeaderMapping objects
        """
        actual_mappings = {}

        # First pass: exact matches
        for col_index, actual_header in enumerate(df.columns):
            if actual_header in self.header_mappings_by_name:
                mapping = self.header_mappings_by_name[actual_header]
                mapping.column_index = col_index
                mapping.column_letter = self._column_number_to_letter(col_index)
                actual_mappings[col_index] = mapping

        # Second pass: fuzzy matches with conflict resolution
        for col_index, actual_header in enumerate(df.columns):
            # Skip if already mapped
            if col_index in actual_mappings:
                continue

            # Try fuzzy matching
            best_match = None
            best_score = 0

            for predefined_mapping in self.header_mappings.values():
                similarity = self._calculate_similarity(actual_header, predefined_mapping.original_header)
                if similarity > best_score and similarity > 0.7:
                    best_score = similarity
                    best_match = predefined_mapping

            if best_match:
                # Check for conflicts with existing mappings
                existing_mapping = self._find_existing_mapping_for_field(actual_mappings, best_match.mapped_header)
                if existing_mapping:
                    # Resolve conflict by preferring numeric data over text data
                    should_replace = self._should_replace_mapping(df, existing_mapping, col_index, actual_header, best_match)
                    if should_replace:
                        # Remove the old mapping
                        old_col_index = None
                        for col_idx, mapping in actual_mappings.items():
                            if mapping.mapped_header == best_match.mapped_header:
                                old_col_index = col_idx
                                break
                        if old_col_index is not None:
                            del actual_mappings[old_col_index]
                    else:
                        # Don't add the new mapping, keep the existing one
                        continue

                actual_mappings[col_index] = HeaderMapping(
                    column_index=col_index,
                    column_letter=self._column_number_to_letter(col_index),
                    original_header=actual_header,
                    mapped_header=best_match.mapped_header,
                    group_under=best_match.group_under,
                    data_type_in_card=best_match.data_type_in_card,
                    data_type_in_chart=best_match.data_type_in_chart,
                    display_order=best_match.display_order
                )
            else:
                # Create default mapping for unknown headers
                actual_mappings[col_index] = HeaderMapping(
                    column_index=col_index,
                    column_letter=self._column_number_to_letter(col_index),
                    original_header=actual_header,
                    mapped_header=self._clean_header_name(actual_header),
                    group_under=CardGroup.ADDITIONAL_DATA,
                    data_type_in_card=CardType.TEXT,
                    data_type_in_chart=ChartType.NOSHOW,
                    display_order=999
                )

        return actual_mappings

    def _find_existing_mapping_for_field(self, mappings: Dict[int, HeaderMapping], target_field: str) -> Optional[HeaderMapping]:
        """Find existing mapping for a target field."""
        for mapping in mappings.values():
            if mapping.mapped_header == target_field:
                return mapping
        return None

    def _should_replace_mapping(self, df: pd.DataFrame, existing_mapping: HeaderMapping,
                               new_col_index: int, new_header: str, predefined_mapping) -> bool:
        """
        Determine if a new mapping should replace an existing one.
        Prefers numeric data over text data for the same field.
        """
        # Get sample values from both columns
        try:
            existing_value = df.iloc[0][existing_mapping.original_header]
            new_value = df.iloc[0][new_header]
        except (KeyError, IndexError):
            return True  # Replace if we can't get sample values

        # Check if values are numeric
        existing_is_numeric = self._is_numeric_value(existing_value)
        new_is_numeric = self._is_numeric_value(new_value)

        # If the new column has numeric data and existing doesn't, replace
        if new_is_numeric and not existing_is_numeric:
            return True

        # If both are numeric or both are text, keep the existing one (first match wins)
        return False

    def _is_numeric_value(self, value) -> bool:
        """Check if a value is numeric (indicating it's likely a rating)."""
        if pd.isna(value):
            return False
        try:
            int(str(value).strip())
            return True
        except (ValueError, TypeError):
            return False
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings."""
        if not str1 or not str2:
            return 0.0
        
        str1_lower = str1.lower().strip()
        str2_lower = str2.lower().strip()
        
        if str1_lower == str2_lower:
            return 1.0
        
        # Check if one contains the other
        if str1_lower in str2_lower or str2_lower in str1_lower:
            return 0.8
        
        # Simple word overlap
        words1 = set(str1_lower.split())
        words2 = set(str2_lower.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _clean_header_name(self, header: str) -> str:
        """Clean header name for use as field name."""
        import re
        cleaned = re.sub(r'\n+', ' ', str(header))
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = cleaned.lower()
        cleaned = re.sub(r'[^a-z0-9\s]', '', cleaned)
        cleaned = re.sub(r'\s+', '_', cleaned)
        return cleaned
    
    def get_grouped_fields(self, mappings: Dict[int, HeaderMapping]) -> Dict[CardGroup, List[HeaderMapping]]:
        """
        Group fields by their card group.
        
        Args:
            mappings: Dictionary of header mappings (keyed by column index)
            
        Returns:
            Dictionary grouped by CardGroup
        """
        grouped = {}
        
        for mapping in mappings.values():
            group = mapping.group_under
            if group not in grouped:
                grouped[group] = []
            grouped[group].append(mapping)
        
        # Sort each group by display_order
        for group in grouped:
            grouped[group].sort(key=lambda x: x.display_order)
        
        return grouped
    
    def get_visible_fields(self, mappings: Dict[int, HeaderMapping]) -> List[HeaderMapping]:
        """Get only visible fields in card group order."""
        visible_fields = []
        
        for group in self.card_group_order:
            group_fields = [m for m in mappings.values() 
                          if m.group_under == group and m.data_type_in_card != CardType.NOSHOW]
            group_fields.sort(key=lambda x: x.display_order)
            visible_fields.extend(group_fields)
        
        return visible_fields
    
    def update_card_group_order(self, new_order: List[CardGroup]):
        """Update the card group display order."""
        self.card_group_order = new_order
    
    def hide_field(self, original_header: str):
        """Hide a field from display by setting CardType to NOSHOW."""
        if original_header in self.header_mappings_by_name:
            self.header_mappings_by_name[original_header].data_type_in_card = CardType.NOSHOW
    
    def show_field(self, original_header: str, card_type: CardType = CardType.TEXT):
        """Show a field in display by setting CardType."""
        if original_header in self.header_mappings_by_name:
            self.header_mappings_by_name[original_header].data_type_in_card = card_type
    
    def get_mapping_summary(self) -> Dict[str, Any]:
        """Get a summary of all mappings for inspection."""
        summary = {
            "total_mappings": len(self.header_mappings),
            "card_group_order": [group.value for group in self.card_group_order],
            "groups": {},
            "ordered_mappings": []  # All mappings ordered by column index
        }
        
        # Create ordered mappings by column index
        for col_index in sorted(self.header_mappings.keys()):
            mapping = self.header_mappings[col_index]
            summary["ordered_mappings"].append({
                "column_index": mapping.column_index,
                "column_letter": mapping.column_letter,
                "original_header": mapping.original_header,
                "mapped_header": mapping.mapped_header,
                "group_under": mapping.group_under.value,
                "data_type_in_card": mapping.data_type_in_card.value,
                "data_type_in_chart": mapping.data_type_in_chart.value,
                "display_order": mapping.display_order
            })
        
        for group in CardGroup:
            group_mappings = [m for m in self.header_mappings.values() 
                            if m.group_under == group]
            summary["groups"][group.value] = {
                "count": len(group_mappings),
                "fields": [
                    {
                        "column_index": m.column_index,
                        "column_letter": m.column_letter,
                        "original_header": m.original_header,
                        "mapped_header": m.mapped_header,
                        "data_type_in_card": m.data_type_in_card.value,
                        "data_type_in_chart": m.data_type_in_chart.value,
                        "display_order": m.display_order
                    }
                    for m in sorted(group_mappings, key=lambda x: x.display_order)
                ]
            }
        
        return summary


# Global instance for easy access
header_mapper = HeaderMapper()
