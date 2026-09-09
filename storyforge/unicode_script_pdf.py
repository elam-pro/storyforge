"""Embedded-font rendering for screenplays outside the legacy WinAnsi range."""
from PySide6.QtCore import QIODevice, QMarginsF, QPointF, QSaveFile
from PySide6.QtGui import QFont, QFontMetricsF, QPageLayout, QPageSize, QPainter, QPdfWriter
from PySide6.QtWidgets import QApplication


def render(path, pages, title, author, contact, date, based_on, copyright, cover):
    # Application runtime already owns QApplication; retain one for CLI exports.
    app = QApplication.instance() or QApplication([])
    output = QSaveFile(str(path))
    if not output.open(QIODevice.OpenModeFlag.WriteOnly):
        raise OSError(output.errorString())
    writer = QPdfWriter(output)
    writer.setResolution(72)
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.Letter))
    writer.setPageMargins(QMarginsF(0, 0, 0, 0), QPageLayout.Unit.Point)
    writer.setTitle(title)
    writer.setCreator('StoryForge')
    painter = QPainter(writer)
    if not painter.isActive():
        output.cancelWriting()
        raise OSError('Impossible de créer le PDF')

    def draw(text, x, y, bold=False, size=12, centered=False):
        font = QFont('DejaVu Sans Mono', size)
        font.setBold(bold)
        painter.setFont(font)
        width = QFontMetricsF(font, writer).horizontalAdvance(text)
        if centered:
            x = (612 - width) / 2
        painter.drawText(QPointF(x, 792 - y), text)

    try:
        if cover:
            from textwrap import wrap
            y = 510
            for value, bold in ((title.upper(), True), ('Écrit par' if author else '', False), (author, False), (based_on, False)):
                for line in wrap(value, 46):
                    draw(line, 0, y, bold, centered=True)
                    y -= 18
                y -= 18
            lines = [line for value in (contact, copyright) for source in value.splitlines() for line in wrap(source, 44)]
            if len(lines) > 20 or y < 200:
                raise ValueError('Page de garde trop longue : réduire les informations de couverture.')
            y = max(118, 54 + len(lines) * 13)
            for line in lines:
                draw(line, 72, y, size=10)
                y -= 13
            for i, line in enumerate(wrap(date, 26)):
                draw(line, 360, 160 - i * 13, size=10)
            if not writer.newPage():
                raise OSError('Échec de pagination PDF')
        for number, page in enumerate(pages, 1):
            if number > 1 and not writer.newPage():
                raise OSError('Échec de pagination PDF')
            for x, y, text, bold in page:
                draw(text, x, y, bold)
            if number > 1:
                draw(f'{number}.', 525, 756, size=10)
        painter.end()
        del writer
        if not output.commit():
            raise OSError(output.errorString())
    except BaseException:
        if painter.isActive():
            painter.end()
        output.cancelWriting()
        raise
