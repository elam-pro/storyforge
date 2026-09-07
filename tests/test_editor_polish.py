import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from app import StoryForgeWindow
from db import NOW


def test_scene_completion_enter_and_repeated_new_scene(tmp_path):
    qt = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "editor.db")
    project = window.db.run("INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)",
                            (NOW(), "Test", "Idée")).lastrowid
    window.active_project = project
    window.show_script_editor()
    window.show()
    qt.processEvents()
    for typed, expected in [("IN", "INT."), ("E", "EXT."), ("EX", "EXT.")]:
        window.script_text.clear()
        window._set_script_element_mode("scene")
        window._apply_script_block_format("scene")
        QTest.keyClicks(window.script_text, typed)
        QTest.keyClick(window.script_text, Qt.Key.Key_Tab)
        qt.processEvents()
        assert window.script_text.toPlainText() == expected
        assert not window.script_text._type_rail.isVisible()
    window.script_text.clear()
    window._set_script_element_mode("action")
    window._apply_script_block_format("action")
    QTest.keyClicks(window.script_text, "Elle ouvre la porte.")
    QTest.keyClick(window.script_text, Qt.Key.Key_Return)
    assert window._infer_script_element_from_cursor() == "character"
    window.script_text.clear()
    for _ in range(7):
        window._insert_script_scene()
    window._sync_script_document_from_editor()
    elements = window.script_document.elements()
    assert len(elements) == 7
    assert all(kind == "Scene Heading" for kind, text in elements)
    window._save_script(silent=True)
    window.show_story_overview()
    qt.processEvents()
    assert window.overview_script_excerpt.toPlainText().count("INT. LIEU - JOUR") == 7
    window._toggle_project_navigation()
    assert window.nav_buttons["characters"].isHidden()
    window._toggle_project_navigation()
    assert not window.nav_buttons["characters"].isHidden()
    window.show_genres()
    qt.processEvents()
    assert window.current_view == "genres"
    window.close()


def test_english_navigation_preserves_user_text_and_setting(tmp_path):
    from db import Database
    from PySide6.QtWidgets import QPushButton
    qt = QApplication.instance() or QApplication([])
    path = tmp_path / "english.db"
    db = Database(path)
    db.set_setting("interface_language", "en")
    db.set_setting("project_navigation_expanded", "0")
    project = db.run("INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)",
                     (NOW(), "Personnages", "Idée")).lastrowid
    db.conn.close()
    window = StoryForgeWindow(path)
    window.active_project = project
    window._update_project_chips()
    assert window.project_chip.currentText() == "Personnages"
    assert window.nav_buttons["characters"].nav_title_label.text() == "Characters"
    assert window.nav_buttons["characters"].isHidden()
    window.show_characters()
    assert window.character_tabs.tabText(0) == "Essentials"
    assert any(button.text() == "Save" for button in window.findChildren(QPushButton))
    window.show_settings()
    window.settings_language.setCurrentIndex(window.settings_language.findData("fr"))
    window._save_settings()
    qt.processEvents()
    assert window.db.setting("interface_language") == "fr"
    assert window.nav_buttons["characters"].nav_title_label.text() == "Personnages"
    window.close()
