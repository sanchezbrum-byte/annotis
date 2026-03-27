"""Folder tree explorer with expand/collapse for hierarchical image discovery."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QDir
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import QTreeView, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)

# Supported image extensions for folder filtering
SUPPORTED_EXTENSIONS = frozenset(
    {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
)


class FolderExplorer(QWidget):
    """Hierarchical folder tree view with image count tracking.

    Shows expandable/collapsible folder structure and counts of images
    in each folder. Double-click a folder to load its images.
    """

    def __init__(self, on_folder_selected: Callable[[Path], None]) -> None:
        """Initialize the folder explorer.

        Args:
            on_folder_selected: Callback invoked when folder is double-clicked.
        """
        super().__init__()
        self._on_folder_selected = on_folder_selected
        self._tree_view = QTreeView()
        self._model = QFileSystemModel()

        self._setup_ui()
        self._configure_model()

    def _setup_ui(self) -> None:
        """Configure the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._tree_view.setModel(self._model)
        self._tree_view.doubleClicked.connect(self._on_item_double_clicked)

        # Hide all columns except Name
        self._tree_view.hideColumn(1)  # Size
        self._tree_view.hideColumn(2)  # Type
        self._tree_view.hideColumn(3)  # Date Modified

        layout.addWidget(self._tree_view)

    def _configure_model(self) -> None:
        """Configure file system model to filter for folders and images."""
        # Show folders and image files; hide other file types
        self._model.setFilter(
            QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.Files
        )
        # Only show folders and supported image extensions
        self._model.setNameFilters(
            ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.tif", "*.webp"]
        )
        self._model.setNameFilterDisables(False)

    def set_root_path(self, path: Path) -> None:
        """Set the root folder for the tree.

        Args:
            path: Absolute path to the root folder.
        """
        if not path.exists() or not path.is_dir():
            logger.warning(f"Invalid root path: {path}")
            return

        root_index = self._model.setRootPath(str(path))
        self._tree_view.setRootIndex(root_index)
        self._tree_view.expandAll()

    def _on_item_double_clicked(self, index: Any) -> None:
        """Handle double-click on tree item.

        If item is a folder, load its images.
        """
        item_path = Path(self._model.filePath(index))

        if item_path.is_dir():
            self._on_folder_selected(item_path)

    def collapse_all(self) -> None:
        """Collapse all expanded tree items."""
        self._tree_view.collapseAll()

    def expand_all(self) -> None:
        """Expand all tree items."""
        self._tree_view.expandAll()
