"""MainWindow: three-panel annotation layout.

Panel layout:
  Left:   QListWidget — image list with annotation status icons
  Centre: AnnotationCanvas — interactive drawing surface
  Right:  Controls — class selector, annotation list, undo/redo, stats

Autosave runs every 60 seconds via QTimer. The window stores a single
Session in memory and delegates all persistence to SessionStore.

Coverage exclusion: UI code is omitted from the coverage requirement.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QKeySequence, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGraphicsPixmapItem,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from annotis.adapters.session_store import SessionStore
from annotis.application.export import export_coco, export_metadata_csv, export_yolo
from annotis.application.image_loader import load_folder
from annotis.application.metrics import compute_annotation_stats
from annotis.domain.models import Annotation, AnnotationType, BoundingBox, Session
from annotis.ui.canvas import AnnotationCanvas

logger = logging.getLogger(__name__)

_AUTOSAVE_INTERVAL_MS = 60_000


class MainWindow(QMainWindow):
    """Top-level application window."""

    def __init__(self) -> None:
        """Initialize the main application window with three-panel layout.

        Sets up the left image list, centre annotation canvas, and right
        control panels. Configures autosave on 60-second interval. Wires
        all keyboard shortcuts and signal connections.
        """
        super().__init__()
        self.setWindowTitle("Annotis")
        self.resize(1400, 900)

        self._session: Session | None = None
        self._current_idx: int = -1
        self._store: SessionStore | None = None

        self._build_ui()
        self._connect_signals()
        self._setup_shortcuts()
        self._start_autosave()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Assemble the three-panel layout."""
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(4, 4, 4, 4)

        splitter = QSplitter()
        root_layout.addWidget(splitter)

        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_canvas_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([220, 900, 280])

        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._update_status()

    def _build_left_panel(self) -> QWidget:
        """Image list panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel("Images"))
        self._image_list = QListWidget()
        layout.addWidget(self._image_list)

        btn_open = QPushButton("Open Folder…")
        btn_open.clicked.connect(self._on_open_folder)
        layout.addWidget(btn_open)
        return panel

    def _build_canvas_panel(self) -> QWidget:
        """Canvas panel."""
        self._canvas = AnnotationCanvas()
        return self._canvas

    def _build_right_panel(self) -> QWidget:
        """Class selector and annotation list panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)

        layout.addWidget(QLabel("Class"))
        self._class_combo = QComboBox()
        layout.addWidget(self._class_combo)

        layout.addWidget(QLabel("Annotations"))
        self._ann_list = QListWidget()
        layout.addWidget(self._ann_list)

        btn_delete = QPushButton("Delete Selected")
        btn_delete.clicked.connect(self._on_delete_annotation)
        layout.addWidget(btn_delete)

        btn_undo = QPushButton("Undo  (Ctrl+Z)")
        btn_undo.clicked.connect(self._on_undo)
        layout.addWidget(btn_undo)

        btn_redo = QPushButton("Redo  (Ctrl+Y)")
        btn_redo.clicked.connect(self._on_redo)
        layout.addWidget(btn_redo)

        layout.addWidget(QLabel("Statistics"))
        self._stats_label = QLabel("No annotations yet.")
        self._stats_label.setWordWrap(True)
        layout.addWidget(self._stats_label)

        self._build_export_buttons(layout)
        layout.addStretch()
        return panel

    def _build_export_buttons(self, layout: QVBoxLayout) -> None:
        export_label = QLabel("Export")
        layout.addWidget(export_label)

        row = QHBoxLayout()
        for label, slot in [
            ("COCO", self._on_export_coco),
            ("YOLO", self._on_export_yolo),
            ("CSV", self._on_export_csv),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            row.addWidget(btn)
        layout.addLayout(row)

    # ------------------------------------------------------------------
    # Signal / shortcut wiring
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self._image_list.currentRowChanged.connect(self._on_image_selected)
        self._canvas.bbox_completed.connect(self._on_bbox_completed)

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+Z"), self, self._on_undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, self._on_redo)
        QShortcut(QKeySequence("Right"), self, self._on_next_image)
        QShortcut(QKeySequence("Left"), self, self._on_prev_image)
        QShortcut(QKeySequence("Ctrl+S"), self, self._on_save)
        QShortcut(QKeySequence("+"), self, self._canvas.zoom_in)
        QShortcut(QKeySequence("-"), self, self._canvas.zoom_out)
        QShortcut(QKeySequence("F"), self, self._canvas.fit_image)

    def _start_autosave(self) -> None:
        timer = QTimer(self)
        timer.timeout.connect(self._on_save)
        timer.start(_AUTOSAVE_INTERVAL_MS)

    # ------------------------------------------------------------------
    # Slot handlers
    # ------------------------------------------------------------------

    def _on_open_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if not folder:
            return
        images = load_folder(Path(folder))
        if not images:
            QMessageBox.warning(self, "No images", "No supported images found.")
            return

        project_name, ok = self._ask_project_name()
        if not ok:
            return

        self._session = Session(
            project_name=project_name,
            image_folder=Path(folder),
            images=images,
        )
        db_path = Path(folder) / "annotis.db"
        self._store = SessionStore(db_path)

        self._refresh_image_list()
        self._refresh_class_combo()
        self._select_image(0)

    def _on_image_selected(self, idx: int) -> None:
        if self._session is None or idx < 0:
            return
        self._current_idx = idx
        record = self._session.images[idx]
        pixmap = QPixmap(str(record.path))
        if pixmap.isNull():
            QMessageBox.critical(
                self,
                "Error Loading Image",
                f"Cannot load image: {record.path}\n\nFile may be corrupted, "
                "deleted, or in an unsupported format.",
            )
            return
        self._canvas.load_pixmap(QGraphicsPixmapItem(pixmap))
        self._refresh_canvas_annotations()
        self._refresh_ann_list()
        self._refresh_stats()

    def _on_bbox_completed(self, x: float, y: float, w: float, h: float) -> None:
        if self._session is None or self._current_idx < 0:
            return
        record = self._session.images[self._current_idx]
        record.push_undo_snapshot()
        label = self._class_combo.currentText()
        ann = Annotation(
            class_label=label,
            annotation_type=AnnotationType.BOUNDING_BOX,
            bbox=BoundingBox(x=x, y=y, width=w, height=h),
        )
        record.annotations.append(ann)
        record.is_annotated = True
        record.annotation_stats = compute_annotation_stats(record)
        self._refresh_canvas_annotations()
        self._refresh_ann_list()
        self._refresh_stats()
        self._refresh_image_list_item(self._current_idx)

    def _on_delete_annotation(self) -> None:
        if self._session is None or self._current_idx < 0:
            return
        row = self._ann_list.currentRow()
        if row < 0:
            return
        record = self._session.images[self._current_idx]
        record.push_undo_snapshot()
        del record.annotations[row]
        record.is_annotated = bool(record.annotations)
        record.annotation_stats = compute_annotation_stats(record)
        self._refresh_canvas_annotations()
        self._refresh_ann_list()
        self._refresh_stats()

    def _on_undo(self) -> None:
        if self._session is None or self._current_idx < 0:
            return
        record = self._session.images[self._current_idx]
        if record.undo():
            record.is_annotated = bool(record.annotations)
            record.annotation_stats = compute_annotation_stats(record)
            self._refresh_canvas_annotations()
            self._refresh_ann_list()
            self._refresh_stats()

    def _on_redo(self) -> None:
        if self._session is None or self._current_idx < 0:
            return
        record = self._session.images[self._current_idx]
        if record.redo():
            record.is_annotated = bool(record.annotations)
            record.annotation_stats = compute_annotation_stats(record)
            self._refresh_canvas_annotations()
            self._refresh_ann_list()
            self._refresh_stats()

    def _on_next_image(self) -> None:
        if self._session and self._current_idx < len(self._session.images) - 1:
            self._select_image(self._current_idx + 1)

    def _on_prev_image(self) -> None:
        if self._session and self._current_idx > 0:
            self._select_image(self._current_idx - 1)

    def _on_save(self) -> None:
        if self._session is None or self._store is None:
            return
        try:
            self._store.save(self._session)
            self._update_status(saved=True)
        except Exception as exc:
            logger.error("Autosave failed: %s", exc)

    def _on_export_coco(self) -> None:
        self._run_export(export_coco, "COCO JSON")

    def _on_export_yolo(self) -> None:
        self._run_export(export_yolo, "YOLO TXT")

    def _on_export_csv(self) -> None:
        self._run_export(export_metadata_csv, "CSV")

    # ------------------------------------------------------------------
    # UI refresh helpers
    # ------------------------------------------------------------------

    def _refresh_image_list(self) -> None:
        self._image_list.clear()
        if self._session is None:
            return
        for record in self._session.images:
            icon = "✅" if record.is_annotated else "⬜"
            item = QListWidgetItem(f"{icon} {record.path.name}")
            self._image_list.addItem(item)

    def _refresh_image_list_item(self, idx: int) -> None:
        if self._session is None:
            return
        record = self._session.images[idx]
        icon = "✅" if record.is_annotated else "⬜"
        item = self._image_list.item(idx)
        if item:
            item.setText(f"{icon} {record.path.name}")

    def _refresh_class_combo(self) -> None:
        self._class_combo.clear()
        if self._session is None:
            return
        for label in self._session.class_labels:
            self._class_combo.addItem(label)
        if not self._session.class_labels:
            self._class_combo.addItem("object")

    def _refresh_canvas_annotations(self) -> None:
        if self._session is None or self._current_idx < 0:
            return
        record = self._session.images[self._current_idx]
        data = [
            (a.bbox.x, a.bbox.y, a.bbox.width, a.bbox.height, a.class_label)
            for a in record.annotations
            if a.bbox is not None
        ]
        self._canvas.render_annotations(data)

    def _refresh_ann_list(self) -> None:
        self._ann_list.clear()
        if self._session is None or self._current_idx < 0:
            return
        for ann in self._session.images[self._current_idx].annotations:
            bbox_info = (
                f"x={ann.bbox.x:.0f} y={ann.bbox.y:.0f} "
                f"w={ann.bbox.width:.0f} h={ann.bbox.height:.0f}"
                if ann.bbox
                else "no bbox"
            )
            self._ann_list.addItem(f"[{ann.class_label}] {bbox_info}")

    def _refresh_stats(self) -> None:
        if self._session is None or self._current_idx < 0:
            self._stats_label.setText("No annotations yet.")
            return
        s = self._session.images[self._current_idx].annotation_stats
        prog = (
            f"{self._session.annotated_count}/{self._session.total_count} "
            f"images annotated"
        )
        self._stats_label.setText(
            f"{prog}\n"
            f"Objects: {s.object_count}\n"
            f"Avg area: {s.avg_area_px:.0f}px ({s.avg_area_pct:.1f}%)\n"
            f"Classes: {s.class_distribution}"
        )

    def _update_status(self, *, saved: bool = False) -> None:
        msg = "Session saved." if saved else "Ready."
        if self._session:
            msg = (
                f"{self._session.project_name} — "
                f"{self._session.annotated_count}/{self._session.total_count} annotated"
                + (" — Saved" if saved else "")
            )
        self._status_bar.showMessage(msg, 3000 if saved else 0)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def _select_image(self, idx: int) -> None:
        self._image_list.setCurrentRow(idx)

    def _run_export(self, export_fn: object, label: str) -> None:
        if self._session is None:
            QMessageBox.warning(self, "No session", "Open a folder first.")
            return
        dest = QFileDialog.getExistingDirectory(self, f"Export {label} to…")
        if not dest:
            return
        try:
            result = export_fn(self._session, Path(dest))  # type: ignore[operator]
            QMessageBox.information(self, "Export complete", f"Saved to:\n{result}")
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))

    def _ask_project_name(self) -> tuple[str, bool | None]:
        name, ok = QInputDialog.getText(
            self,
            "Project name",
            "Enter a name for this annotation session:",
        )
        return name or "Untitled", ok
