"""Bounded, disposable previews; originals remain in SQLite, unchanged."""
from collections import OrderedDict
from PySide6.QtCore import QByteArray, QBuffer, QIODevice, QSize, Qt
from PySide6.QtGui import QImageReader, QPixmap


class PixmapCache:
    def __init__(self, max_bytes=48 * 1024 * 1024):
        self.max_bytes = max_bytes
        self.bytes_used = 0
        self._items = OrderedDict()

    def get(self, key, default=None):
        if key not in self._items:
            return default
        self._items.move_to_end(key)
        return self._items[key][0]

    def __contains__(self, key):
        return key in self._items

    def pop(self, key, default=None):
        item = self._items.pop(key, None)
        if item is None:
            return default
        self.bytes_used -= item[1]
        return item[0]

    def __setitem__(self, key, pixmap):
        self.pop(key)
        cost = max(1, pixmap.width() * pixmap.height() * max(1, pixmap.depth() // 8))
        if cost > self.max_bytes:
            return
        while self._items and self.bytes_used + cost > self.max_bytes:
            self.pop(next(iter(self._items)))
        self._items[key] = (pixmap, cost)
        self.bytes_used += cost

    def clear(self):
        self._items.clear()
        self.bytes_used = 0


def decode_preview(data, size=QSize(1800, 1400)):
    buffer = QBuffer()
    buffer.setData(QByteArray(data))
    buffer.open(QIODevice.OpenModeFlag.ReadOnly)
    reader = QImageReader(buffer)
    reader.setAutoTransform(True)
    original = reader.size()
    if original.isValid() and (original.width() > size.width() or original.height() > size.height()):
        reader.setScaledSize(original.scaled(size, Qt.AspectRatioMode.KeepAspectRatio))
    image = reader.read()
    if image.isNull():
        return QPixmap()
    pixmap = QPixmap.fromImage(image)
    # Some codecs cannot downsample while decoding, and EXIF may swap axes.
    if pixmap.width() > size.width() or pixmap.height() > size.height():
        pixmap = pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    return pixmap
