import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QColor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QGraphicsPixmapItem
from app import StoryForgeWindow, TEMPLATE_LIBRARY
from db import NOW


def test_margins_centered_script_and_nonoverlapping_popup(tmp_path):
    qt = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "layout.db")
    window.active_project = window.db.run("INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)",
                                         (NOW(), "Test", "Idée")).lastrowid
    window.resize(1600,1000)
    window.show()
    for show in (window.show_search, window.show_story_overview, window.show_form_templates):
        show()
        qt.processEvents()
        page = window.page_host_layout.itemAt(0).widget()
        margins = page.layout().contentsMargins()
        assert (margins.left(), margins.top(), margins.right()) == (22,18,22)
    window.show_story_overview()
    window.overview_tabs.setCurrentIndex(5)
    qt.processEvents()
    editor = window.overview_script_excerpt
    assert editor.width() <= 820
    assert abs(editor.geometry().center().x() - editor.parentWidget().rect().center().x()) <= 2
    window.show_script_editor()
    window.script_text.clear()
    window._set_script_element_mode("scene")
    window._apply_script_block_format("scene")
    QTest.keyClicks(window.script_text, "IN")
    qt.processEvents()
    popup = window.script_scene_completer.popup()
    assert popup.isVisible()
    caret = window.script_text.cursorRect()
    caret.moveTopLeft(window.script_text.viewport().mapToGlobal(caret.topLeft()))
    assert not popup.geometry().intersects(caret)
    QTest.keyClick(window.script_text, Qt.Key.Key_Tab)
    assert window.script_text.toPlainText() == "INT."
    window.close()


def test_template_custom_image_persists_without_source_file(tmp_path):
    qt = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "images.db")
    source = tmp_path / "custom.png"
    image = QImage(640,480,QImage.Format.Format_RGB32)
    image.fill(QColor("#dd8822"))
    assert image.save(str(source))
    key = TEMPLATE_LIBRARY[0]["key"]
    window._store_template_visual(key, str(source))
    original = window.db.setting(f"template_image_{key}")
    source.unlink()
    window.close()
    reopened = StoryForgeWindow(tmp_path / "images.db")
    view = reopened._build_template_visual_view(TEMPLATE_LIBRARY[0])
    assert any(isinstance(item,QGraphicsPixmapItem) for item in view.scene().items())
    assert reopened.db.setting(f"template_image_{key}") == original
    assert not reopened.db.setting(f"template_image_{TEMPLATE_LIBRARY[1]['key']}", "")
    reopened._reset_template_visual(key)
    assert not reopened.db.setting(f"template_image_{key}", "")
    qt.processEvents()
    reopened.close()
