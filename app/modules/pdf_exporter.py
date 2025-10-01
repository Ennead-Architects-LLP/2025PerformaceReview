import os
from typing import List, Dict, Any, Callable, Optional

from .config import Config


def _safe_filename(name: str) -> str:
    """Return a filesystem-safe filename (letters/digits/dash/dot only)."""
    import re
    return re.sub(r"[^\w\-\.]+", "_", str(name))[:80] or "Employee"


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


def export_pdfs_reportlab(
    employees: List[Dict[str, Any]],
    export_dir: str,
    log_func: Callable[[str], None],
    header_mappings: Optional[Dict[Any, Any]] = None,
) -> str:
    """Export one portrait-letter PDF per employee using ReportLab.

    Steps:
      1. Ensure output exists; load profile image mappings and rating icon paths
      2. Build group ordering from `header_mappings` to mirror the modal
      3. For each employee:
         a) Header with profile image, name, and date (YYYY-MM-DD)
         b) For each group: teal title + divider
         c) For ratings: render 0..5 icons; for text: teal label + rounded value box
         d) Proactively page-break when remaining space is insufficient
         e) Save the PDF with a safe file name
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

    os.makedirs(export_dir, exist_ok=True)

    # (1) Image mappings for profile photos
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

    # (1) Rating icon asset paths
    rating_checked_path = os.path.join(Config.get_assets_dir_path(), 'icons', 'rating_checked.png')
    rating_unchecked_path = os.path.join(Config.get_assets_dir_path(), 'icons', 'rating_unchecked.png')

    def _rgb(hex_color: str):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))

    TEAL = _rgb('2B7A78')
    BOX_BG = _rgb('F7FBFA')

    # (2) Precompute grouping from header_mappings
    group_to_fields = {}
    group_order = []
    if header_mappings:
        for _idx, m in header_mappings.items():
            grp = m.group_under
            if grp not in group_to_fields:
                group_to_fields[grp] = []
                group_order.append(grp)
            group_to_fields[grp].append(m)
        for grp in group_to_fields:
            group_to_fields[grp] = sorted(group_to_fields[grp], key=lambda m: m.display_order)

    # (3) Export per-employee
    for emp in employees:
        name_field = next((v for k, v in emp.items() if v and 'name' in k.lower()), None)
        safe = _safe_filename(name_field or 'Employee')
        pdf_path = os.path.join(export_dir, Config.PDF_FILE_NAMING.format(name=safe))
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter

        header_y = height - 0.75*inch
        img_size = 0.9*inch
        left_margin = 0.75*inch
        top_name_y = header_y - 0.1*inch

        img_path = name_to_image.get(name_field or '', None)
        if img_path and os.path.exists(img_path):
            try:
                c.drawImage(img_path, left_margin, header_y - img_size, img_size, img_size, preserveAspectRatio=True, mask='auto')
            except Exception:
                pass

        text_left = left_margin + (img_size + 0.3*inch if img_path else 0)
        c.setFont('Helvetica-Bold', 18)
        c.drawString(text_left, top_name_y, f"{name_field or safe}")
        date_val = next((v for k, v in emp.items() if v and 'date' in k.lower() and 'evaluation' in k.lower()), '')
        if date_val:
            c.setFont('Helvetica', 11)
            c.drawString(text_left, top_name_y - 16, _format_date_only(date_val))
        c.setLineWidth(1)
        c.line(left_margin, header_y - img_size - 0.15*inch, width - left_margin, header_y - img_size - 0.15*inch)

        # Helpers / typography
        body_font = 'Helvetica'
        label_font = 'Helvetica-Bold'
        body_size = 10
        label_size = 11
        line_leading = 12
        x = 0.75*inch
        y = header_y - img_size - 0.35*inch
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

        if header_mappings:
            for grp in group_order:
                values = []
                for m in group_to_fields.get(grp, []):
                    val = emp.get(m.mapped_header)
                    if val and str(val).strip():
                        values.append((m.mapped_header, val, m))
                if not values:
                    continue
                ensure_space_lines(6)
                group_title = grp.value.replace('_', ' ').title()
                c.setFillColorRGB(*TEAL)
                c.setFont(label_font, 13)
                c.drawString(x, y, group_title)
                # Move divider 1pt closer to title
                y -= 4
                c.setLineWidth(0.8)
                c.setStrokeColorRGB(*TEAL)
                c.line(x, y, x + max_width, y)
                y -= 8
                basic_allow = {"Title", "Employee Role", "Email"}
                for label, val, m in values:
                    if grp == CardGroup.BASIC_INFO and label not in basic_allow:
                        continue
                    mapping = m
                    base_gap = 18
                    if getattr(mapping, 'data_type_in_card', None) and mapping.data_type_in_card.value.lower() == 'rating_num':
                        icon_size = 0.22 * inch
                        ensure_space_px(icon_size + base_gap + 8)
                        c.setFillColorRGB(*TEAL)
                        draw_text(label, label_font, label_size)
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
                        draw_value_box(label, val)
                y -= 10
        else:
            for k, v in emp.items():
                if not v:
                    continue
                ensure_space_lines(4)
                label = k.replace('_', ' ').title()
                draw_value_box(label, v)

        c.showPage()
        c.save()
        log_func(f"Saved PDF: {pdf_path}")

    return export_dir


