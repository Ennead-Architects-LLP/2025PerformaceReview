import os
import threading
import traceback
import webbrowser
from tkinter import Tk, Button, Label, filedialog, StringVar, END, DISABLED, NORMAL

from .excel_parser import parse_excel_to_json
from .html_generator import create_html_output_from_employees
from .employee import Employee
from .config import Config
import shutil


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

        # Minimal status line instead of verbose console output
        self.status = StringVar(value="")
        self.status_label = Label(self.root, textvariable=self.status, fg=DARK_SUBTEXT, bg=DARK_BG)
        self.status_label.pack(padx=12, pady=(6, 12), anchor="w")

        self.footer = Label(self.root, text="© EnneadTab 2025", fg=DARK_SUBTEXT, bg=DARK_BG)
        self.footer.pack(padx=12, pady=(0, 12), anchor="e")

        self.file_path = None

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

    def start(self):
        self.root.mainloop()


def launch_gui():
    app = GuiApp()
    app.start()
