import sys

from app.modules.gui_app import launch_gui


def main() -> int:
    launch_gui()
    return 0


if __name__ == "__main__":
    sys.exit(main())
