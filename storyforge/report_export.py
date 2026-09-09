"""Paginated, Unicode project reports using the application's Qt runtime."""
from pathlib import Path

from PySide6.QtCore import QRectF, Qt, QMarginsF
from PySide6.QtGui import QFont, QPainter, QPageLayout, QPageSize, QPdfWriter, QTextDocument


def export_report_pdf(path: Path, markdown: str, project_title: str) -> None:
    writer = QPdfWriter(str(path))
    writer.setResolution(96)
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setPageMargins(QMarginsF(22, 22, 22, 22), QPageLayout.Unit.Millimeter)
    writer.setTitle(project_title)
    writer.setCreator("StoryForge")
    width, height = writer.width(), writer.height()
    header, footer = 40, 35
    body_height = height - header - footer
    document = QTextDocument()
    document.setDefaultFont(QFont("DejaVu Sans", 11))
    document.setDefaultStyleSheet(
        "body { color: #202020; } h1 { font-size: 24pt; margin-bottom: 22px; }"
        "h2 { font-size: 16pt; margin-top: 24px; margin-bottom: 12px; }"
        "h3 { font-size: 12pt; margin-top: 18px; } p { margin-bottom: 12px; }"
        "table { border-collapse: collapse; } td, th { padding: 7px; }"
    )
    document.setMarkdown(markdown)
    from PySide6.QtCore import QSizeF
    document.setPageSize(QSizeF(width, body_height))
    painter = QPainter(writer)
    try:
        for page in range(document.pageCount()):
            if page:
                writer.newPage()
            painter.setPen(Qt.GlobalColor.darkGray)
            painter.setFont(QFont("DejaVu Sans", 9))
            painter.drawText(QRectF(0, 0, width, 25), Qt.AlignmentFlag.AlignLeft, project_title)
            painter.drawLine(0, 29, width, 29)
            painter.save()
            painter.setClipRect(QRectF(0, header, width, body_height))
            painter.translate(0, header - page * body_height)
            document.drawContents(painter, QRectF(0, page * body_height, width, body_height))
            painter.restore()
            painter.drawText(QRectF(0, height - 25, width, 25), Qt.AlignmentFlag.AlignRight,
                             f"StoryForge  ·  {page + 1} / {document.pageCount()}")
    finally:
        painter.end()
