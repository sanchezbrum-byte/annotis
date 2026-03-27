"""AnnotationCanvas: QGraphicsView for displaying images and drawing bboxes.

This widget is the only place where annotation geometry is CREATED.
All domain model mutations go through ImageRecord.push_undo_snapshot()
before changes so that undo/redo works correctly.

Coverage exclusion: UI components are not unit-tested; they are covered
by manual integration smoke-tests and optional pytest-qt tests.
"""

from __future__ import annotations

import logging

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QCursor, QMouseEvent, QPen, QWheelEvent
from PyQt6.QtWidgets import (
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
)

logger = logging.getLogger(__name__)

_PALETTE = (
    "#e6194b",
    "#3cb44b",
    "#4363d8",
    "#f58231",
    "#911eb4",
    "#42d4f4",
    "#f032e6",
    "#bfef45",
    "#fabed4",
    "#469990",
)


class AnnotationCanvas(QGraphicsView):
    """Interactive canvas for loading images and drawing bounding boxes.

    Signals:
        bbox_completed: Emitted with (x, y, width, height, class_label) when
            the user finishes drawing a bounding box.  class_label is always
            empty string here — the parent widget sets it.
    """

    bbox_completed = pyqtSignal(float, float, float, float)

    def __init__(self) -> None:
        super().__init__()
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

        self._draw_start: QPointF | None = None
        self._rubber_item: QGraphicsRectItem | None = None
        self._annotations: list[tuple[QRectF, str]] = []
        self._class_colors: dict[str, QColor] = {}
        self._next_color_idx = 0

    def load_pixmap(self, pixmap_item: QGraphicsPixmapItem) -> None:  # type: ignore[name-defined]  # noqa: F821
        """Replace the current image with *pixmap_item*.

        Args:
            pixmap_item: A QGraphicsPixmapItem to display.
        """
        self._scene.clear()
        self._annotations = []
        self._scene.addItem(pixmap_item)
        self.setSceneRect(pixmap_item.boundingRect())
        self._fit_in_view()

    def render_annotations(
        self,
        annotations: list[tuple[float, float, float, float, str]],
    ) -> None:
        """Draw bounding boxes over the current image.

        Removes all previously drawn annotation rectangles first.

        Args:
            annotations: List of (x, y, width, height, class_label) tuples.
        """
        for item in list(self._scene.items()):
            if isinstance(item, QGraphicsRectItem):
                self._scene.removeItem(item)

        for x, y, w, h, label in annotations:
            color = self._color_for_class(label)
            pen = QPen(color, 2)
            rect_item = QGraphicsRectItem(QRectF(x, y, w, h))
            rect_item.setPen(pen)
            self._scene.addItem(rect_item)

    def zoom_in(self) -> None:
        """Zoom in by 25 %."""
        self.scale(1.25, 1.25)

    def zoom_out(self) -> None:
        """Zoom out by 20 %."""
        self.scale(0.8, 0.8)

    def fit_image(self) -> None:
        """Fit the scene into the viewport at the best scale."""
        self._fit_in_view()

    # ------------------------------------------------------------------
    # Qt event overrides
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self._draw_start = self.mapToScene(event.pos())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
        if self._draw_start is not None:
            current = self.mapToScene(event.pos())
            rect = self._make_rect(self._draw_start, current)
            if self._rubber_item is None:
                pen = QPen(QColor("#ffffff"), 1, Qt.PenStyle.DashLine)
                self._rubber_item = QGraphicsRectItem(rect)
                self._rubber_item.setPen(pen)
                self._scene.addItem(self._rubber_item)
            else:
                self._rubber_item.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton and self._draw_start is not None:
            end = self.mapToScene(event.pos())
            rect = self._make_rect(self._draw_start, end)
            if rect.width() > 2 and rect.height() > 2:
                self.bbox_completed.emit(
                    rect.x(), rect.y(), rect.width(), rect.height()
                )
            if self._rubber_item is not None:
                self._scene.removeItem(self._rubber_item)
                self._rubber_item = None
            self._draw_start = None
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:  # type: ignore[override]
        factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
        self.scale(factor, factor)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fit_in_view(self) -> None:
        """Fit the entire scene into the viewport without distortion."""
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    @staticmethod
    def _make_rect(p1: QPointF, p2: QPointF) -> QRectF:
        """Return a normalised QRectF from two arbitrary corner points.  O(1)."""
        x = min(p1.x(), p2.x())
        y = min(p1.y(), p2.y())
        w = abs(p2.x() - p1.x())
        h = abs(p2.y() - p1.y())
        return QRectF(x, y, w, h)

    def _color_for_class(self, label: str) -> QColor:
        """Return a consistent colour for *label*, assigning one if new.  O(1)."""
        if label not in self._class_colors:
            hex_color = _PALETTE[self._next_color_idx % len(_PALETTE)]
            self._class_colors[label] = QColor(hex_color)
            self._next_color_idx += 1
        return self._class_colors[label]
