from PySide6.QtCore import QByteArray, QBuffer, QIODevice, QSize
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication
from storyforge.image_previews import PixmapCache, decode_preview


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
    from storyforge.app import StoryForgeWindow
    class View:
        _location_image_refresh_generation = 3
        location_id = 8
        def _show_location_image_row(self, row):
            raise AssertionError('stale callback painted')
    StoryForgeWindow._show_deferred_location_image(View(), 2, {}, 8)
    StoryForgeWindow._show_deferred_location_image(View(), 3, {}, 7)


def test_image_library_decodes_a_bounded_thumbnail_once(tmp_path, monkeypatch):
    import storyforge.app as app_module
    from storyforge.app import StoryForgeWindow
    from storyforge.db import NOW

    qt = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "library.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage,updated_at) VALUES(?,?,?,?)",
        (NOW(), "Images lourdes", "Idée", NOW()),
    ).lastrowid
    data = fixture_jpeg()
    image_id = window.db.run(
        """INSERT INTO image_library(
        project_id,title,category,notes,file_name,mime_type,image_data,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?,?,?)""",
        (project_id, "Décor", "Lieu / décor", "", "decor.jpg", "image/jpeg", data, NOW(), NOW()),
    ).lastrowid
    window.active_project = int(project_id)

    calls = 0
    original = app_module.decode_preview

    def counted_decode(source, size=QSize(1800, 1400)):
        nonlocal calls
        calls += 1
        return original(source, size)

    monkeypatch.setattr(app_module, "decode_preview", counted_decode)
    window.show_images()
    qt.processEvents()
    window._refresh_library_images()

    assert calls == 1
    thumbnail = window._image_library_thumbnail_cache.get(int(image_id))
    assert thumbnail.width() <= 170 and thumbnail.height() <= 105
    assert window._image_library_thumbnail_cache.bytes_used <= 8 * 1024 * 1024

    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    qt.processEvents()
