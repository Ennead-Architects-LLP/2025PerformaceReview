"""
Evaluator-Employee PDF Maker

Main entry point for the batch PDF generator application.
This app reads Excel files with evaluator-employee pairs and generates
PDFs with both profile images displayed side by side.
"""

import sys
import os
import threading

# Fix console encoding for Windows (safe)
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from tkinter import Tk, Button, Label, filedialog, StringVar, DISABLED, NORMAL
from app.modules.batch_pdf_generator import export_batch_pdfs_with_dual_images
from app.modules.config import Config

# GUI Color Scheme (matching existing app style)
DARK_BG = "#121212"
DARK_PANEL = "#1e1e1e"
DARK_TEXT = "#e5e5e5"
DARK_SUBTEXT = "#999999"
ACCENT = "#4CAF50"
ACCENT_HOVER = "#45a049"


class EvaluatorEmployeePdfMakerApp:
    """GUI application for batch PDF generation."""
    
    def __init__(self):
        self.root = Tk()
        self.root.title("Evaluator-Employee PDF Maker")
        self.root.configure(bg=DARK_BG)
        
        # Set window icon if available
        try:
            icon_path = os.path.join(Config.get_assets_dir_path(), "icons", "ennead_architects_logo.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass
        
        # File selection
        self.selected_file = StringVar(value="No Excel file selected")
        self.excel_path = None
        
        # Output folder selection
        self.output_dir_label = StringVar(value="No output folder selected")
        self.output_dir = None
        
        # Status
        self.status = StringVar(value="Ready")
        
        # Build UI
        self._build_ui()
    
    def _build_ui(self):
        """Build the user interface."""
        # Title/Notice
        notice = Label(
            self.root, 
            text="Generate PDFs for Evaluator-Employee Review Pairs",
            fg=DARK_TEXT, 
            bg=DARK_BG,
            font=("Helvetica", 10, "bold")
        )
        notice.pack(padx=12, pady=(12, 4), anchor="w")
        
        privacy = Label(
            self.root, 
            text="All data is processed locally. No information is uploaded or shared.",
            fg=DARK_SUBTEXT, 
            bg=DARK_BG
        )
        privacy.pack(padx=12, pady=(0, 12), anchor="w")
        
        # Excel file selection
        excel_label = Label(
            self.root, 
            textvariable=self.selected_file, 
            fg=DARK_TEXT, 
            bg=DARK_BG,
            wraplength=500
        )
        excel_label.pack(padx=12, pady=(0, 4), anchor="w")
        
        pick_excel_button = Button(
            self.root, 
            text="Select Excel File (.xlsx)", 
            command=self.pick_excel_file, 
            bg=ACCENT, 
            fg="#0b0b0b", 
            activebackground=ACCENT_HOVER, 
            activeforeground="#0b0b0b", 
            relief="flat", 
            highlightthickness=0
        )
        pick_excel_button.pack(padx=12, pady=6, anchor="w")
        
        # Output folder selection
        output_label = Label(
            self.root, 
            textvariable=self.output_dir_label, 
            fg=DARK_TEXT, 
            bg=DARK_BG,
            wraplength=500
        )
        output_label.pack(padx=12, pady=(12, 4), anchor="w")
        
        pick_output_button = Button(
            self.root, 
            text="Select Output Folder", 
            command=self.pick_output_folder, 
            bg=ACCENT, 
            fg="#0b0b0b", 
            activebackground=ACCENT_HOVER, 
            activeforeground="#0b0b0b", 
            relief="flat", 
            highlightthickness=0
        )
        pick_output_button.pack(padx=12, pady=6, anchor="w")
        
        # Generate button
        self.generate_button = Button(
            self.root, 
            text="Generate PDFs", 
            command=self.generate_pdfs, 
            state=DISABLED,
            bg=ACCENT, 
            fg="#0b0b0b", 
            activebackground=ACCENT_HOVER, 
            activeforeground="#0b0b0b", 
            relief="flat", 
            highlightthickness=0
        )
        self.generate_button.pack(padx=12, pady=12, anchor="w")
        
        # Status
        status_label = Label(
            self.root, 
            textvariable=self.status, 
            fg=DARK_SUBTEXT, 
            bg=DARK_BG,
            wraplength=500
        )
        status_label.pack(padx=12, pady=(6, 12), anchor="w")
        
        # Footer
        footer = Label(
            self.root, 
            text="© EnneadTab 2025", 
            fg=DARK_SUBTEXT, 
            bg=DARK_BG
        )
        footer.pack(padx=12, pady=(0, 12), anchor="e")
    
    def log(self, message: str):
        """Update status message."""
        try:
            self.status.set(message)
            self.root.update_idletasks()
        except Exception:
            pass
    
    def pick_excel_file(self):
        """Open file dialog to select Excel file."""
        filetypes = [("Excel files", "*.xlsx"), ("All files", "*.*")]
        path = filedialog.askopenfilename(
            title="Select Excel File with Evaluator-Employee Data",
            filetypes=filetypes
        )
        if path:
            self.excel_path = path
            filename = os.path.basename(path)
            self.selected_file.set(f"Excel: {filename}")
            self.log(f"Selected: {filename}")
            self._update_generate_button_state()
    
    def pick_output_folder(self):
        """Open folder dialog to select output directory."""
        path = filedialog.askdirectory(title="Select Output Folder for PDFs")
        if path:
            self.output_dir = path
            self.output_dir_label.set(f"Output: {path}")
            self.log(f"Output folder: {path}")
            self._update_generate_button_state()
    
    def _update_generate_button_state(self):
        """Enable generate button if both file and output folder are selected."""
        if self.excel_path and self.output_dir:
            self.generate_button.configure(state=NORMAL)
        else:
            self.generate_button.configure(state=DISABLED)
    
    def _generate_background(self):
        """Generate PDFs in background thread."""
        try:
            self.generate_button.configure(state=DISABLED)
            self.log("Starting PDF generation...")
            
            result = export_batch_pdfs_with_dual_images(
                self.excel_path,
                self.output_dir,
                self.log
            )
            
            if result:
                self.log(f"✓ PDF generation completed! Check: {self.output_dir}")
            else:
                self.log("✗ PDF generation failed. Check the status messages above.")
        except Exception as e:
            self.log(f"Error: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
        finally:
            if self.excel_path and self.output_dir:
                self.generate_button.configure(state=NORMAL)
    
    def generate_pdfs(self):
        """Start PDF generation in background thread."""
        if not self.excel_path:
            self.log("Please select an Excel file first.")
            return
        if not self.output_dir:
            self.log("Please select an output folder first.")
            return
        
        threading.Thread(target=self._generate_background, daemon=True).start()
    
    def start(self):
        """Start the GUI main loop."""
        self.root.mainloop()


def main() -> int:
    """Main entry point."""
    app = EvaluatorEmployeePdfMakerApp()
    app.start()
    return 0


if __name__ == "__main__":
    sys.exit(main())

