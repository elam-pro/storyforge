import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QColor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QGraphicsPixmapItem
from storyforge.app import StoryForgeWindow, TEMPLATE_LIBRARY
from storyforge.db import NOW
from storyforge.template_diagrams import DIAGRAM_FAMILIES, build_diagram
from storyforge.theme import DARK


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


def test_every_template_uses_a_distinct_native_diagram_family():
    qt = QApplication.instance() or QApplication([])
    assert set(DIAGRAM_FAMILIES) == {template["key"] for template in TEMPLATE_LIBRARY}
    assert len(set(DIAGRAM_FAMILIES.values())) == len(TEMPLATE_LIBRARY)

    for template in TEMPLATE_LIBRARY:
        view = build_diagram(template, DARK)
        assert view.property("diagramFamily") == DIAGRAM_FAMILIES[template["key"]]
        assert len(view.scene().items()) > len(template["steps"])
        assert not view.sceneRect().isEmpty()
        view.deleteLater()
    qt.processEvents()


def test_primary_workspaces_respect_the_minimum_supported_window(tmp_path):
    qt = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "small-window.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage,updated_at) VALUES(?,?,?,?)",
        (NOW(), "Fenêtre compacte", "Idée", NOW()),
    ).lastrowid
    window.active_project = int(project_id)
    window.resize(1120, 720)
    window.show()

    for show_view in (
        window.show_guides,
        window.show_story_overview,
        window.show_locations,
        window.show_characters,
        window.show_images,
        window.show_script_editor,
    ):
        show_view()
        qt.processEvents()
        page = window.page_host_layout.itemAt(0).widget()
        assert page.width() <= window.page_host.width()
        assert page.height() <= window.page_host.height()

    window.autosave_timer.stop()
    window.close()
    qt.processEvents()
