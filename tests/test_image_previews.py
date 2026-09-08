from PySide6.QtCore import QByteArray, QBuffer, QIODevice, QSize
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication
from image_previews import PixmapCache, decode_preview


def fixture_jpeg():
    image = QImage(5000, 3500, QImage.Format.Format_RGB32)
    image.fill(0xff325a8f)
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    assert image.save(buffer, 'JPEG')
    return bytes(data)


def test_preview_bounds_and_original_unchanged():
    app = QApplication.instance() or QApplication([])
    data = fixture_jpeg()
    copy = bytes(data)
    preview = decode_preview(data, QSize(180, 140))
    assert preview.width() <= 180 and preview.height() <= 140
    assert not preview.isNull() and data == copy
    assert decode_preview(b'invalid').isNull()


def test_memory_budget_lru_replacement_and_clear():
    app = QApplication.instance() or QApplication([])
    cache = PixmapCache(800)
    pixmap = QPixmap(10, 10)
    pixmap.fill()
    cache[1] = pixmap
    cache[2] = pixmap
    cache.get(1)
    cache[3] = pixmap
    assert cache.get(2) is None
    assert cache.get(1) is not None
    cache[1] = pixmap
    assert cache.bytes_used == 800
    cache[4] = QPixmap(100, 100)
    assert cache.get(4) is None
    cache.clear()
    assert cache.bytes_used == 0 and cache.get(1) is None


def test_obsolete_location_preview_cannot_paint():
    from app import StoryForgeWindow
    class View:
        _location_image_refresh_generation = 3
        location_id = 8
        def _show_location_image_row(self, row):
            raise AssertionError('stale callback painted')
    StoryForgeWindow._show_deferred_location_image(View(), 2, {}, 8)
    StoryForgeWindow._show_deferred_location_image(View(), 3, {}, 7)
