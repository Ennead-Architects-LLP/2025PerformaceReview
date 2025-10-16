import os
import threading
import traceback
import webbrowser
from tkinter import Tk, Button, Label, filedialog, StringVar, END, DISABLED, NORMAL

from .excel_parser import parse_excel_to_json
from .pdf_exporter import export_pdfs_reportlab
def _safe_filename(name: str) -> str:
    import re
    return re.sub(r"[^\w\-\.]+", "_", name)[:80] or "Employee"

def _export_pdf_reportlab(employees: list, export_dir: str, log_func, header_mappings=None) -> str:
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

    # Load image mappings for profile pictures
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

    # Rating icons
    rating_checked_path = os.path.join(Config.get_assets_dir_path(), 'icons', 'rating_checked.png')
    rating_unchecked_path = os.path.join(Config.get_assets_dir_path(), 'icons', 'rating_unchecked.png')

    # Prepare grouping order and fields if mappings are available
    group_to_fields = {}
    group_order = []
    if header_mappings:
        # header_mappings: dict[col_index] -> mapping with attributes: mapped_header, group_under, display_order
        for _idx, m in header_mappings.items():
            grp = m.group_under
            if grp not in group_to_fields:
                group_to_fields[grp] = []
                group_order.append(grp)
            group_to_fields[grp].append(m)
        for grp in group_to_fields:
            group_to_fields[grp] = sorted(group_to_fields[grp], key=lambda m: m.display_order)

    for emp in employees:
        name_field = next((v for k,v in emp.items() if v and 'name' in k.lower()), None)
        safe = _safe_filename(name_field or 'Employee')
        pdf_path = os.path.join(export_dir, Config.PDF_FILE_NAMING.format(name=safe))
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter

        # Header
        header_y = height - 0.75*inch
        img_size = 0.9*inch
        left_margin = 0.75*inch
        top_name_y = header_y - 0.1*inch

        # Profile image if available
        img_path = name_to_image.get(name_field or '', None)
        if img_path and os.path.exists(img_path):
            try:
                c.drawImage(img_path, left_margin, header_y - img_size, img_size, img_size, preserveAspectRatio=True, mask='auto')
            except Exception:
                pass

        # Name and date
        text_left = left_margin + (img_size + 0.3*inch if img_path else 0)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(text_left, top_name_y, f"{name_field or safe}")
        # optional date field if present in employee dict
        date_val = next((v for k,v in emp.items() if v and 'date' in k.lower() and 'evaluation' in k.lower()), '')
        if date_val:
            def _format_date_only(val):
                try:
                    # handle datetime objects directly
                    import datetime as _dt
                    if isinstance(val, (_dt.datetime, _dt.date)):
                        return val.date().isoformat() if isinstance(val, _dt.datetime) else val.isoformat()
                except Exception:
                    pass
                s = str(val)
                # Common separators
                if 'T' in s:
                    s = s.split('T')[0]
                if ' ' in s:
                    s = s.split(' ')[0]
                # Fallback: try pandas parsing for robustness
                try:
                    import pandas as _pd
                    parsed = _pd.to_datetime(val, errors='coerce')
                    if parsed is not None and not _pd.isna(parsed):
                        return parsed.date().isoformat()
                except Exception:
                    pass
                # Last resort: trim to 10 chars (YYYY-MM-DD)
                return s[:10]

            c.setFont("Helvetica", 11)
            c.drawString(text_left, top_name_y - 16, _format_date_only(date_val))
        # Header underline
        c.setLineWidth(1)
        c.line(left_margin, header_y - img_size - 0.15*inch, width - left_margin, header_y - img_size - 0.15*inch)

        # Modal-like palette and spacing
        def _rgb(hex_color: str):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))
        TEAL = _rgb('2B7A78')
        BOX_BG = _rgb('F7FBFA')
        body_font = "Helvetica"
        label_font = "Helvetica-Bold"
        body_size = 10
        label_size = 11
        line_leading = 12
        x = 0.75*inch
        y = header_y - img_size - 0.35*inch
        max_width = width - 1.5*inch

        def draw_text(text: str, font: str, size: int, extra_gap: int = 0):
            nonlocal y
            lines = simpleSplit(str(text), font, size, max_width)
            for ln in lines:
                c.setFont(font, size)
                c.drawString(x, y, ln)
                y -= line_leading
            if extra_gap:
                y -= extra_gap

        def ensure_space_lines(lines_needed: int = 4):
            nonlocal y
            if y - lines_needed * line_leading < 0.75*inch:
                c.showPage()
                y = height - 0.75*inch

        def ensure_space_px(pixels_needed: float):
            nonlocal y
            if y - pixels_needed < 0.75*inch:
                c.showPage()
                y = height - 0.75*inch

        def draw_value_box(label: str, value: str):
            nonlocal y
            # Label in teal
            c.setFillColorRGB(*TEAL)
            c.setFont(label_font, 10)
            c.drawString(x, y, label)
            y -= 12
            # Value rounded box with light teal border
            c.setFillColorRGB(*BOX_BG)
            c.setStrokeColorRGB(*TEAL)
            text_lines = simpleSplit(str(value), body_font, body_size, max_width - 12)
            box_h = len(text_lines) * line_leading + 12
            c.roundRect(x, y - box_h + 6, max_width, box_h, 6, stroke=1, fill=1)
            c.setFillColorRGB(0,0,0)
            c.setFont(body_font, body_size)
            ty = y - 6
            for ln in text_lines:
                c.drawString(x + 6, ty, ln)
                ty -= line_leading
            y = y - box_h - 6

        # Render grouped fields if mappings available; otherwise fallback to flat
        if header_mappings:
            for grp in group_order:
                # Collect fields with values
                values = []
                for m in group_to_fields.get(grp, []):
                    val = emp.get(m.mapped_header)
                    if val and str(val).strip():
                        values.append((m.mapped_header, val))
                if not values:
                    continue
                # Group box
                ensure_space_lines(6)
                group_title = grp.value.replace('_',' ').title()
                c.setFillColorRGB(*TEAL)
                c.setFont(label_font, 13)
                c.drawString(x, y, group_title)
                # place divider a bit lower to avoid overlapping the title baseline
                y -= 8
                c.setLineWidth(0.8)
                c.setStrokeColorRGB(*TEAL)
                c.line(x, y, x+max_width, y)
                y -= 8
                # Fields
                basic_allow = {"Title", "Employee Role", "Email"}
                for label, val in values:
                    if grp == CardGroup.BASIC_INFO and label not in basic_allow:
                        continue
                    # estimate space before drawing
                    # default base spacing
                    base_gap = 18
                    # Check if rating_num
                    # Check if rating_num
                    mapping = next((m for m in group_to_fields.get(grp, []) if m.mapped_header == label), None)
                    if mapping and getattr(mapping, 'data_type_in_card', '').value.lower() == 'rating_num':
                        icon_size = 0.22*inch
                        ensure_space_px(icon_size + base_gap + 8)
                        # Draw label
                        c.setFillColorRGB(*TEAL)
                        draw_text(label, label_font, label_size)
                        # Draw 5 icons
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
                        # compute value box height and ensure space
                        text_lines = simpleSplit(str(val), body_font, body_size, max_width - 12)
                        box_h = len(text_lines) * line_leading + 12
                        ensure_space_px(box_h + base_gap)
                        draw_value_box(label, val)
                # Extra space between groups
                y -= 10
        else:
            # Fallback: flat
            for k, v in emp.items():
                if not v:
                    continue
                ensure_space(4)
                label = k.replace('_', ' ').title()
                draw_text(label, label_font, label_size)
                draw_text(v, body_font, body_size, extra_gap=4)

        c.showPage()
        c.save()
        log_func(f"Saved PDF: {pdf_path}")

    return export_dir
from .html_generator import create_html_output_from_employees
from .employee import Employee
from .config import Config
import shutil
import asyncio

async def _export_pdf_with_playwright(index_html_path: str, export_dir: str, log_func) -> str:
    try:
        from playwright.async_api import async_playwright
    except Exception as e:
        log_func(f"Playwright not available: {e}")
        return ""

    if not export_dir:
        raise ValueError("PDF export directory is required")
    os.makedirs(export_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        file_url = "file:///" + index_html_path.replace("\\", "/")
        await page.goto(file_url)
        # Wait for modal hooks
        await page.wait_for_function("() => window.__employeeCount && window.__employeeCount() > 0")
        count = await page.evaluate("() => window.__employeeCount()")

        # Derive names from DOM (employee-name text)
        names = await page.evaluate("() => Array.from(document.querySelectorAll('#employee-list .employee-card .employee-name')).map(e => e.textContent.trim())")
        # Fallback safe names
        def _safe(n):
            import re
            return re.sub(r"[^\w\-\.]+", "_", n)[:80] or "Employee"

        for i in range(count):
            await page.evaluate(f"window.__openModalAt({i})")
            await page.wait_for_selector('#modalOverlay:not([hidden])')
            # Print only the modal
            # Use page.pdf with letter size
            name = _safe(names[i] if i < len(names) else f"Employee_{i+1}")
            pdf_path = os.path.join(export_dir, Config.PDF_FILE_NAMING.format(name=name))
            await page.pdf(path=pdf_path, format='letter', print_background=True, margin={"top":"0","right":"0","bottom":"0","left":"0"})
            log_func(f"Saved PDF: {pdf_path}")
            await page.evaluate("window.__closeModal()")

        await browser.close()
    return export_dir


DARK_BG = "#121212"
DARK_PANEL = "#1e1e1e"
DARK_TEXT = "#e5e5e5"
DARK_SUBTEXT = "#a0a0a0"
ACCENT = "#6c8cff"
ACCENT_HOVER = "#88a3ff"
BORDER = "#2a2a2a"


def _load_employees_from_json(json_path: str):
    try:
        import json
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        employees = []
        for emp in data:
            employees.append(Employee(emp))
        return employees
    except Exception:
        return []


def _get_onedrive_desktop_path() -> str:
    """Return the user's OneDrive Desktop path used in this org."""
    home = os.path.expanduser("~")
    return os.path.join(home, "OneDrive - Ennead Architects", "Desktop")


def _copy_site_to_desktop(source_dir: str, log_func) -> str:
    """Copy generated site directory to Desktop and return the new index.html path."""
    try:
        desktop_dir = _get_onedrive_desktop_path()
        os.makedirs(desktop_dir, exist_ok=True)
        target_dir = os.path.join(desktop_dir, "2025 Ennead Performance Report")
        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
        log_func(f"Copied site to: {target_dir}")
        return os.path.join(target_dir, "index.html")
    except Exception:
        log_func("Failed to copy site to Desktop.")
        return ""


def run_pipeline(excel_path: str, log_func) -> str:
    """Run parse -> json -> load employees -> html, return index.html path or empty string."""
    try:
        if not excel_path or not os.path.exists(excel_path):
            log_func(f"Excel not found: {excel_path}")
            return ""

        log_func("Parsing Excel ...")
        json_output = Config.get_json_output_path()
        success = parse_excel_to_json(excel_path, json_output, copy_images=True)
        if not success:
            log_func("Failed to parse Excel.")
            return ""

        log_func("Loading employees from JSON ...")
        employees = _load_employees_from_json(json_output)
        if not employees:
            log_func("Failed to load employee data from JSON.")
            return ""

        log_func("Generating HTML ...")
        website_dir = Config.get_website_output_path()
        index_path = create_html_output_from_employees(employees, website_dir)
        if not index_path:
            log_func("Failed to generate HTML website.")
            return ""

        log_func(f"Generated (project docs): {index_path}")

        site_source_dir = website_dir
        desktop_index = _copy_site_to_desktop(site_source_dir, log_func)
        if desktop_index:
            try:
                webbrowser.open_new_tab(desktop_index)
                log_func("Opened Desktop copy in default browser.")
                # Optional PDF export
                if getattr(Config, 'ENABLE_PDF_EXPORT', False):
                    try:
                        log_func("Exporting PDFs (letter size)...")
                        export_dir = asyncio.run(_export_pdf_with_playwright(desktop_index, log_func))
                        if export_dir:
                            log_func(f"PDFs saved in: {export_dir}")
                    except Exception as e:
                        log_func(f"PDF export failed: {e}")
                return desktop_index
            except Exception:
                log_func("Could not open Desktop copy automatically.")
                return desktop_index
        return index_path
    except Exception:
        log_func(traceback.format_exc())
        return ""


class GuiApp:
    def __init__(self):
        self.root = Tk()
        self.root.title("Employee Evaluation Report Generator")
        self.root.configure(bg=DARK_BG)
        try:
            icon_path = os.path.join(Config.get_assets_dir_path(), "icons", "ennead_architects_logo.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

        self.selected_file = StringVar(value="No file selected")

        self.notice = Label(self.root, text="This report generator is for Ennead 2025 Self Evaluation only", fg=DARK_SUBTEXT, bg=DARK_BG)
        self.notice.pack(padx=12, pady=(12, 2), anchor="w")

        self.privacy = Label(self.root, text="All data is processed locally on your machine. No information is uploaded or shared.", fg=DARK_SUBTEXT, bg=DARK_BG)
        self.privacy.pack(padx=12, pady=(0, 8), anchor="w")

        self.label = Label(self.root, textvariable=self.selected_file, fg=DARK_TEXT, bg=DARK_BG)
        self.label.pack(padx=12, pady=(0, 8), anchor="w")

        self.pick_button = Button(self.root, text="Pick Excel (.xlsx)", command=self.pick_file, bg=ACCENT, fg="#0b0b0b", activebackground=ACCENT_HOVER, activeforeground="#0b0b0b", relief="flat", highlightthickness=0)
        self.pick_button.pack(padx=12, pady=6, anchor="w")

        self.run_button = Button(self.root, text="Generate Report", command=self.run, bg=ACCENT, fg="#0b0b0b", activebackground=ACCENT_HOVER, activeforeground="#0b0b0b", relief="flat", highlightthickness=0)
        self.run_button.pack(padx=12, pady=6, anchor="w")

        # PDF export controls
        self.pdf_dir_label = StringVar(value="No PDF output folder set")
        self.pdf_label = Label(self.root, textvariable=self.pdf_dir_label, fg=DARK_SUBTEXT, bg=DARK_BG)
        self.pdf_label.pack(padx=12, pady=(12, 2), anchor="w")

        self.pick_pdf_button = Button(self.root, text="Pick PDF Output Folder", command=self.pick_pdf_dir, bg=ACCENT, fg="#0b0b0b", activebackground=ACCENT_HOVER, activeforeground="#0b0b0b", relief="flat", highlightthickness=0)
        self.pick_pdf_button.pack(padx=12, pady=6, anchor="w")

        self.export_button = Button(self.root, text="Export PDFs (Portrait 8.5x11)", command=self.export_pdfs, state=DISABLED, bg=ACCENT, fg="#0b0b0b", activebackground=ACCENT_HOVER, activeforeground="#0b0b0b", relief="flat", highlightthickness=0)
        self.export_button.pack(padx=12, pady=6, anchor="w")

        # Minimal status line instead of verbose console output
        self.status = StringVar(value="")
        self.status_label = Label(self.root, textvariable=self.status, fg=DARK_SUBTEXT, bg=DARK_BG)
        self.status_label.pack(padx=12, pady=(6, 12), anchor="w")

        self.footer = Label(self.root, text="© EnneadTab 2025", fg=DARK_SUBTEXT, bg=DARK_BG)
        self.footer.pack(padx=12, pady=(0, 12), anchor="e")

        self.file_path = None
        self.latest_index_path = None
        self.pdf_output_dir = None

    def log(self, message: str):
        # Show only the latest status message
        try:
            self.status.set(message)
            self.root.update_idletasks()
        except Exception:
            pass

    def pick_file(self):
        filetypes = [("Excel files", "*.xlsx"), ("All files", "*.*")]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self.file_path = path
            self.selected_file.set(path)
            self.log(f"Selected: {path}")

    def _run_background(self):
        try:
            self.pick_button.configure(state=DISABLED)
            self.run_button.configure(state=DISABLED)
            index_path = run_pipeline(self.file_path, self.log)
            if index_path:
                self.latest_index_path = index_path
                # Enable export if PDF dir is set
                if self.pdf_output_dir:
                    self.export_button.configure(state=NORMAL)
                self.log("Done.")
            else:
                self.log("Failed.")
        finally:
            self.pick_button.configure(state=NORMAL)
            self.run_button.configure(state=NORMAL)

    def run(self):
        if not self.file_path:
            self.log("Please pick an Excel file first.")
            return
        threading.Thread(target=self._run_background, daemon=True).start()

    def pick_pdf_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.pdf_output_dir = path
            self.pdf_dir_label.set(f"PDF output: {path}")
            # Enable export button only if we already generated index
            if self.latest_index_path:
                self.export_button.configure(state=NORMAL)
            else:
                self.export_button.configure(state=DISABLED)
            self.log(f"PDF output folder set: {path}")

    def _export_background(self):
        try:
            self.export_button.configure(state=DISABLED)
            if not self.latest_index_path:
                self.log("Generate the report first.")
                return
            if not self.pdf_output_dir:
                self.log("Please pick a PDF output folder.")
                return
            self.log("Exporting PDFs (letter size) with dedicated module...")
            # Reuse parsed data for accurate PDF content
            try:
                from .config import Config as _C
                from .excel_parser import ExcelEmployeeParser as _P
                parser = _P(_C.get_excel_input_path())
                if parser.load_excel():
                    employees_dicts = parser.parse_all_employees_as_dicts()
                    header_mappings = parser.header_mappings
                else:
                    employees_dicts = []
                    header_mappings = None
            except Exception:
                employees_dicts = []
                header_mappings = None

            export_dir = export_pdfs_reportlab(employees_dicts, self.pdf_output_dir, self.log, header_mappings)
            if export_dir:
                self.log(f"PDFs saved in: {export_dir}")
        finally:
            # Re-enable if still valid state
            if self.latest_index_path and self.pdf_output_dir:
                self.export_button.configure(state=NORMAL)

    def export_pdfs(self):
        threading.Thread(target=self._export_background, daemon=True).start()

    def start(self):
        self.root.mainloop()


def launch_gui():
    app = GuiApp()
    app.start()
