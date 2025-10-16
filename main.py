import sys
import os

# Fix console encoding for Windows (safe)
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from app.modules.gui_app import launch_gui


def main() -> int:
    launch_gui()
    return 0


if __name__ == "__main__":
    sys.exit(main())
