"""Synthetic JPEG benchmark, no Database or personal files. Run from repo root."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from statistics import median
from time import perf_counter
from PySide6.QtCore import QByteArray, QBuffer, QIODevice, QSize, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication
from storyforge.image_previews import decode_preview, PixmapCache


def main():
    app = QApplication.instance() or QApplication([])
    image = QImage(5000, 3500, QImage.Format.Format_RGB32)
    image.fill(0xff325a8f)
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, 'JPEG')
    payload = bytes(data)
    def old():
        pixmap = QPixmap()
        pixmap.loadFromData(payload)
        return pixmap.scaled(QSize(1800, 1400), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    cache = PixmapCache()
    cache[1] = decode_preview(payload)
    for label, operation in [('full decode then scale', old), ('scaled decoder', lambda: decode_preview(payload)), ('warm cache', lambda: cache.get(1))]:
        times = []
        for _ in range(15):
            start = perf_counter()
            result = operation()
            times.append((perf_counter() - start) * 1000)
        print(f'{label}: median={median(times):.3f}ms p95={sorted(times)[-1]:.3f}ms')
    print(f'cached pixel bytes={cache.bytes_used}; budget={cache.max_bytes}')


if __name__ == '__main__':
    main()
