"""Application entry point.

Run with:
    python -m annotis.ui.app
    # or after pip install -e .
    annotis
"""

from __future__ import annotations

import logging
import sys

from PyQt6.QtWidgets import QApplication

from annotis.ui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)s  %(levelname)s  %(message)s",
)


def main() -> None:
    """Create the QApplication and display the main window."""
    app = QApplication(sys.argv)
    app.setApplicationName("Annotis")
    app.setOrganizationName("annotis")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
