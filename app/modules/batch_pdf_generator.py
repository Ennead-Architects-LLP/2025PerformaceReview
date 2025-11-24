"""
Batch PDF Generator for Evaluator-Employee Reviews

This module handles batch generation of PDFs from Excel files containing
evaluator-employee pairs. Each PDF displays both evaluator and employee profile images.
"""

import os
import sys
from typing import List, Dict, Any, Callable, Optional, Tuple

# Fix console encoding for Windows (safe)
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from .config import Config
from .excel_parser import ExcelEmployeeParser
from .image_manager import ImageManager
import pandas as pd

# PIL imports for circular image processing
try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def _safe_filename(name: str) -> str:
    """Return a filesystem-safe filename (letters/digits/dash/dot only)."""
    import re
    return re.sub(r"[^\w\-\.]+", "_", str(name))[:80] or "Unknown"


def _get_display_label(field_name: str) -> str:
    """Convert field name to a clean, readable display label.
    
    Maps long/technical field names to shorter, professional labels.
    """
    # Mapping of long field names to clean labels
    label_mapping = {
        # Long question fields
        "are_there_specific_examples_of_the_employees_performance_youd_like_to_share_that_werent_captured_in_earlier_questions": "Specific Performance Examples",
        "are_there_specific_examples_of_the_employees_performance_youd_like_to_share_that_werent_captured_in_earlier": "Specific Performance Examples",
        "rate_the_employees_overall_performance_this_year": "Overall Performance Rating",
        "what_additional_resources_would_help_you_do_your_job_more_effectively": "Additional Resources Needed",
        "please_share_your_thoughts_about_the_character_and_culture_of_our_studio_and_practice": "Studio Culture & Practice Thoughts",
        
        # Other long fields
        "workflow_implementation_management_execution_ratingprojects_proposals_employee_relations_accounting_marketing_it_technology_and_office": "Workflow Implementation Rating",
        "workflow_implementation_management_execution_comments": "Workflow Implementation Comments",
        "technical_knowledge_expertise_rating": "Technical Knowledge & Expertise Rating",
        "technical_knowledge_expertise_comments": "Technical Knowledge & Expertise Comments",
    }
    
    # Normalize field name for lookup
    normalized = str(field_name).strip().lower().replace('\xa0', ' ').replace('\n', ' ')
    normalized = normalized.replace(' ', '_').replace('-', '_')
    
    # Check exact match first
    if normalized in label_mapping:
        return label_mapping[normalized]
    
    # Check partial matches for long question fields
    if "specific_examples" in normalized and "performance" in normalized:
        return "Specific Performance Examples"
    if "rate" in normalized and "overall_performance" in normalized:
        return "Overall Performance Rating"
    if "additional_resources" in normalized:
        return "Additional Resources Needed"
    if "character_and_culture" in normalized or "studio_and_practice" in normalized:
        return "Studio Culture & Practice Thoughts"
    
    # Default: clean up the field name
    label = str(field_name).strip()
    # Replace underscores and dashes with spaces
    label = label.replace('_', ' ').replace('-', ' ')
    # Remove extra whitespace
    label = ' '.join(label.split())
    # Title case
    label = label.title()
    
    # Truncate very long labels (but keep important words)
    if len(label) > 60:
        # Try to keep first part if it's meaningful
        words = label.split()
        if len(words) > 8:
            # Keep first 6-8 words
            label = ' '.join(words[:8]) + "..."
    
    return label


def _format_date_only(val) -> str:
    """Format many possible date/time inputs to ISO date (YYYY-MM-DD)."""
    try:
        import datetime as _dt
        if isinstance(val, (_dt.datetime, _dt.date)):
            return val.date().isoformat() if isinstance(val, _dt.datetime) else val.isoformat()
    except Exception:
        pass
    s = str(val)
    if 'T' in s:
        s = s.split('T')[0]
    if ' ' in s:
        s = s.split(' ')[0]
    try:
        import pandas as _pd
        parsed = _pd.to_datetime(val, errors='coerce')
        if parsed is not None and not _pd.isna(parsed):
            return parsed.date().isoformat()
    except Exception:
        pass
    return s[:10]


def _find_name_field(data: Dict[str, Any], field_keywords: List[str]) -> Optional[str]:
    """Find a name field in data dictionary using keywords.
    
    Args:
        data: Dictionary with field names as keys
        field_keywords: List of keywords to search for in field names
        
    Returns:
        First matching value found, or None
    """
    # Normalize keywords to lowercase
    keywords_lower = [kw.lower() for kw in field_keywords]
    
    # Try to find matching field
    for key, value in data.items():
        if not value:
            continue
        key_lower = key.lower()
        # Check if any keyword matches (exact or partial)
        for keyword in keywords_lower:
            if keyword == key_lower or keyword in key_lower:
                val_str = str(value).strip()
                if val_str:
                    return val_str
    return None


def _get_image_path(name: str, image_manager: ImageManager, name_to_image: Dict[str, str]) -> Optional[str]:
    """Get image path for a name, using image_manager or existing mappings."""
    # First check existing mappings
    if name in name_to_image:
        img_path = name_to_image[name]
        if img_path and os.path.exists(img_path):
            return img_path
    
    # Try to find using image manager
    if name:
        best_match, confidence = image_manager.find_best_image_match(name, threshold=70)
        if best_match:
            img_path = os.path.join(image_manager.target_dir, best_match)
            if os.path.exists(img_path):
                return img_path
    
    return None


def export_batch_pdfs_with_dual_images(
    excel_path: str,
    export_dir: str,
    log_func: Callable[[str], None],
) -> str:
    """Export PDFs for evaluator-employee pairs with dual images in header.
    
    Args:
        excel_path: Path to Excel file with evaluator-employee data
        export_dir: Directory to save PDFs
        log_func: Function to log progress messages
        
    Returns:
        Path to export directory if successful, empty string otherwise
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from reportlab.lib.utils import simpleSplit
        from .header_mapper import CardGroup
    except Exception as e:
        log_func(f"ReportLab not available: {e}")
        return ""

    # Parse Excel file
    log_func("Loading Excel file...")
    parser = ExcelEmployeeParser(excel_path)
    if not parser.load_excel():
        log_func("Failed to load Excel file")
        return ""
    
    employees_data = parser.parse_all_employees_as_dicts()
    if not employees_data:
        log_func("No employee data found in Excel file")
        return ""
    
    log_func(f"Found {len(employees_data)} rows to process")
    
    # Setup image manager
    image_source_dir = Config.get_image_source_path()
    image_target_dir = Config.get_image_target_path()
    image_manager = ImageManager(image_source_dir, image_target_dir)
    image_manager.setup_directories()
    image_manager.scan_source_images()
    
    # Load existing image mappings
    name_to_image = {}
    try:
        import json as _json
        with open(Config.get_image_mappings_path(), 'r', encoding='utf-8') as f:
            data = _json.load(f)
        for name, info in data.items():
            if info.get('filename') and info.get('copied'):
                name_to_image[name] = os.path.join(Config.get_image_target_path(), info['filename'])
    except Exception:
        pass
    
    # Rating icon asset paths
    rating_checked_path = os.path.join(Config.get_assets_dir_path(), 'icons', 'rating_checked.png')
    rating_unchecked_path = os.path.join(Config.get_assets_dir_path(), 'icons', 'rating_unchecked.png')
    
    def _rgb(hex_color: str):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))
    
    TEAL = _rgb('2B7A78')
    BOX_BG = _rgb('F7FBFA')
    
    # Precompute grouping from header_mappings
    group_to_fields = {}
    group_order = []
    header_mappings = parser.header_mappings
    if header_mappings:
        for _idx, m in header_mappings.items():
            grp = m.group_under
            if grp not in group_to_fields:
                group_to_fields[grp] = []
                group_order.append(grp)
            group_to_fields[grp].append(m)
        for grp in group_to_fields:
            group_to_fields[grp] = sorted(group_to_fields[grp], key=lambda m: m.display_order)
    
    os.makedirs(export_dir, exist_ok=True)
    
    # Process each row (evaluator-employee pair)
    # Access raw Excel data to get "Evaluator Name" column which may not be in mapped data
    df = parser.df
    processed_count = 0
    
    for idx, emp_data in enumerate(employees_data):
        try:
            # Get evaluator and employee names from raw Excel data
            # Column E (index 4): "Name" = Evaluator Name
            # Column 7: "Employee Name\xa0" (mapped as "Employee Name Alt") = Employee Name
            evaluator_name = None
            employee_name = None
            
            # Get evaluator name from column E (index 4) - "Name" field
            if df is not None and idx < len(df):
                try:
                    # Column E (index 4) is "Name" which refers to the Evaluator
                    evaluator_name_raw = df.iloc[idx, 4]
                    if pd.notna(evaluator_name_raw):
                        evaluator_name = str(evaluator_name_raw).strip()
                except (IndexError, KeyError):
                    pass
            
            # Fallback: try column 6 "Evaluator Name" if column E didn't work
            if not evaluator_name and df is not None and idx < len(df):
                try:
                    evaluator_name_raw = df.iloc[idx, 6]
                    if pd.notna(evaluator_name_raw):
                        evaluator_name = str(evaluator_name_raw).strip()
                except (IndexError, KeyError):
                    pass
            
            # Get employee name from mapped data (column 7 -> "Employee Name Alt")
            employee_name = emp_data.get('Employee Name Alt') or emp_data.get('Employee Name')
            
            # Additional fallback: try to find in mapped data if raw access didn't work
            if not evaluator_name:
                evaluator_name = _find_name_field(emp_data, ['evaluator name', 'evaluator_name', 'name'])
            
            if not employee_name:
                employee_name = _find_name_field(emp_data, ['employee name', 'employee_name'])
            
            if not evaluator_name:
                log_func(f"Row {idx + 1}: Skipping - no evaluator name found")
                continue
            if not employee_name:
                log_func(f"Row {idx + 1}: Skipping - no employee name found")
                continue
            
            log_func(f"Processing: {evaluator_name} -> {employee_name}")
            
            # Get image paths
            employee_img_path = _get_image_path(employee_name, image_manager, name_to_image)
            evaluator_img_path = _get_image_path(evaluator_name, image_manager, name_to_image)
            
            # Create PDF filename
            safe_evaluator = _safe_filename(evaluator_name)
            safe_employee = _safe_filename(employee_name)
            pdf_filename = f"{safe_evaluator}_{safe_employee}_Review.pdf"
            pdf_path = os.path.join(export_dir, pdf_filename)
            
            # Create PDF
            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter
            
            # Header setup - dual images side by side (employee left, evaluator right)
            header_y = height - 0.75*inch
            img_size = 0.9*inch
            left_margin = 0.75*inch
            spacing = 1.0*inch  # Space between images (increased significantly for clear separation)
            name_gap = 0.2*inch  # Gap between image and name (increased further to prevent overlap)
            circle_border_width = 2  # Border width for circular images
            
            # Helper function to draw circular image with visible border
            def draw_circular_image(img_path, x, y, size):
                """Draw an image with a circular mask and visible border."""
                if PIL_AVAILABLE:
                    try:
                        from reportlab.lib.utils import ImageReader
                        import io
                        
                        # Load and process image
                        pil_img = Image.open(img_path)
                        # Convert to RGBA if needed
                        if pil_img.mode != 'RGBA':
                            pil_img = pil_img.convert('RGBA')
                        
                        # Create circular mask
                        mask = Image.new('L', pil_img.size, 0)
                        draw = ImageDraw.Draw(mask)
                        # Draw white circle
                        draw.ellipse([0, 0, pil_img.size[0], pil_img.size[1]], fill=255)
                        
                        # Apply mask
                        pil_img.putalpha(mask)
                        
                        # Save to bytes
                        img_bytes = io.BytesIO()
                        pil_img.save(img_bytes, format='PNG')
                        img_bytes.seek(0)
                        
                        # Draw circular image
                        c.drawImage(ImageReader(img_bytes), x, y, size, size, preserveAspectRatio=True, mask='auto')
                        
                        # Draw visible circle border in teal (matching other elements)
                        c.setStrokeColorRGB(*TEAL)  # Teal border to match design
                        c.setLineWidth(circle_border_width)
                        # Draw circle outline (centered on image)
                        c.circle(x + size/2, y + size/2, size/2, stroke=1, fill=0)
                        
                        return
                    except Exception:
                        # Fallback to regular image if circular fails
                        pass
                
                # Fallback: draw regular image (square/rectangular) with border
                try:
                    c.drawImage(img_path, x, y, size, size, preserveAspectRatio=True, mask='auto')
                    # Draw border around square image in teal
                    c.setStrokeColorRGB(*TEAL)  # Teal border to match design
                    c.setLineWidth(circle_border_width)
                    c.rect(x, y, size, size, stroke=1, fill=0)
                except Exception:
                    pass
            
            # Draw employee image (left) - circular
            employee_img_x = left_margin
            employee_img_y = header_y - img_size
            if employee_img_path and os.path.exists(employee_img_path):
                draw_circular_image(employee_img_path, employee_img_x, employee_img_y, img_size)
            
            # Draw evaluator image (right) - circular
            evaluator_img_x = left_margin + img_size + spacing if employee_img_path else left_margin
            evaluator_img_y = header_y - img_size
            if evaluator_img_path and os.path.exists(evaluator_img_path):
                draw_circular_image(evaluator_img_path, evaluator_img_x, evaluator_img_y, img_size)
            
            # Draw role labels and names below images
            label_y = header_y - img_size - name_gap
            name_y = label_y - 14  # Names below labels
            
            # Employee label and name (left) - centered below image
            c.setFont('Helvetica-Bold', 11)
            c.setFillColorRGB(*TEAL)
            employee_label = "Employee"
            if employee_img_path:
                label_width = c.stringWidth(employee_label, 'Helvetica-Bold', 11)
                label_x = employee_img_x + (img_size - label_width) / 2
                c.drawString(label_x, label_y, employee_label)
            else:
                c.drawString(left_margin, label_y, employee_label)
            
            # Employee name
            c.setFont('Helvetica-Bold', 16)
            c.setFillColorRGB(0, 0, 0)  # Black for name
            if employee_img_path:
                name_width = c.stringWidth(employee_name, 'Helvetica-Bold', 16)
                name_x = employee_img_x + (img_size - name_width) / 2
                c.drawString(name_x, name_y, employee_name)
            else:
                c.drawString(left_margin, name_y, employee_name)
            
            # Evaluator label and name (right) - centered below image
            c.setFont('Helvetica-Bold', 11)
            c.setFillColorRGB(*TEAL)
            evaluator_label = "Evaluator"
            if evaluator_img_path:
                label_width = c.stringWidth(evaluator_label, 'Helvetica-Bold', 11)
                label_x = evaluator_img_x + (img_size - label_width) / 2
                c.drawString(label_x, label_y, evaluator_label)
            else:
                label_width = c.stringWidth(evaluator_label, 'Helvetica-Bold', 11)
                label_x = width - left_margin - label_width
                c.drawString(label_x, label_y, evaluator_label)
            
            # Evaluator name
            c.setFont('Helvetica-Bold', 16)
            c.setFillColorRGB(0, 0, 0)  # Black for name
            if evaluator_img_path:
                name_width = c.stringWidth(evaluator_name, 'Helvetica-Bold', 16)
                name_x = evaluator_img_x + (img_size - name_width) / 2
                c.drawString(name_x, name_y, evaluator_name)
            else:
                name_width = c.stringWidth(evaluator_name, 'Helvetica-Bold', 16)
                name_x = width - left_margin - name_width
                c.drawString(name_x, name_y, evaluator_name)
            
            # Date if available (positioned below names)
            date_val = _find_name_field(emp_data, ['date', 'evaluation'])
            if date_val:
                c.setFont('Helvetica', 10)
                c.setFillColorRGB(0, 0, 0)  # Black for date
                date_y = name_y - 14  # Below names
                date_str = _format_date_only(date_val)
                # Center date below employee name if image exists
                if employee_img_path:
                    date_width = c.stringWidth(date_str, 'Helvetica', 10)
                    date_x = employee_img_x + (img_size - date_width) / 2
                    c.drawString(date_x, date_y, date_str)
                else:
                    c.drawString(left_margin, date_y, date_str)
            
            # Divider line (below date/names)
            divider_y = date_y - 0.15*inch if date_val else name_y - 0.15*inch
            c.setLineWidth(1)
            c.setStrokeColorRGB(*TEAL)
            c.line(left_margin, divider_y, width - left_margin, divider_y)
            
            # Body content
            body_font = 'Helvetica'
            label_font = 'Helvetica-Bold'
            body_size = 10
            label_size = 11
            line_leading = 12
            x = 0.75*inch
            y = divider_y - 0.2*inch
            max_width = width - 1.5*inch
            
            def draw_text(text: str, font: str, size: int, extra_gap: int = 0):
                """Draw wrapped text and move cursor up with leading & gap."""
                nonlocal y
                lines = simpleSplit(str(text), font, size, max_width)
                for ln in lines:
                    c.setFont(font, size)
                    c.drawString(x, y, ln)
                    y -= line_leading
                if extra_gap:
                    y -= extra_gap
            
            def ensure_space_lines(lines_needed: int = 4):
                """Guard: page break by approximate line count."""
                nonlocal y
                if y - lines_needed * line_leading < 0.75*inch:
                    c.showPage()
                    y = height - 0.75*inch
            
            def ensure_space_px(pixels_needed: float):
                """Guard: page break by pixel height need."""
                nonlocal y
                if y - pixels_needed < 0.75*inch:
                    c.showPage()
                    y = height - 0.75*inch
            
            def draw_value_box(label: str, value: str):
                """Teal label + rounded rectangle for the value body."""
                nonlocal y
                c.setFillColorRGB(*TEAL)
                c.setFont(label_font, 10)
                c.drawString(x, y, label)
                y -= 12
                c.setFillColorRGB(*BOX_BG)
                c.setStrokeColorRGB(*TEAL)
                text_lines = simpleSplit(str(value), body_font, body_size, max_width - 12)
                box_h = len(text_lines) * line_leading + 12
                c.roundRect(x, y - box_h + 6, max_width, box_h, 6, stroke=1, fill=1)
                c.setFillColorRGB(0, 0, 0)
                c.setFont(body_font, body_size)
                ty = y - 6
                for ln in text_lines:
                    c.drawString(x + 6, ty, ln)
                    ty -= line_leading
                y = y - box_h - 6
            
            # Render evaluation data - include ALL fields from Excel
            # First, render fields from header mappings (organized by groups)
            if header_mappings:
                for grp in group_order:
                    values = []
                    for m in group_to_fields.get(grp, []):
                        val = emp_data.get(m.mapped_header)
                        if val and str(val).strip():
                            values.append((m.mapped_header, val, m))
                    if not values:
                        continue
                    ensure_space_lines(6)
                    group_title = grp.value.replace('_', ' ').title()
                    c.setFillColorRGB(*TEAL)
                    c.setFont(label_font, 13)
                    c.drawString(x, y, group_title)
                    y -= 4
                    c.setLineWidth(0.8)
                    c.setStrokeColorRGB(*TEAL)
                    c.line(x, y, x + max_width, y)
                    y -= 8
                    # Exclude certain fields from Basic Info section
                    for label, val, m in values:
                        # Skip excluded fields in Basic Info: id, Employee Name, Employee Name Alt
                        if grp == CardGroup.BASIC_INFO:
                            label_str = str(label).strip()
                            label_lower = label_str.lower()
                            # Exclude: id, Employee Name, Employee Name Alt
                            if (label_lower == "id" or 
                                label_str == "Employee Name" or 
                                label_str == "Employee Name Alt"):
                                continue
                        mapping = m
                        base_gap = 18
                        if getattr(mapping, 'data_type_in_card', None) and mapping.data_type_in_card.value.lower() == 'rating_num':
                            icon_size = 0.22 * inch
                            ensure_space_px(icon_size + base_gap + 8)
                            c.setFillColorRGB(*TEAL)
                            # Use clean display label for ratings too
                            display_label = _get_display_label(label)
                            draw_text(display_label, label_font, label_size)
                            try:
                                score = int(str(val).strip()[:1]) if str(val).strip() else 0
                            except Exception:
                                score = 0
                            icon_y = y
                            icon_x = x
                            for i in range(5):
                                icon_path = rating_checked_path if i < score else rating_unchecked_path
                                try:
                                    c.drawImage(icon_path, icon_x, icon_y - icon_size + 8, icon_size, icon_size, mask='auto')
                                except Exception:
                                    pass
                                icon_x += icon_size + 2
                            y -= (icon_size + 6)
                        else:
                            text_lines = simpleSplit(str(val), body_font, body_size, max_width - 12)
                            box_h = len(text_lines) * line_leading + 12
                            ensure_space_px(box_h + base_gap)
                            # Use clean display label
                            display_label = _get_display_label(label)
                            draw_value_box(display_label, val)
                    y -= 10
            
            # Also render any remaining fields that might not be in header mappings
            # This ensures we capture everything from the Excel file
            rendered_fields = set()
            if header_mappings:
                for m in header_mappings.values():
                    rendered_fields.add(m.mapped_header)
            
            # Check for unmapped fields in parsed data
            unmapped_fields = []
            for k, v in emp_data.items():
                # Skip already rendered fields and metadata
                if k in rendered_fields:
                    continue
                if not v or str(v).strip() == '':
                    continue
                # Skip internal/metadata fields
                if k.lower() in ['id', 'start_time', 'completion_time', 'last_modified']:
                    continue
                # Skip name fields (already in header)
                if k.lower() in ['employee name', 'employee name alt', 'evaluator name']:
                    continue
                unmapped_fields.append((k, v))
            
            # Also check raw Excel data for any columns not in parsed data
            if df is not None and idx < len(df):
                row_data = df.iloc[idx]
                # Get all column names
                for col_idx, col_name in enumerate(df.columns):
                    # Skip columns we've already handled
                    if col_idx in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:  # Metadata and name columns
                        continue
                    
                    # Check if this column is represented in rendered fields
                    col_normalized = str(col_name).strip().replace('\xa0', ' ').replace('\n', ' ').lower()
                    found_in_rendered = False
                    for rendered_field in rendered_fields:
                        rendered_normalized = str(rendered_field).strip().replace('\xa0', ' ').replace('\n', ' ').lower()
                        if col_normalized in rendered_normalized or rendered_normalized in col_normalized:
                            found_in_rendered = True
                            break
                    
                    if not found_in_rendered:
                        # Check if value exists
                        try:
                            raw_val = row_data.iloc[col_idx] if hasattr(row_data, 'iloc') else row_data[col_idx]
                            if pd.notna(raw_val) and str(raw_val).strip():
                                # Check if not already in unmapped_fields
                                col_clean = str(col_name).strip().replace('\xa0', ' ')
                                already_added = any(col_clean.lower() == str(uf[0]).lower() for uf in unmapped_fields)
                                if not already_added:
                                    unmapped_fields.append((col_clean, str(raw_val).strip()))
                        except (IndexError, KeyError):
                            pass
            
            if unmapped_fields:
                ensure_space_lines(6)
                c.setFillColorRGB(*TEAL)
                c.setFont(label_font, 13)
                c.drawString(x, y, "Additional Information")
                y -= 4
                c.setLineWidth(0.8)
                c.setStrokeColorRGB(*TEAL)
                c.line(x, y, x + max_width, y)
                y -= 8
                for label, val in unmapped_fields:
                    ensure_space_lines(4)
                    # Use clean display label
                    label_clean = _get_display_label(label)
                    text_lines = simpleSplit(str(val), body_font, body_size, max_width - 12)
                    box_h = len(text_lines) * line_leading + 12
                    ensure_space_px(box_h + 18)
                    draw_value_box(label_clean, val)
                y -= 10
            
            c.showPage()
            c.save()
            log_func(f"Saved: {pdf_filename}")
            processed_count += 1
            
        except Exception as e:
            log_func(f"Row {idx + 1}: Error - {str(e)}")
            import traceback
            log_func(traceback.format_exc())
            continue
    
    log_func(f"Completed: {processed_count} PDFs generated in {export_dir}")
    return export_dir

