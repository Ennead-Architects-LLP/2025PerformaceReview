"""Test PDF with visible circle borders and proper spacing"""
import sys
import os
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from app.modules.batch_pdf_generator import export_batch_pdfs_with_dual_images

def log(msg):
    print(msg)

if __name__ == "__main__":
    excel_path = r"assets/data/Evaluator Employee Performance Review 2025_TEST For SEN.xlsx"
    output_dir = r"OUTPUT/test_pdfs_final"
    
    print("Testing PDF with visible circle borders and proper spacing...")
    os.makedirs(output_dir, exist_ok=True)
    
    result = export_batch_pdfs_with_dual_images(excel_path, output_dir, log)
    print(f"\n✓ Test complete. Check: {output_dir}")

