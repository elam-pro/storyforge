"""Editable geographic canvases backed by project locations and image references."""

from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
)


class GeographyMarkerItem(QGraphicsEllipseItem):
    """A movable marker; persistence happens once when the drag is released."""

    def __init__(self, row: dict, palette, on_select, on_move, on_edit):
        super().__init__(-10, -10, 20, 20)
        self.marker_id = int(row["id"])
        self.on_select = on_select
        self.on_move = on_move
        self.on_edit = on_edit
        color = QColor(row.get("color") or palette.accent)
        self.setPen(QPen(color.lighter(135), 2))
        self.setBrush(QBrush(color))
        self.setPos(float(row.get("x", 0)), float(row.get("y", 0)))
        self.setZValue(2)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        label = QGraphicsSimpleTextItem(row.get("display_label") or row.get("label") or "Repère", self)
        label.setBrush(QBrush(QColor(palette.text)))
        label.setPos(15, -10)
        label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        self.setToolTip(
            f"{row.get('display_label') or row.get('label') or 'Repère'}\n"
            f"{row.get('marker_type') or 'location'}\nGlisser pour déplacer · double-cliquer pour modifier"
        )

    def mousePressEvent(self, event) -> None:
        self.on_select(self.marker_id)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)
        self.on_move(self.marker_id, float(self.pos().x()), float(self.pos().y()))

    def mouseDoubleClickEvent(self, event) -> None:
        self.on_edit(self.marker_id)
        event.accept()


class GeographyView(QGraphicsView):
    def __init__(self, palette, on_select, on_move, on_edit, parent=None):
        super().__init__(parent)
        self.map_scene = QGraphicsScene(self)
        self.setScene(self.map_scene)
        self.palette = palette
        self.on_select = on_select
        self.on_move = on_move
        self.on_edit = on_edit
        self.marker_items: dict[int, GeographyMarkerItem] = {}
        self.has_background = False
        self.setObjectName("GeographyMapCanvas")
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setBackgroundBrush(QBrush(QColor(palette.surface_raised)))
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setToolTip("Glisse le fond pour te déplacer. Ctrl + molette pour zoomer.")

    def set_map(self, map_row: dict, markers: list[dict], background: QPixmap) -> None:
        self.map_scene.clear()
        self.marker_items = {}
        width = max(800.0, float(map_row.get("width", 1600)))
        height = max(560.0, float(map_row.get("height", 1000)))
        self.map_scene.setSceneRect(0, 0, width, height)
        self.has_background = not background.isNull()
        if self.has_background:
            scaled = background.scaled(
                QSize(int(width), int(height)),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            item = QGraphicsPixmapItem(scaled)
            item.setPos((width - scaled.width()) / 2, (height - scaled.height()) / 2)
            item.setZValue(-2)
            self.map_scene.addItem(item)
        for marker in markers:
            item = GeographyMarkerItem(
                marker, self.palette, self.on_select, self.on_move, self.on_edit
            )
            self.map_scene.addItem(item)
            self.marker_items[item.marker_id] = item

    def drawBackground(self, painter, rect) -> None:
        super().drawBackground(painter, rect)
        if self.has_background:
            return
        grid = 50
        left = math.floor(rect.left() / grid) * grid
        top = math.floor(rect.top() / grid) * grid
        painter.setPen(QPen(QColor(self.palette.border), 0.8))
        x = left
        while x < rect.right():
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
            x += grid
        y = top
        while y < rect.bottom():
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            y += grid

    def center_content(self) -> None:
        self.resetTransform()
        if self.marker_items:
            bounds = QRectF()
            for item in self.marker_items.values():
                bounds = bounds.united(item.sceneBoundingRect()) if not bounds.isNull() else item.sceneBoundingRect()
            self.centerOn(bounds.center())
        else:
            self.centerOn(self.map_scene.sceneRect().center())

    def center_position(self) -> QPointF:
        return self.mapToScene(self.viewport().rect().center())

    def wheelEvent(self, event) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.12 if event.angleDelta().y() > 0 else 0.89
            current = self.transform().m11()
            if 0.25 <= current * factor <= 4.0:
                self.scale(factor, factor)
            event.accept()
            return
        super().wheelEvent(event)


def render_geography_map(
    path: Path,
    map_row: dict,
    markers: list[dict],
    background: QPixmap,
    palette,
) -> None:
    """Render one portable map image without depending on the visible workspace."""

    source_width = min(4000.0, max(800.0, float(map_row.get("width", 1600))))
    source_height = min(3000.0, max(560.0, float(map_row.get("height", 1000))))
    scale = min(1.0, 2200.0 / source_width, 1500.0 / source_height)
    width = max(1, round(source_width * scale))
    height = max(1, round(source_height * scale))
    image = QImage(width, height, QImage.Format.Format_ARGB32)
    image.fill(QColor(palette.surface_raised))
    painter = QPainter(image)
    try:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        if not background.isNull():
            scaled = background.scaled(
                QSize(width, height),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(
                round((width - scaled.width()) / 2),
                round((height - scaled.height()) / 2),
                scaled,
            )
        else:
            step = max(12.0, 50.0 * scale)
            painter.setPen(QPen(QColor(palette.border), 1))
            x = 0.0
            while x <= width:
                painter.drawLine(QPointF(x, 0), QPointF(x, height))
                x += step
            y = 0.0
            while y <= height:
                painter.drawLine(QPointF(0, y), QPointF(width, y))
                y += step

        painter.setFont(QFont("DejaVu Sans", 10))
        for marker in markers:
            x = min(width, max(0.0, float(marker.get("x", 0)) * scale))
            y = min(height, max(0.0, float(marker.get("y", 0)) * scale))
            color = QColor(marker.get("color") or palette.accent)
            if not color.isValid():
                color = QColor(palette.accent)
            radius = max(7.0, 10.0 * scale)
            painter.setPen(QPen(color.lighter(135), 2))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(x, y), radius, radius)
            painter.setPen(QPen(QColor(palette.text), 1))
            label = str(
                marker.get("display_label")
                or marker.get("label")
                or marker.get("location_name")
                or "Repère"
            )
            painter.drawText(
                QRectF(x + radius + 5, y - 15, min(360.0, width - x), 44),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                label,
            )
    finally:
        painter.end()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not image.save(str(path), "PNG"):
        raise OSError(f"Impossible d’enregistrer la carte : {path}")
