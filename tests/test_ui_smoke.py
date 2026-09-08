import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QPixmap, QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QInputDialog,
    QPushButton,
    QSizePolicy,
    QTextEdit,
)

from app import (
    APP_VERSION,
    CURRICULUM,
    DEVELOPMENT_DOCUMENTS,
    LEARNING_SESSION,
    STORY_MAP_STEPS,
    SYNOPSIS_STEPS,
    TEMPLATE_LIBRARY,
    RelationshipMapDialog,
    SequenceBlockWidget,
    StoryForgeWindow,
    TimelineEventItem,
)
from db import NOW, Database


def test_every_main_view_opens_without_mutating_user_data(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "ui.db")
    window.show()
    app.processEvents()

    assert APP_VERSION == "0.30.3"
    assert len(LEARNING_SESSION.steps) == 14
    assert [key for key, _title in DEVELOPMENT_DOCUMENTS] == [
        "premise",
        "logline",
        "summary",
        "story_map",
        "synopsis",
        "treatment",
        "beats",
        "outline",
        "scenes",
        "script",
    ]
    assert [step["title"] for step in STORY_MAP_STEPS] == [
        "Situation de départ",
        "Événement qui dérègle",
        "Objectif",
        "Premières actions",
        "Obstacles et conséquences",
        "Aggravation",
        "Choix difficile",
        "Confrontation finale",
        "Résolution et changement",
    ]
    assert [step["part"] for step in SYNOPSIS_STEPS] == [
        "Début",
        "Début",
        "Développement",
        "Développement",
        "Fin",
        "Fin",
    ]
    assert [phase["key"] for phase in CURRICULUM] == [
        "foundations",
        "short_one",
        "short_two",
        "longer_projects",
    ]
    assert [len(phase["steps"]) for phase in CURRICULUM] == [10, 10, 8, 10]
    assert "ai" not in window.nav_buttons
    assert "questions" not in window.nav_buttons
    assert window.nav_buttons["search"].accessibleName() == "Rechercher"
    assert window.nav_buttons["learning"].accessibleName() == "Guides d’écriture"
    assert window.nav_buttons["guide_runs"].accessibleName() == "Guides en cours"
    assert window.nav_buttons["guide_runs"].property("navChild") is True
    assert window.nav_buttons["development"].accessibleName() == "Construction"
    assert window.nav_buttons["overview"].accessibleName() == "Vue d’ensemble"
    assert window.nav_buttons["overview"].property("navChild") is True
    assert window.nav_buttons["timeline"].accessibleName() == "Chronologie"
    assert window.nav_buttons["universe"].accessibleName() == "Univers"
    assert window.nav_buttons["locations"].accessibleName() == "Lieux"
    assert window.nav_buttons["locations"].property("navChild") is True
    assert window.nav_buttons["characters"].accessibleName() == "Personnages"
    assert window.nav_buttons["arcs"].accessibleName() == "Arcs"
    assert window.nav_buttons["arcs"].property("navChild") is True
    assert window.nav_buttons["promises"].accessibleName() == "Accroche et promesses"
    assert window.nav_buttons["promises"].property("navChild") is True
    assert window.nav_buttons["theme"].accessibleName() == "Thème"
    assert window.nav_buttons["theme"].property("navChild") is True
    assert window.nav_buttons["conflicts"].accessibleName() == "Conflits"
    assert window.nav_buttons["conflicts"].property("navChild") is True
    assert window.nav_buttons["conflicts"].nav_icon_label.text() == "×"
    assert window.nav_buttons["images"].accessibleName() == "Images"
    assert window.nav_buttons["script_editor"].accessibleName() == "Éditeur de scripts"
    assert window.nav_buttons["templates"].accessibleName() == "Templates"
    assert window.nav_buttons["glossary"].accessibleName() == "Glossaire"
    assert window.sidebar.width() == 236
    assert window.nav_buttons["characters"].nav_title_label.text() == "Personnages"
    assert window.nav_buttons["characters"].nav_title_label.isVisible()
    assert window.nav_buttons["home"].height() == 44
    app.processEvents()
    home_bottom = window.nav_buttons["home"].geometry().bottom()
    ideas_top = window.nav_buttons["ideas"].geometry().top()
    assert ideas_top > home_bottom
    window.toggle_sidebar()
    assert not window.sidebar.isHidden()
    assert window.sidebar.width() == 54
    assert not window.nav_buttons["characters"].nav_title_label.isVisible()
    assert window.nav_buttons["characters"].nav_icon_label.text() == "♙"
    assert window.db.setting("sidebar_expanded", "1") == "0"
    window.toggle_sidebar()
    assert window.sidebar.width() == 236
    assert window.db.setting("sidebar_expanded", "0") == "1"
    # The active row may change its styling, but must not change the layout
    # height and push neighbouring entries into one another.
    window.show_locations()
    app.processEvents()
    assert {button.height() for button in window.nav_buttons.values()} == {44}
    assert {"mckee_value_progression", "truby_seven_steps"}.issubset(
        {template["key"] for template in TEMPLATE_LIBRARY}
    )
    for callback in (
        window.show_home,
        window.show_search,
        window.show_guides,
        window.show_learning,
        window.show_development,
        window.show_ideas,
        window.show_projects,
        window.show_story_overview,
        window.show_timeline,
        window.show_universe,
        window.show_locations,
        window.show_arcs,
        window.show_promises,
        window.show_theme,
        window.show_conflicts,
        window.show_form_templates,
        window.show_templates,
        window.show_glossary,
    ):
        callback()
        app.processEvents()

    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage,protagonist,objective,opposition,stakes) VALUES(?,?,?,?,?,?,?)",
        (NOW(), "La dernière lettre", "Noyau", "Mina", "livrer une lettre", "la ville est fermée", "son frère part à l’aube"),
    ).lastrowid
    window.active_project = project_id
    window.db.set_setting("active_project", str(project_id))
    window._update_project_chips()

    window.db.ensure_doc(project_id, "summary", "Résumé très court")
    window.db.save_doc(project_id, "summary", "Mina accepte de traverser une ville fermée.")
    window.db.set_setting("development_document", "short_summary")
    window.show_development()
    app.processEvents()
    assert window.development_doc_type == "summary"
    assert window.development_text.toPlainText().startswith("Mina accepte")
    window._switch_development_document("premise")
    app.processEvents()
    window.development_text.setPlainText("Une messagère doit livrer la dernière lettre avant l’aube.")
    window._save_development_document()
    window._switch_development_document("outline")
    app.processEvents()
    assert window.current_view == "development"
    assert window.db.setting(f"last_development_doc_{project_id}") == "outline"
    assert window.db.one(
        "SELECT content FROM project_docs WHERE project_id=? AND doc_type='premise'",
        (project_id,),
    )[0].startswith("Une messagère")
    assert window.outline_tree.columnCount() == 6
    window._set_outline_mode("sequences")
    app.processEvents()
    assert window.sequence_list.count() == 0
    window._add_sequence_block()
    sequence_item = window.sequence_list.item(0)
    sequence_widget = window.sequence_list.itemWidget(sequence_item)
    assert isinstance(sequence_widget, SequenceBlockWidget)
    sequence_widget.title.setText("Mina reçoit la lettre")
    sequence_widget.purpose.setText("Dérégler sa nuit")
    sequence_widget.events.setPlainText("Une lettre interdite arrive au centre de tri.")
    sequence_widget.consequence.setPlainText("Mina décide de sortir avant l’aube.")
    window._save_sequence_board()
    saved_sequence = window.db.one(
        "SELECT * FROM sequence_blocks WHERE project_id=?",
        (project_id,),
    )
    assert saved_sequence["title"] == "Mina reçoit la lettre"
    assert "Une lettre interdite" in window.db.one(
        "SELECT content FROM project_docs WHERE project_id=? AND doc_type='outline'",
        (project_id,),
    )[0]

    window.db.ensure_doc(project_id, "story_map", "Carte de l’histoire")
    window.db.save_doc(project_id, "story_map", "Ancienne carte libre à préserver.")
    window._switch_development_document("story_map")
    app.processEvents()
    assert window.story_map_mode == "board"
    assert not window.story_map_items
    window._show_story_map_guide()
    app.processEvents()
    assert window.story_map_step_index == 0
    window.story_map_text.setPlainText("Mina trie les lettres impossibles à livrer.")
    window._next_story_map_step()
    app.processEvents()
    assert window.story_map_step_index == 1
    assert window.db.one(
        "SELECT answer FROM story_map_answers WHERE project_id=? AND step_key='starting_situation'",
        (project_id,),
    )[0].startswith("Mina trie")
    for step in STORY_MAP_STEPS[1:-1]:
        window.db.save_story_map_answer(project_id, step["key"], f"Réponse causale pour {step['title']}.")
    window.db.set_setting(f"story_map_step_{project_id}", len(STORY_MAP_STEPS) - 1)
    window.show_development()
    app.processEvents()
    window.story_map_text.setPlainText("La lettre est remise et Mina choisit désormais d’agir.")
    window._finish_story_map(show_dialog=False)
    story_map = window.db.one(
        "SELECT content FROM project_docs WHERE project_id=? AND doc_type='story_map'",
        (project_id,),
    )[0]
    assert "01. SITUATION DE DÉPART" in story_map
    assert "09. RÉSOLUTION ET CHANGEMENT" in story_map
    assert window.db.one("SELECT stage FROM projects WHERE id=?", (project_id,))[0] == "Carte"
    assert window.db.one(
        "SELECT content FROM doc_versions WHERE project_id=? AND doc_type='story_map'",
        (project_id,),
    )[0] == "Ancienne carte libre à préserver."
    window._show_story_map_board()
    app.processEvents()
    assert window.story_map_mode == "board"
    assert len(window.story_map_items) == len(STORY_MAP_STEPS)
    assert len(window.story_map_link_items) == len(STORY_MAP_STEPS) - 1
    assert window.story_map_view.viewportUpdateMode() == window.story_map_view.ViewportUpdateMode.FullViewportUpdate
    assert window.story_map_view.dragMode() == window.story_map_view.DragMode.ScrollHandDrag
    assert not window.story_map_view.mask().isEmpty()
    assert not window.story_map_view.mask().contains(QPoint(0, 0))
    assert window.story_map_view.mask().contains(window.story_map_view.rect().center())
    first_card = min(window.story_map_items.values(), key=lambda item: item.node_id)
    first_card.setPos(125, 135)
    window._move_story_map_card(first_card)
    saved_position = window.db.one("SELECT x,y FROM story_map_nodes WHERE id=?", (first_card.node_id,))
    assert saved_position["x"] == 125
    assert saved_position["y"] == 135
    previous_right = window.story_map_scene.sceneRect().right()
    previous_scroll = window.story_map_view.horizontalScrollBar().value()
    first_card.setPos(previous_right - 100, 135)
    window._drag_story_map_card(first_card)
    window._apply_story_map_auto_pan()
    assert window.story_map_scene.sceneRect().right() > previous_right
    assert window.story_map_view.horizontalScrollBar().value() > previous_scroll
    window._finish_story_map_drag()

    expected = {
        window.show_characters: "characters",
        window.show_images: "images",
        window.show_script_editor: "script_editor",
        window.show_workshop: "workshop",
        window.show_rewrite: "rewrite",
        window.show_path: "path",
        window.show_settings: "settings",
        window.show_form_templates: "form_templates",
        window.show_templates: "templates",
    }
    for callback, view_name in expected.items():
        callback()
        app.processEvents()
        assert window.current_view == view_name

    window._select_path_phase("short_two")
    app.processEvents()
    assert window.current_view == "path"
    assert window.db.setting("path_phase") == "short_two"

    window.settings_theme.setCurrentIndex(window.settings_theme.findData("dark"))
    window.settings_autosave.setCurrentIndex(window.settings_autosave.findData(30))
    window._save_settings()
    assert window.mode == "dark"
    assert window.autosave_seconds == 30

    window.show_learning()
    window.learning_draft.setPlainText("Une messagère doit livrer une lettre avant l’aube.")
    window._save_learning_work(silent=True, status="terminé")
    saved = window.db.one("SELECT * FROM learning_work WHERE session_key='session01' AND step_index=0")
    assert saved["status"] == "terminé"
    assert saved["draft"].startswith("Une messagère")

    window._learning_step(2)
    window.learning_draft.setPlainText("Mina, une messagère qui refuse d’abandonner.")
    window._save_learning_work(silent=True, status="terminé")
    assert window.db.one("SELECT protagonist FROM projects WHERE id=?", (project_id,))[0] == "Mina"
    assert window.db.one(
        "SELECT answer FROM project_questions WHERE project_id=? AND question_key='center'",
        (project_id,),
    ) is None
    manual_text = "\n".join(body for _title, body in window._manual_sections())
    assert "Qui est le protagoniste" in manual_text
    assert "Mina, une messagère" in manual_text
    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_form_template_can_be_applied_and_saved_on_character(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "form-template-ui.db")
    project_id = window._create_empty_project(
        {
            "title": "Les odeurs de la ville",
            "project_type": "film",
            "story_format": "short",
            "target_duration": 12,
            "start_mode": "free",
        }
    )
    character_id = window.db.run(
        """INSERT INTO characters(project_id,name,role,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, "Mina", "Protagoniste", NOW(), NOW()),
    ).lastrowid
    template_id = window.db.run(
        """INSERT INTO form_templates(name,target_type,description,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        ("Fiche sensorielle", "character", "Compléments utiles", NOW(), NOW()),
    ).lastrowid
    section_id = window.db.run(
        "INSERT INTO form_template_sections(template_id,title,position) VALUES(?,?,?)",
        (template_id, "Perception", 0),
    ).lastrowid
    field_id = window.db.run(
        """INSERT INTO form_template_fields(
        template_id,section_id,label,field_type,options_json,help_text,
        default_value,required,position) VALUES(?,?,?,?,?,?,?,?,?)""",
        (
            template_id,
            section_id,
            "Odeur associée",
            "text_short",
            "[]",
            "Un repère sensoriel",
            "",
            0,
            0,
        ),
    ).lastrowid
    window.db.run(
        "INSERT INTO project_form_templates(project_id,target_type,template_id) VALUES(?,?,?)",
        (project_id, "character", template_id),
    )
    window.active_project = project_id
    window.db.set_setting("active_project", project_id)
    window.db.set_setting(f"last_character_{project_id}", character_id)
    window.db.set_setting("selected_form_template", template_id)

    window.show_form_templates()
    app.processEvents()
    assert window.current_view == "form_templates"
    assert window.form_template_list.count() == 1
    assert window.form_template_outline.topLevelItemCount() == 1

    window.show_characters()
    app.processEvents()
    assert field_id in window.record_template_widgets
    _field_type, widget = window.record_template_widgets[field_id]
    widget.setText("Papier mouillé")
    window._save_record_template_values()
    saved = window.db.one(
        """SELECT value_text FROM form_field_values
        WHERE project_id=? AND target_type='character' AND entity_id=? AND field_id=?""",
        (project_id, character_id, field_id),
    )
    assert saved["value_text"] == "Papier mouillé"

    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_guides_keep_runs_isolated_and_apply_to_existing_project(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "guides.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage,updated_at) VALUES(?,?,?,?)",
        (NOW(), "Les deux veilles", "Noyau", NOW()),
    ).lastrowid
    window.active_project = project_id
    window.db.set_setting("active_project", str(project_id))

    first = window.db.create_guided_run("seed", "Première graine", legacy_session_key="session01")
    second = window.db.create_guided_run("seed", "Deuxième graine")
    window.db.save_guided_answer(first, "idea", 0, "Une gardienne déplace un tableau.", "complete")
    window.db.save_guided_answer(second, "idea", 0, "Un enfant entend les murs.", "complete")
    assert window.db.one(
        "SELECT answer FROM guided_answers WHERE run_id=? AND step_key='idea'", (first,)
    )[0].startswith("Une gardienne")
    assert window.db.one(
        "SELECT answer FROM guided_answers WHERE run_id=? AND step_key='idea'", (second,)
    )[0].startswith("Un enfant")

    ending_run = window.db.create_guided_run(
        "find_ending", "Fin du projet", project_id=project_id, assistance_level="autonomous"
    )
    window.db.save_guided_answer(
        ending_run,
        "provisional_ending",
        4,
        "Elle révèle la fraude et quitte le musée.",
        "complete",
    )
    window._apply_guide_result(ending_run)
    assert window.db.one("SELECT ending FROM projects WHERE id=?", (project_id,))[0].startswith(
        "Elle révèle"
    )
    assert window.db.one(
        "SELECT answer FROM story_map_answers WHERE project_id=? AND step_key='resolution_change'",
        (project_id,),
    )[0].startswith("Elle révèle")
    assert window.db.guided_run(ending_run)["applied_at"]

    window.show_guide_runs()
    app.processEvents()
    assert window.guide_run_tree.topLevelItemCount() == 3
    assert (
        window.guide_run_count_badge.sizePolicy().verticalPolicy()
        == QSizePolicy.Policy.Fixed
    )
    assert window.guide_run_count_badge.height() <= window.guide_run_count_badge.sizeHint().height() + 2
    window.show_guides()
    app.processEvents()
    assert window.guide_catalog_tree.topLevelItemCount() == 7
    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_sidebar_project_selector_switches_context_without_overwriting_script(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "project-selector.db")
    first = window.db.run(
        "INSERT INTO projects(created_at,title,stage,updated_at) VALUES(?,?,?,?)",
        (NOW(), "Projet Alpha", "Scénario", NOW()),
    ).lastrowid
    second = window.db.run(
        "INSERT INTO projects(created_at,title,stage,updated_at) VALUES(?,?,?,?)",
        (NOW(), "Projet Bêta", "Scénario", NOW()),
    ).lastrowid
    window.db.ensure_doc(first, "script", "Scénario")
    window.db.save_doc(first, "script", "INT. HALL - JOUR\nAncienne version.")
    window.db.ensure_doc(second, "script", "Scénario")
    window.db.save_doc(second, "script", "EXT. QUAI - NUIT\nLe second projet.")
    window.active_project = first
    window.db.set_setting("active_project", first)
    window._update_project_chips()
    assert isinstance(window.project_chip, QComboBox)
    assert window.project_chip.count() == 2

    window.show_script_editor()
    window.script_text.setPlainText("INT. HALL - JOUR\nVersion modifiée avant le changement.")
    window.project_chip.setCurrentIndex(window.project_chip.findData(second))
    app.processEvents()

    assert window.active_project == second
    assert window.top_project.text() == "Projet Bêta"
    assert window.db.one(
        "SELECT content FROM project_docs WHERE project_id=? AND doc_type='script'", (first,)
    )[0].endswith("Version modifiée avant le changement.")
    assert window.db.one(
        "SELECT content FROM project_docs WHERE project_id=? AND doc_type='script'", (second,)
    )[0].endswith("Le second projet.")
    assert window.script_text.toPlainText().endswith("Le second projet.")

    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_story_map_edge_drag_does_not_reenter_qt(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "drag-safe.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)",
        (NOW(), "Déplacement sûr", "Carte"),
    ).lastrowid
    window.db.create_story_map_node(
        project_id,
        "Carte au bord",
        "Le canevas doit suivre sans réentrer dans Qt.",
        "action",
        140,
        420,
    )
    window.active_project = project_id
    window.db.set_setting("active_project", project_id)
    window.db.set_setting(f"last_development_doc_{project_id}", "story_map")
    window.db.set_setting(f"story_map_mode_{project_id}", "board")
    window.resize(1120, 720)
    window.show_development()
    window.show()
    app.processEvents()

    view = window.story_map_view
    card = next(iter(window.story_map_items.values()))
    view.centerOn(card)
    app.processEvents()
    initial_scroll = view.horizontalScrollBar().value()
    for _ in range(3):
        start = view.mapFromScene(card.sceneBoundingRect().center())
        destination = QPoint(view.viewport().width() - 5, max(20, min(view.viewport().height() - 20, start.y())))
        QTest.mousePress(view.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, start)
        QTest.mouseMove(view.viewport(), destination, 10)
        QTest.qWait(80)
        QTest.mouseRelease(view.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, destination)
        app.processEvents()

    assert view.horizontalScrollBar().value() > initial_scroll
    window.story_map_pan_timer.stop()
    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_story_map_empty_space_expands_without_a_card_on_the_edge(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "empty-space.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)",
        (NOW(), "Canevas libre", "Carte"),
    ).lastrowid
    window.active_project = project_id
    window.db.set_setting("active_project", project_id)
    window.db.set_setting(f"last_development_doc_{project_id}", "story_map")
    window.db.set_setting(f"story_map_mode_{project_id}", "board")
    window.resize(1120, 720)
    window.show_development()
    window.show()
    app.processEvents()

    assert not window.story_map_items
    initial_right = window.story_map_scene.sceneRect().right()
    horizontal = window.story_map_view.horizontalScrollBar()
    horizontal.setValue(horizontal.maximum())
    QTest.qWait(30)
    app.processEvents()

    assert window.story_map_scene.sceneRect().right() > initial_right
    window.story_map_pan_timer.stop()
    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_development_navigation_leaves_story_map_after_old_editor_is_deleted(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "delayed-navigation.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)",
        (NOW(), "Navigation fiable", "Carte"),
    ).lastrowid
    window.db.ensure_doc(project_id, "summary", "Résumé très court")
    window.db.save_doc(project_id, "summary", "Une histoire complète en quelques lignes.")
    window.db.run(
        "INSERT INTO development_status(project_id,doc_type,status,updated_at) VALUES(?,?,?,?)",
        (project_id, "summary", "complete", NOW()),
    )
    window.db.create_story_map_node(project_id, "Carte sans titre", "", "situation", 90, 90)
    window.active_project = project_id
    window.db.set_setting("active_project", project_id)
    window.db.set_setting(f"last_development_doc_{project_id}", "premise")
    window.resize(1400, 850)
    window.show_development()
    window.show()
    app.processEvents()

    def visible_document_button(label: str) -> QPushButton:
        return next(
            button
            for button in window.findChildren(QPushButton)
            if button.property("segment") and label in button.text() and button.isVisible()
        )

    visible_document_button("Carte de l’histoire").click()
    app.processEvents()
    QTest.qWait(150)

    summary_button = visible_document_button("Résumé très court")
    story_map_button = visible_document_button("Carte de l’histoire")
    assert summary_button.text().startswith("03")
    assert summary_button.text().endswith("✓")
    assert story_map_button.text().startswith("04")
    assert not story_map_button.text().endswith("✓")

    visible_document_button("Synopsis").click()
    app.processEvents()
    assert window.development_doc_type == "synopsis"
    assert window.synopsis_mode == "guide"
    assert isinstance(window.synopsis_answer_text, QTextEdit)
    assert not hasattr(window, "story_map_view") or not window.story_map_view.isVisible()

    window.story_map_pan_timer.stop()
    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()

def test_guided_synopsis_uses_story_map_and_builds_an_editable_final_text(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "guided-synopsis.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage,protagonist,objective,opposition,stakes,change_note,ending) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (
            NOW(),
            "La dernière lettre",
            "Carte",
            "Mina",
            "remettre une lettre au juge",
            "les portes sont fermées",
            "son frère sera condamné",
            "elle choisit d’agir",
            "la lettre ouvre une enquête",
        ),
    ).lastrowid
    map_material = {
        "starting_situation": "Mina trie les lettres impossibles à livrer.",
        "disrupting_event": "Elle découvre une lettre qui innocente son frère.",
        "objective": "Elle décide de remettre la lettre au juge avant l’aube.",
        "first_actions": "Elle vole un laissez-passer et prend les tunnels.",
        "obstacles_consequences": "Une grille bloquée déclenche une alarme.",
        "escalation": "Les gardes la recherchent dans toute la ville.",
        "difficult_choice": "Elle renonce à son passage secret pour sauver une alliée.",
        "final_confrontation": "Mina lit la lettre publiquement devant le tribunal.",
        "resolution_change": "Une enquête commence et Mina refuse désormais d’obéir aveuglément.",
    }
    for key, answer in map_material.items():
        window.db.save_story_map_answer(project_id, key, answer)
    window.active_project = project_id
    window.db.set_setting("active_project", project_id)
    window.db.set_setting(f"last_development_doc_{project_id}", "synopsis")
    window.resize(1400, 850)
    window.show_development()
    window.show()
    app.processEvents()

    assert window.development_doc_type == "synopsis"
    assert window.synopsis_mode == "guide"
    assert window.synopsis_step_index == 0
    assert "Mina trie" in window.synopsis_answer_text.toPlainText()

    for expected_index in range(len(SYNOPSIS_STEPS) - 1):
        assert window.synopsis_step_index == expected_index
        assert window.synopsis_answer_text.toPlainText().strip()
        window._next_synopsis_step()
        app.processEvents()

    assert window.synopsis_step_index == len(SYNOPSIS_STEPS) - 1
    assert "enquête" in window.synopsis_answer_text.toPlainText()
    window._finish_synopsis_guide()
    app.processEvents()

    assert window.synopsis_mode == "final"
    final_text = window.synopsis_final_text.toPlainText()
    assert "Mina trie" in final_text
    assert "lit la lettre publiquement" in final_text
    assert "DÉBUT" not in final_text
    assert window.db.one("SELECT stage FROM projects WHERE id=?", (project_id,))[0] == "Synopsis"
    assert window.db.one(
        "SELECT COUNT(*) FROM synopsis_answers WHERE project_id=? AND TRIM(answer)<>''",
        (project_id,),
    )[0] == len(SYNOPSIS_STEPS)

    window.synopsis_final_text.append("Une dernière conséquence demeure.")
    window._save_synopsis_final(silent=True)
    assert window.db.one(
        "SELECT content FROM project_docs WHERE project_id=? AND doc_type='synopsis'",
        (project_id,),
    )[0].endswith("Une dernière conséquence demeure.")

    window.story_map_pan_timer.stop()
    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_old_opposition_and_seed_answers_move_to_their_new_steps(tmp_path: Path) -> None:
    path = tmp_path / "legacy-v05.db"
    db = Database(path)
    db.save_learning_work("session01", 4, "opposition", "Une porte verrouillée", "", "", "", "à revoir", "terminé")
    db.save_learning_work("session01", 5, "graine", "Une gardienne cherche la vérité", "", "", "", "à revoir", "terminé")
    db.run(
        "INSERT INTO progress(session_key,step_index,status,updated_at) VALUES('session01',5,'terminée',?)",
        (NOW(),),
    )
    db.conn.close()

    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(path)
    assert window.db.one("SELECT draft FROM learning_work WHERE session_key='session01' AND step_index=5")[0] == "Une porte verrouillée"
    assert window.db.one("SELECT draft FROM learning_work WHERE session_key='session01' AND step_index=13")[0] == "Une gardienne cherche la vérité"
    progress = window.db.one("SELECT step_index,status FROM progress WHERE session_key='session01'")
    assert progress["step_index"] == 6
    assert progress["status"] == "en cours"
    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_learning_answers_create_a_prefilled_project(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "project-from-seed.db")
    answers = {
        "idea": "Une gardienne déplace un tableau.",
        "protagonist": "Nora, gardienne de nuit",
        "desire": "Rétablir sa réputation",
        "objective": "Prouver que le tableau est faux",
        "opposition": "Le directeur verrouille les archives",
        "stakes": "Elle risque son emploi",
        "change": "Elle choisit la vérité plutôt que le mérite",
        "ending": "Le faux est retiré avant l’exposition",
        "seed": "Une gardienne tente de révéler une contrefaçon avant l’ouverture du musée.",
    }
    for index, step in enumerate(LEARNING_SESSION.steps):
        window.db.save_learning_work(
            LEARNING_SESSION.key,
            index,
            step.concept_key,
            answers.get(step.key, ""),
            "",
            "",
            "",
            "à revoir",
            "terminé",
        )

    window._create_project_from_learning(title="Le faux tableau")
    project = window.db.one("SELECT * FROM projects WHERE id=?", (window.active_project,))
    premise = window.db.one(
        "SELECT content FROM project_docs WHERE project_id=? AND doc_type='premise'",
        (window.active_project,),
    )
    assert project["title"] == "Le faux tableau"
    assert project["protagonist"].startswith("Nora")
    assert project["objective"].startswith("Prouver")
    assert premise["content"].startswith("Une gardienne")
    assert window.db.one("SELECT COUNT(*) FROM project_questions WHERE project_id=?", (window.active_project,))[0] == 12
    assert window.current_view == "projects"
    assert window.project_tree.topLevelItemCount() == 1
    project_item = window.project_tree.topLevelItem(0)
    assert project_item.text(0).startswith("Le faux tableau\nFilm · Court métrage")
    assert project_item.text(1) == "1/10"
    assert project_item.text(2) == "Logline"
    window._open_project_construction()
    app.processEvents()
    assert window.current_view == "development"
    assert window.development_doc_type == "premise"
    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_visual_sequencer_imports_story_cards_and_reorders_blocks(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "visual-sequencer.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)",
        (NOW(), "La lettre", "Carte"),
    ).lastrowid
    first_node = window.db.create_story_map_node(
        project_id,
        "Situation de nuit",
        "Mina trie des lettres impossibles à livrer.",
        "situation",
        80,
        80,
    )
    second_node = window.db.create_story_map_node(
        project_id,
        "La lettre interdite",
        "Une lettre qui innocente son frère arrive.",
        "event",
        420,
        80,
    )
    window.db.create_story_map_link(project_id, first_node, second_node)
    window.active_project = project_id
    window.db.set_setting("active_project", project_id)
    window.db.set_setting(f"last_development_doc_{project_id}", "outline")
    window.db.set_setting(f"outline_mode_{project_id}", "sequences")
    window.show_development()
    window.show()
    app.processEvents()

    assert window.sequence_list.count() == 0
    window._import_story_cards_to_sequences()
    app.processEvents()
    assert window.sequence_list.count() == 2
    rows = window.db.q(
        "SELECT title,source_node_id,consequence FROM sequence_blocks WHERE project_id=? ORDER BY position,id",
        (project_id,),
    )
    assert [row["source_node_id"] for row in rows] == [first_node, second_node]
    assert "La lettre interdite" in rows[0]["consequence"]

    window._duplicate_sequence_block(int(window.sequence_list.item(0).data(Qt.ItemDataRole.UserRole)))
    app.processEvents()
    assert window.sequence_list.count() == 3
    last_item = window.sequence_list.takeItem(2)
    window.sequence_list.insertItem(0, last_item)
    window._sequence_order_changed()
    app.processEvents()
    ordered = window.db.q(
        "SELECT title,position FROM sequence_blocks WHERE project_id=? ORDER BY position,id",
        (project_id,),
    )
    assert ordered[0]["position"] == 0
    assert ordered[0]["title"] == "La lettre interdite"
    assert "Contenu" in window.db.one(
        "SELECT content FROM project_docs WHERE project_id=? AND doc_type='outline'",
        (project_id,),
    )[0]

    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_template_bank_adds_optional_blocks_to_active_project(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "templates.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)",
        (NOW(), "Court test", "Noyau"),
    ).lastrowid
    window.active_project = project_id
    window.db.set_setting("active_project", project_id)
    window.show_templates()
    window.show()
    app.processEvents()

    assert window.current_view == "templates"
    assert window.template_tree.topLevelItemCount() >= 4
    template = next(item for item in TEMPLATE_LIBRARY if item["key"] == "short_film")
    window._apply_template_to_sequence(template["key"])
    app.processEvents()

    assert window.current_view == "development"
    assert window.development_doc_type == "outline"
    assert window.outline_tree.topLevelItemCount() == len(template["steps"])
    assert window.db.one(
        "SELECT COUNT(*) FROM outline_items WHERE project_id=? AND item_type='sequence'",
        (project_id,),
    )[0] == len(template["steps"])
    assert window.db.one(
        "SELECT title FROM sequence_blocks WHERE project_id=? ORDER BY position LIMIT 1",
        (project_id,),
    )[0] == "Image de départ"

    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_global_outline_links_hierarchy_and_sequence_edits(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "global-outline.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)",
        (NOW(), "Plan lié", "Construction"),
    ).lastrowid
    sequence_id = window.db.create_sequence_block(
        project_id,
        0,
        "La porte",
        "Forcer un choix",
        "Mina arrive devant deux portes.",
        "Elle doit choisir.",
    )
    scene_id = window.db.run(
        """INSERT INTO scene_rows(
        project_id,position,title,duration,objective,opposition,change_note,source_sequence_id,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, 0, "Devant la porte", 2, "Sortir", "Noé refuse", "Mina agit",
            sequence_id, NOW(), NOW(),
        ),
    ).lastrowid
    window.active_project = project_id
    window.db.set_setting("active_project", project_id)
    window.db.set_setting(f"last_development_doc_{project_id}", "outline")
    window.show_development()
    window.show()
    app.processEvents()

    assert window.outline_tree.topLevelItemCount() == 1
    sequence_item = window.outline_tree.topLevelItem(0)
    assert sequence_item.text(0) == "SÉQUENCE"
    assert sequence_item.childCount() == 1
    assert int(sequence_item.child(0).data(0, Qt.ItemDataRole.UserRole + 3)) == scene_id

    sequence_item.setText(1, "La porte interdite")
    app.processEvents()
    assert window.db.one("SELECT title FROM sequence_blocks WHERE id=?", (sequence_id,))[0] == "La porte interdite"

    window.outline_tree.setCurrentItem(sequence_item)
    window.outline_add_type.setCurrentIndex(window.outline_add_type.findData("beat"))
    window._add_outline_item()
    app.processEvents()
    assert window.db.one(
        "SELECT COUNT(*) FROM outline_items WHERE project_id=? AND item_type='beat'",
        (project_id,),
    )[0] == 1

    window.outline_view_combo.setCurrentIndex(window.outline_view_combo.findData("compact"))
    app.processEvents()
    assert window.outline_tree.isColumnHidden(2)

    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_idea_notebook_selects_filters_and_preserves_existing_ideas(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "idea-notebook.db")
    first_id = window.db.run(
        "INSERT INTO ideas(created_at,title,seed,attraction,status,potential,idea_type) VALUES(?,?,?,?,?,?,?)",
        (NOW(), "Le musée", "Un tableau bouge la nuit.", "Une image inquiétante.", "retenue", "court", "theme"),
    ).lastrowid
    latest_id = window.db.run(
        "INSERT INTO ideas(created_at,title,seed,attraction,status,potential,idea_type) VALUES(?,?,?,?,?,?,?)",
        (NOW(), "La voix", "Une voix annonce demain.", "La peur de savoir.", "à explorer", "moyen", "dialogue"),
    ).lastrowid
    window.resize(1120, 720)
    window.show_ideas()
    window.show()
    app.processEvents()

    assert window.idea_id == latest_id
    assert window.idea_fields["title"].text() == "La voix"
    assert window.idea_fields["seed"].toPlainText() == "Une voix annonce demain."
    assert window.idea_count.text() == "2"
    window.idea_search.setText("musée")
    app.processEvents()
    visible_ids = [
        int(window.idea_list.item(index).data(Qt.ItemDataRole.UserRole))
        for index in range(window.idea_list.count())
        if not window.idea_list.item(index).isHidden()
    ]
    assert visible_ids == [first_id]

    window.idea_search.clear()
    window.idea_type_filter.setCurrentIndex(window.idea_type_filter.findData("dialogue"))
    app.processEvents()
    visible_ids = [
        int(window.idea_list.item(index).data(Qt.ItemDataRole.UserRole))
        for index in range(window.idea_list.count())
        if not window.idea_list.item(index).isHidden()
    ]
    assert visible_ids == [latest_id]
    assert window.idea_count.text() == "1/2"

    window.idea_type_filter.setCurrentIndex(window.idea_type_filter.findData("all"))
    window.idea_search.clear()
    window._new_idea()
    window.idea_fields["title"].setText("Nouvelle étincelle")
    window.idea_fields["seed"].setPlainText("Une porte refuse de s’ouvrir deux fois.")
    window._append_idea_what_if()
    window.idea_fields["what_if"].insertPlainText("la porte reconnaissait seulement les mensonges ?")
    window.idea_kind.setCurrentIndex(window.idea_kind.findData("setting"))
    attachment_path = tmp_path / "porte.png"
    attachment_image = QPixmap(40, 28)
    attachment_image.fill(QColor("#4488CC"))
    assert attachment_image.save(str(attachment_path))
    window._set_idea_attachment(attachment_path)
    assert window.idea_attachment_name == "porte.png"
    assert not window.idea_attachment_preview.pixmap().isNull()
    window._save_idea()
    assert window.idea_list.currentItem().data(Qt.ItemDataRole.UserRole) == window.idea_id
    assert window.db.one("SELECT COUNT(*) FROM ideas")[0] == 3
    assert window.db.one("SELECT idea_type FROM ideas WHERE id=?", (window.idea_id,))[0] == "setting"
    assert "reconnaissait seulement" in window.db.one(
        "SELECT what_if FROM ideas WHERE id=?", (window.idea_id,)
    )[0]
    attachment = window.db.one(
        "SELECT attachment_name,attachment_mime,attachment_data FROM ideas WHERE id=?",
        (window.idea_id,),
    )
    assert attachment["attachment_name"] == "porte.png"
    assert attachment["attachment_mime"] == "image/png"
    assert len(attachment["attachment_data"]) > 0

    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_project_libraries_scene_table_and_script_editor_work_together(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "project-tools.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)",
        (NOW(), "La fenêtre", "Noyau"),
    ).lastrowid
    window.active_project = project_id
    window.db.set_setting("active_project", project_id)
    window._update_project_chips()
    window.resize(1280, 800)
    group_id = window.db.run(
        """INSERT INTO character_groups(
        project_id,name,group_type,description,color,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?)""",
        (project_id, "Veilleurs", "Équipe", "Surveillent les maisons.", "", NOW(), NOW()),
    ).lastrowid

    window.show_characters()
    window.show()
    app.processEvents()
    assert window.character_add_portrait_button.property("role") == "secondary"
    assert window.character_remove_portrait_button.property("role") == "tertiary"
    assert window.character_delete_button.property("role") == "danger"
    assert not window.character_delete_button.isEnabled()
    assert [window.character_tabs.tabText(index) for index in range(window.character_tabs.count())] == [
        "Essentiel",
        "Dramaturgie",
        "Arc et transformation",
        "Voix et notes",
        "Connexions",
        "Modèle de fiche",
        "Champs libres",
    ]
    window.character_fields["name"].setText("Mina")
    window.character_fields["role"].setCurrentText("Protagoniste")
    window.character_fields["desire"].setText("Comprendre qui ouvre la fenêtre")
    window.character_fields["objective"].setText("Identifier l’intrus avant l’aube")
    window.character_fields["start_situation"].setPlainText("Mina refuse de regarder dehors.")
    window.character_group_membership.item(0).setSelected(True)
    window._add_character_custom_field_row("Signe distinctif", "Une bague noire")
    window._save_character()
    saved_character = window.db.one(
        "SELECT id,name,objective,start_situation FROM characters WHERE project_id=?", (project_id,)
    )
    assert saved_character["name"] == "Mina"
    assert saved_character["objective"].startswith("Identifier")
    assert window.character_selector.count() == 1
    assert window.character_delete_button.isEnabled()
    window.character_fields["name"].setText("Nom non enregistré")
    window._cancel_character_edits()
    assert window.character_fields["name"].text() == "Mina"
    assert window.character_list.count() == 1
    assert window.character_list.item(0).sizeHint().height() == 72
    assert not window.character_selector.isVisible()
    column_widths = [
        window.character_roster_card.width(),
        window.character_portrait_card.width(),
        window.character_detail_card.width(),
    ]
    assert column_widths[0] == 320
    assert column_widths[0] < column_widths[1]
    assert column_widths[0] < column_widths[2]
    assert column_widths[1] > column_widths[2]
    assert window.db.one(
        "SELECT COUNT(*) FROM character_group_members WHERE group_id=? AND character_id=?",
        (group_id, int(saved_character["id"])),
    )[0] == 1
    assert window.db.one(
        "SELECT value FROM character_custom_fields WHERE character_id=?",
        (int(saved_character["id"]),),
    )[0] == "Une bague noire"

    moodboard_path = tmp_path / "mina-moodboard.png"
    moodboard = QPixmap(70, 90)
    moodboard.fill(QColor("#6A5A4C"))
    assert moodboard.save(str(moodboard_path))
    window.db.run(
        """INSERT INTO character_references(
        project_id,character_id,title,category,notes,file_name,mime_type,image_data,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, int(saved_character["id"]), "Manteau", "Costume", "",
            moodboard_path.name, "image/png", moodboard_path.read_bytes(), NOW(), NOW(),
        ),
    )
    window._refresh_character_references()
    assert window.character_reference_list.count() == 1

    main_timeline = window.db.ensure_timeline_track(project_id, "Intrigue principale", "#3D8EF7")
    window.db.ensure_timeline_track(project_id, "Backstory", "#9B6BDE")
    timeline_event_id = window.db.run(
        """INSERT INTO timeline_events(
        project_id,track_id,title,time_hours,display_label,category,description,place,consequence,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, int(main_timeline["id"]), "La fenêtre s’ouvre", 0, "Jour 0", "Intrigue principale",
            "Mina entend le verrou.", "Chambre", "Elle commence à enquêter.", NOW(), NOW(),
        ),
    ).lastrowid
    window.db.run(
        "INSERT INTO timeline_event_characters(event_id,character_id) VALUES(?,?)",
        (timeline_event_id, int(saved_character["id"])),
    )
    map_node_id = window.db.create_story_map_node(
        project_id, "La fenêtre s’ouvre", "Mina entend le verrou.", "event"
    )
    window.db.run(
        "INSERT INTO story_map_node_characters(node_id,character_id) VALUES(?,?)",
        (map_node_id, int(saved_character["id"])),
    )
    window.show_timeline()
    app.processEvents()
    assert not window.timeline_view.mask().isEmpty()
    assert not window.timeline_view.mask().contains(QPoint(0, 0))
    assert window.timeline_view.mask().contains(window.timeline_view.rect().center())
    assert len(window.timeline_rows) == 1
    assert window.timeline_rows[0]["character_names"] == "Mina"
    assert len(window.timeline_tracks) == 2
    scene_labels = {
        item.toPlainText()
        for item in window.timeline_view.timeline_scene.items()
        if hasattr(item, "toPlainText")
    }
    assert {"Intrigue principale", "Backstory"}.issubset(scene_labels)
    horizontal_bar = window.timeline_view.horizontalScrollBar()
    assert horizontal_bar.maximum() > 0
    before_drag = horizontal_bar.value()
    viewport = window.timeline_view.viewport()
    drag_y = max(20, viewport.height() - 35)
    QTest.mousePress(
        viewport,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
        QPoint(max(80, viewport.width() - 80), drag_y),
    )
    QTest.mouseMove(viewport, QPoint(max(20, viewport.width() - 330), drag_y), delay=30)
    QTest.mouseRelease(
        viewport,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
        QPoint(max(20, viewport.width() - 330), drag_y),
    )
    app.processEvents()
    assert horizontal_bar.value() > before_drag
    vertical_bar = window.timeline_view.verticalScrollBar()
    assert vertical_bar.maximum() > 0
    vertical_bar.setValue(vertical_bar.maximum() // 2)
    before_vertical_drag = vertical_bar.value()
    drag_x = max(20, viewport.width() - 35)
    QTest.mousePress(
        viewport,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
        QPoint(drag_x, max(80, viewport.height() - 100)),
    )
    QTest.mouseMove(viewport, QPoint(drag_x, max(20, viewport.height() - 300)), delay=30)
    QTest.mouseRelease(
        viewport,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
        QPoint(drag_x, max(20, viewport.height() - 300)),
    )
    app.processEvents()
    assert vertical_bar.value() != before_vertical_drag
    event_item = next(
        item for item in window.timeline_view.timeline_scene.items()
        if isinstance(item, TimelineEventItem)
    )
    edited_ids = []
    event_item.on_edit = edited_ids.append
    window.timeline_view.centerOn(event_item)
    app.processEvents()
    event_point = window.timeline_view.mapFromScene(
        event_item.mapToScene(event_item.boundingRect().center())
    )
    QTest.mouseDClick(
        window.timeline_view.viewport(),
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
        event_point,
    )
    app.processEvents()
    assert edited_ids == [timeline_event_id]
    window._select_timeline_event(timeline_event_id)
    assert window.timeline_detail_title.text() == "La fenêtre s’ouvre"
    assert window.timeline_detail_meta.text().startswith("INTRIGUE PRINCIPALE")

    reference_path = tmp_path / "fenetre.png"
    reference = QPixmap(120, 80)
    reference.fill(QColor("#315A81"))
    assert reference.save(str(reference_path))
    window.db.run(
        """INSERT INTO image_library(
        project_id,title,category,notes,file_name,mime_type,image_data,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?)""",
        (
            project_id,
            "Fenêtre de nuit",
            "Lieu / décor",
            "",
            reference_path.name,
            "image/png",
            reference_path.read_bytes(),
            NOW(),
            NOW(),
        ),
    )
    window.show_images()
    app.processEvents()
    assert window.image_library_list.count() == 1
    assert window.image_library_list.item(0).text() == "Fenêtre de nuit"

    window.db.set_setting(f"last_development_doc_{project_id}", "scenes")
    window.show_development()
    app.processEvents()
    window._add_scene_row()
    assert [
        window.scene_table.horizontalHeaderItem(index).text()
        for index in range(window.scene_table.columnCount())
    ] == ["N°", "Nom / titre de la scène", "Lieu", "Statut", "Durée (min)"]
    assert [window.scene_tabs.tabText(index) for index in range(window.scene_tabs.count())] == [
        "Noyau",
        "Déroulement",
        "Connexions",
        "Modèle de fiche",
    ]
    window.scene_table.item(0, 1).setText("Mina découvre la fenêtre")
    window.scene_table.item(0, 4).setText("1,5")
    window.scene_status_combo.setCurrentIndex(window.scene_status_combo.findData("draft"))
    window.scene_driver_combo.setCurrentIndex(
        window.scene_driver_combo.findData(int(saved_character["id"]))
    )
    window.scene_detail_fields["moment_label"].setText("Jour 0 · nuit")
    window.scene_detail_fields["objective"].setText("Identifier l’intrus")
    window.scene_detail_fields["character_objective"].setText(
        "Trouver une preuve avant le retour de Noé"
    )
    window.scene_detail_fields["opposition"].setText("La chambre est plongée dans le noir")
    window.scene_detail_fields["conflict_note"].setText(
        "Mina veut savoir, mais elle redoute la vérité"
    )
    window.scene_detail_fields["information_revealed"].setText(
        "Le verrou ne peut être actionné que de l’intérieur"
    )
    window.scene_detail_fields["change_note"].setText("Mina comprend que la fenêtre s’ouvre de l’intérieur")
    window.scene_detail_fields["entry_state"].setText("Mina pense à un courant d’air")
    window.scene_detail_fields["exit_state"].setText("Mina commence à soupçonner Noé")
    window.scene_detail_fields["notes"].setText("Garder la découverte très visuelle.")
    window.scene_character_list.item(0).setSelected(True)
    window.scene_connection_lists["events"].item(0).setCheckState(Qt.CheckState.Checked)
    window.scene_connection_lists["story_nodes"].item(0).setCheckState(Qt.CheckState.Checked)
    window._save_scene_list(silent=True)
    scene = window.db.one(
        """SELECT id,title,duration,objective,opposition,change_note,status,moment_label,
        driver_character_id,character_objective,conflict_note,information_revealed,
        entry_state,exit_state,notes FROM scene_rows WHERE project_id=?""",
        (project_id,),
    )
    assert scene["title"] == "Mina découvre la fenêtre"
    assert scene["duration"] == 1.5
    assert scene["objective"] == "Identifier l’intrus"
    assert scene["opposition"] == "La chambre est plongée dans le noir"
    assert scene["change_note"].startswith("Mina comprend")
    assert scene["status"] == "draft"
    assert scene["moment_label"] == "Jour 0 · nuit"
    assert scene["driver_character_id"] == int(saved_character["id"])
    assert scene["character_objective"].startswith("Trouver une preuve")
    assert scene["conflict_note"].startswith("Mina veut savoir")
    assert scene["information_revealed"].startswith("Le verrou")
    assert scene["entry_state"].startswith("Mina pense")
    assert scene["exit_state"].startswith("Mina commence")
    assert scene["notes"] == "Garder la découverte très visuelle."
    assert window.db.one("SELECT COUNT(*) FROM scene_characters WHERE scene_id=?", (scene["id"],))[0] == 1
    assert window.db.one("SELECT event_id FROM scene_events WHERE scene_id=?", (scene["id"],))[0] == timeline_event_id
    assert window.db.one("SELECT node_id FROM scene_story_nodes WHERE scene_id=?", (scene["id"],))[0] == map_node_id
    original_scene_id = int(scene["id"])
    window.scene_table.item(0, 1).setText("Mina inspecte la fenêtre")
    window._save_scene_list(silent=True)
    assert window.db.one("SELECT id FROM scene_rows WHERE project_id=?", (project_id,))[0] == original_scene_id
    assert window.db.one(
        "SELECT source_scene_id FROM outline_items WHERE project_id=? AND item_type='scene'",
        (project_id,),
    )[0] == original_scene_id

    window.show_characters()
    app.processEvents()
    assert window.character_scene_connections.count() == 1
    assert "Mina inspecte" in window.character_scene_connections.item(0).text()
    assert window.character_map_connections.count() == 1
    assert "fenêtre" in window.character_map_connections.item(0).text().lower()
    assert window.character_timeline_connections.count() == 1
    assert "La fenêtre s’ouvre" in window.character_timeline_connections.item(0).text()
    assert window.character_fields["role"].currentText() == "Protagoniste"

    image_id = int(window.db.one(
        "SELECT id FROM image_library WHERE project_id=?", (project_id,)
    )[0])
    window.show_locations()
    app.processEvents()
    assert window.location_library_card.width() == 320
    assert window.location_list.count() == 0
    assert window.location_remove_image_button.property("role") == "tertiary"
    assert window.location_delete_button.property("role") == "danger"
    assert not window.location_delete_button.isEnabled()
    assert window.nav_buttons["characters"].property("navChild") is True
    window.location_fields["name"].setText("Chambre de Mina")
    window.location_fields["category"].setCurrentText("Maison / intérieur")
    window.location_fields["region"].setText("Quartier nord")
    window.location_fields["description"].setPlainText(
        "Une chambre dont la fenêtre s’ouvre de l’intérieur."
    )
    window.location_fields["narrative_function"].setPlainText(
        "Lieu de départ et première preuve."
    )
    window.location_tabs.setCurrentIndex(2)
    app.processEvents()
    character_picker = window.location_connection_lists["characters"]
    character_item = character_picker.item(0)
    character_item.setCheckState(Qt.CheckState.Unchecked)
    assert character_picker.isVisible()
    assert character_picker.itemAt(character_picker.visualItemRect(character_item).center()) is character_item, (
        character_picker.viewport().size(),
        character_picker.visualItemRect(character_item),
    )
    QTest.mouseClick(
        character_picker.viewport(),
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
        character_picker.visualItemRect(character_item).center(),
    )
    assert character_item.checkState() == Qt.CheckState.Checked
    for key, target_id in (
        ("characters", int(saved_character["id"])),
        ("events", timeline_event_id),
        ("scenes", int(scene["id"])),
        ("images", image_id),
    ):
        picker = window.location_connection_lists[key]
        item = next(
            picker.item(index)
            for index in range(picker.count())
            if int(picker.item(index).data(Qt.ItemDataRole.UserRole)) == target_id
        )
        item.setCheckState(Qt.CheckState.Checked)
    window._save_location()
    app.processEvents()
    location = window.db.one(
        "SELECT id,name,category FROM locations WHERE project_id=?", (project_id,)
    )
    assert location["name"] == "Chambre de Mina"
    assert location["category"] == "Maison / intérieur"
    assert window.location_list.count() == 1
    assert window.location_delete_button.isEnabled()
    window.location_fields["name"].setText("Nom non enregistré")
    window._cancel_location_edits()
    assert window.location_fields["name"].text() == "Chambre de Mina"
    assert window.location_image_list.count() == 1
    assert image_id in window._location_pixmap_cache
    for table in ("location_characters", "location_events", "location_scenes", "location_images"):
        assert window.db.one(
            f"SELECT COUNT(*) FROM {table} WHERE location_id=?", (int(location["id"]),)
        )[0] == 1

    second_scene_id = window.db.run(
        """INSERT INTO scene_rows(
        project_id,position,title,objective,status,entry_state,exit_state,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?)""",
        (
            project_id,
            1,
            "Mina suit la trace",
            "Transformer l’indice en décision",
            "idea",
            "Mina hésite à sortir",
            "Mina quitte la chambre",
            NOW(),
            NOW(),
        ),
    ).lastrowid
    window.db.run(
        "INSERT INTO scene_characters(scene_id,character_id) VALUES(?,?)",
        (second_scene_id, int(saved_character["id"])),
    )

    window.show_script_editor()
    app.processEvents()
    window.script_text.setPlainText(
        "INT. CHAMBRE - NUIT\n\nMina s’approche de la fenêtre.\n\nMINA\nQui est là ?"
    )
    app.processEvents()
    window._save_script(silent=True)
    assert window.script_scene_list.count() == 2
    written_scene = window.script_scene_list.item(0)
    prepared_scene = window.script_scene_list.item(1)
    assert int(written_scene.data(Qt.ItemDataRole.UserRole + 1)) == int(scene["id"])
    assert int(written_scene.data(Qt.ItemDataRole.UserRole)) == 0
    assert int(prepared_scene.data(Qt.ItemDataRole.UserRole + 1)) == second_scene_id
    assert int(prepared_scene.data(Qt.ItemDataRole.UserRole)) == -1
    window._jump_to_script_scene(written_scene)
    assert window.script_context_title.text() == "Mina inspecte la fenêtre"
    assert window.script_context_objective.text() == "Identifier l’intrus"
    assert window.script_context_characters_layout.count() == 1
    character_button = window.script_context_characters_layout.itemAt(0).widget()
    assert isinstance(character_button, QPushButton)
    assert "Mina" in character_button.text()
    window._jump_to_script_scene(prepared_scene)
    assert window.script_context_title.text() == "Mina suit la trace"
    assert window.script_context_insert_button.isEnabled()
    window._insert_selected_prepared_scene()
    assert window.script_text.toPlainText().count("INT.") == 2
    assert int(window.script_scene_list.item(1).data(Qt.ItemDataRole.UserRole)) >= 0

    window._set_script_context_visible(True)
    window._set_script_focus_mode(True)
    assert not window.top_bar.isVisible()
    assert not window.sidebar.isVisible()
    assert not window.script_navigator_card.isVisible()
    assert not window.script_context_card.isVisible()
    assert window.script_text.isVisible()
    window._set_script_focus_mode(False)
    assert window.top_bar.isVisible()
    assert window.sidebar.isVisible()

    assert window.db.one(
        "SELECT content FROM project_docs WHERE project_id=? AND doc_type='script'",
        (project_id,),
    )[0].startswith("INT. CHAMBRE")
    window._snapshot_script()
    assert window.db.one(
        "SELECT COUNT(*) FROM doc_versions WHERE project_id=? AND doc_type='script'",
        (project_id,),
    )[0] == 1

    character_position = window.script_text.toPlainText().index("\nMINA\n") + 2
    cursor = window.script_text.textCursor()
    cursor.setPosition(character_position, QTextCursor.MoveMode.MoveAnchor)
    window.script_text.setTextCursor(cursor)
    window._open_script_character_by_name("MINA")
    assert window.current_view == "characters"
    assert window.character_id == int(saved_character["id"])

    window.script_save_timer.stop()
    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_relationship_map_is_directional_filterable_and_extensible(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "relationship-map.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)",
        (NOW(), "Les deux regards", "Personnages"),
    ).lastrowid
    mina_id = window.db.run(
        """INSERT INTO characters(
        project_id,name,role,story_function,desire,conflict,arc,notes,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (project_id, "Mina", "Protagoniste", "", "", "", "", "", NOW(), NOW()),
    ).lastrowid
    sarah_id = window.db.run(
        """INSERT INTO characters(
        project_id,name,role,story_function,desire,conflict,arc,notes,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (project_id, "Sarah", "Allié", "", "", "", "", "", NOW(), NOW()),
    ).lastrowid
    group_id = window.db.run(
        """INSERT INTO character_groups(
        project_id,name,group_type,description,color,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?)""",
        (project_id, "Famille de Mina", "Famille", "", "", NOW(), NOW()),
    ).lastrowid
    window.db.run(
        "INSERT INTO character_group_members(group_id,character_id,role_in_group) VALUES(?,?,?)",
        (group_id, mina_id, "Fille"),
    )
    dialog = RelationshipMapDialog(window, window.db, project_id, window.palette, mina_id)
    dialog.show()
    app.processEvents()
    assert dialog.map_selector.count() == 1
    assert len(dialog.map_view.node_items) == 2
    map_id = int(dialog.current_map_id)
    first_relation = window.db.run(
        """INSERT INTO character_relationships(
        project_id,map_id,character_a_id,character_b_id,relationship_type,description,tension,
        secret,evolution,color,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, map_id, mina_id, sarah_id, "Respect", "Mina admire Sarah", "",
            "", "", "#31A879", NOW(), NOW(),
        ),
    ).lastrowid
    window.db.run(
        """INSERT INTO character_relationships(
        project_id,map_id,character_a_id,character_b_id,relationship_type,description,tension,
        secret,evolution,color,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, map_id, sarah_id, mina_id, "Méfiance", "Sarah doute de Mina", "",
            "Un mensonge", "La méfiance augmente", "#C49A34", NOW(), NOW(),
        ),
    )
    dialog._render_map()
    assert len(dialog.map_view.edge_items) == 2
    assert {
        (edge.source.character_id, edge.target.character_id)
        for edge in dialog.map_view.edge_items
    } == {(mina_id, sarah_id), (sarah_id, mina_id)}
    assert {edge.color.name().upper() for edge in dialog.map_view.edge_items} == {"#31A879", "#C49A34"}
    dialog._select_relation(first_relation)
    assert dialog.detail_title.text() == "Mina → Sarah"

    mina_node = dialog.map_view.node_items[mina_id]
    mina_node.setPos(2450, 1380)
    dialog._save_node_position(mina_node)
    saved_position = window.db.one(
        "SELECT x,y FROM relationship_map_nodes WHERE map_id=? AND character_id=?",
        (map_id, mina_id),
    )
    assert saved_position["x"] == 2450
    assert saved_position["y"] == 1380
    assert dialog.map_view.sceneRect().right() > 2600

    dialog.character_filter.setCurrentIndex(dialog.character_filter.findData(mina_id))
    app.processEvents()
    assert len(dialog.map_view.node_items) == 2
    dialog.character_filter.setCurrentIndex(0)
    dialog.group_filter.setCurrentIndex(dialog.group_filter.findData(group_id))
    app.processEvents()
    assert set(dialog.map_view.node_items) == {mina_id}

    second_map_id = window.db.run(
        """INSERT INTO relationship_maps(project_id,name,map_type,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, "Début de l’histoire", "start", NOW(), NOW()),
    ).lastrowid
    dialog.group_filter.setCurrentIndex(0)
    dialog._load_maps(second_map_id)
    assert dialog.current_map_id == second_map_id
    assert dialog.map_selector.count() == 2
    assert len(dialog.map_view.node_items) == 2

    dialog.close()
    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_explicit_completion_and_script_tab_cycle(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "completion-and-tab.db")

    window.show_learning()
    window.learning_draft.setPlainText("Une image encore provisoire.")
    window._save_learning_work(silent=True, status="terminé")
    window._mark_learning_incomplete()
    app.processEvents()
    learning = window.db.one(
        "SELECT status FROM learning_work WHERE session_key=? AND step_index=0",
        (LEARNING_SESSION.key,),
    )
    progress = window.db.one(
        "SELECT step_index,status FROM progress WHERE session_key=?",
        (LEARNING_SESSION.key,),
    )
    assert learning["status"] == "brouillon"
    assert progress["step_index"] == 0
    assert progress["status"] == "en cours"

    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)",
        (NOW(), "Étapes explicites", "Noyau"),
    ).lastrowid
    window.active_project = project_id
    window.db.set_setting("active_project", project_id)
    window.db.set_setting(f"last_development_doc_{project_id}", "premise")
    window.db.run(
        """INSERT INTO locations(project_id,position,name,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, 0, "Musée", NOW(), NOW()),
    )
    window.show_development()
    window.development_text.setPlainText("Une archiviste découvre que ses souvenirs ont été classés.")
    window._set_development_step_status("complete")
    app.processEvents()
    assert "premise" in window._completed_development_documents(project_id)
    window._set_development_step_status("draft")
    app.processEvents()
    assert "premise" not in window._completed_development_documents(project_id)
    assert window.db.one(
        "SELECT content FROM project_docs WHERE project_id=? AND doc_type='premise'",
        (project_id,),
    )[0].startswith("Une archiviste")

    window.show_script_editor()
    window.show()
    app.processEvents()
    assert window.script_text.extraSelections()
    assert window.script_text._script_active_background.isValid()
    assert window.script_text.extraSelections()
    assert "INT. MUSÉE - NUIT" in window.script_scene_completer_model.stringList()
    window.script_text.clear()
    window._set_script_element_mode("scene")
    window.script_text.insertPlainText("INT")
    window._update_script_scene_completion()
    assert window.script_scene_completer.completionCount() >= 2
    window.script_text.setFocus()
    QTest.keyClick(window.script_text, Qt.Key.Key_Tab)
    app.processEvents()
    assert window.script_text.toPlainText() == "INT."
    assert not window.script_scene_completer.popup().isVisible()
    window.script_text.clear()
    window._set_script_element_mode("scene")
    window.script_text.insertPlainText("INT. MUS")
    window._update_script_scene_completion()
    assert window.script_scene_completer.completionCount() >= 1
    window.script_text.setFocus()
    QTest.keyClick(window.script_text, Qt.Key.Key_Tab)
    app.processEvents()
    assert window.script_text.toPlainText() == "INT. MUSÉE"
    assert not window.script_scene_completer.popup().isVisible()
    window.script_text.clear()
    window._set_script_element_mode("scene")
    window._apply_script_block_format("scene")
    for _index in range(12):
        QTest.keyClick(window.script_text, Qt.Key.Key_Tab)
    assert window.script_text.toPlainText() == ""
    assert window.script_element_mode == "transition"
    for _index in range(12):
        QTest.keyClick(
            window.script_text,
            Qt.Key.Key_Tab,
            Qt.KeyboardModifier.ShiftModifier,
        )
    assert window.script_text.toPlainText() == ""
    assert window.script_element_mode == "scene"
    QTest.keyClick(window.script_text, Qt.Key.Key_Tab)
    assert window.script_element_mode == "action"
    assert window.script_text.textCursor().blockFormat().leftMargin() == 0
    QTest.keyClick(window.script_text, Qt.Key.Key_Tab)
    assert window.script_element_mode == "character"
    character_margin = window.script_text.textCursor().blockFormat().leftMargin()
    assert character_margin >= 200
    QTest.keyClicks(window.script_text, "mina")
    assert window.script_text.toPlainText() == "MINA"
    for _index in range(4):
        QTest.keyClick(window.script_text, Qt.Key.Key_Backspace)
    assert window.script_text.toPlainText() == ""
    assert window.script_element_mode == "action"
    assert window.script_text.textCursor().blockFormat().leftMargin() == 0
    QTest.keyClick(window.script_text, Qt.Key.Key_Backspace)
    assert window.script_element_mode == "scene"
    QTest.keyClick(window.script_text, Qt.Key.Key_Tab)
    assert window.script_element_mode == "action"
    QTest.keyClick(window.script_text, Qt.Key.Key_Tab)
    assert window.script_element_mode == "character"
    QTest.keyClicks(window.script_text, "mina")
    QTest.keyClick(window.script_text, Qt.Key.Key_Return)
    assert window.script_element_mode == "dialogue"
    dialogue_margin = window.script_text.textCursor().blockFormat().leftMargin()
    assert 0 < dialogue_margin < character_margin
    QTest.keyClicks(window.script_text, "Je reste.")
    assert window.script_text.toPlainText().endswith("Je reste.")
    QTest.keyClick(window.script_text, Qt.Key.Key_Return)
    assert window.script_element_mode == "action"
    QTest.keyClick(window.script_text, Qt.Key.Key_Tab)
    assert window.script_element_mode == "character"
    QTest.keyClicks(window.script_text, "mina")
    QTest.keyClick(window.script_text, Qt.Key.Key_Return)
    assert window.script_element_mode == "dialogue"
    assert "MINA (CONT'D)" in window.script_text.toPlainText()

    # Renaming or removing a cue later in the draft must also remove a stale
    # continuation marker instead of leaving formatting behind in the text.
    window.script_text.setPlainText(
        "INT. HALL - JOUR\n\nMINA\nBonjour.\n\nMINA\nEncore."
    )
    window._format_all_script_blocks()
    window._normalise_script_continued_cues()
    assert "MINA (CONT'D)" in window.script_text.toPlainText()
    window.script_text.setPlainText(
        "INT. HALL - JOUR\n\nMINA\nBonjour.\n\nNOAH\nEncore."
    )
    window._format_all_script_blocks()
    window._normalise_script_continued_cues()
    assert "MINA (CONT'D)" not in window.script_text.toPlainText()

    window.script_save_timer.stop()
    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_project_formats_filters_duplication_and_archive(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "project-management.db")
    project_id = window._create_empty_project(
        {
            "title": "La ville close",
            "project_type": "film",
            "story_format": "short",
            "target_duration": 18,
            "start_mode": "free",
        }
    )
    window.db.run(
        """INSERT INTO characters(
        project_id,name,role,story_function,desire,conflict,arc,notes,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (project_id, "Mina", "Protagoniste", "Décider", "Sortir", "La ville", "Agir", "", NOW(), NOW()),
    )
    window.show_projects()
    app.processEvents()
    assert window.project_tree.topLevelItemCount() == 1
    assert "Court métrage · cible 18 min" in window.project_tree.topLevelItem(0).text(0)

    window.project_search.setText("introuvable")
    assert window.project_tree.topLevelItemCount() == 0
    window.project_search.clear()
    assert window.project_tree.topLevelItemCount() == 1

    window.project_id = project_id
    monkeypatch.setattr(QInputDialog, "getText", lambda *_args, **_kwargs: ("La ville close — variante", True))
    window._duplicate_project()
    duplicate_id = window.project_id
    assert duplicate_id != project_id
    assert window.db.one("SELECT COUNT(*) FROM projects")[0] == 2
    assert window.db.one("SELECT COUNT(*) FROM characters WHERE project_id=?", (duplicate_id,))[0] == 1

    window._toggle_project_archive()
    assert window.db.one("SELECT archived FROM projects WHERE id=?", (duplicate_id,))[0] == 1
    window.project_status_filter.setCurrentIndex(window.project_status_filter.findData("archived"))
    assert window.project_tree.topLevelItemCount() == 1
    window.project_id = duplicate_id
    window._toggle_project_archive()
    assert window.db.one("SELECT archived FROM projects WHERE id=?", (duplicate_id,))[0] == 0

    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_guided_project_waits_for_the_seed_before_creation(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "guided-project.db")
    values = {
        "title": "La dernière veille",
        "project_type": "film",
        "story_format": "micro",
        "target_duration": 5,
        "start_mode": "guided",
    }
    monkeypatch.setattr(window, "_project_setup_dialog", lambda: values)
    window._new_project()
    assert window.current_view == "learning"
    assert window.db.one("SELECT COUNT(*) FROM projects")[0] == 0
    assert "La dernière veille" in window.db.setting("pending_guided_project")

    window._create_project_from_learning()
    project = window.db.one("SELECT * FROM projects")
    assert project["title"] == "La dernière veille"
    assert project["story_format"] == "micro"
    assert project["target_duration"] == 5
    assert project["start_mode"] == "guided"
    assert window.db.setting("pending_guided_project") == ""

    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_theme_workspace_saves_positions_motifs_and_connections(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "theme-ui.db")
    project_id = window._create_empty_project(
        {
            "title": "La fenêtre fermée",
            "project_type": "film",
            "story_format": "short",
            "target_duration": 12,
            "start_mode": "free",
        }
    )
    character_id = window.db.run(
        """INSERT INTO characters(project_id,name,role,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, "Mina", "Protagoniste", NOW(), NOW()),
    ).lastrowid
    track_id = int(window.db.ensure_timeline_track(project_id, "Intrigue principale")["id"])
    event_id = window.db.run(
        """INSERT INTO timeline_events(project_id,track_id,title,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, track_id, "Mina ferme la fenêtre", NOW(), NOW()),
    ).lastrowid
    location_id = window.db.run(
        """INSERT INTO locations(project_id,position,name,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, 0, "Chambre de Mina", NOW(), NOW()),
    ).lastrowid
    image_id = window.db.run(
        """INSERT INTO image_library(project_id,title,category,image_data,created_at,updated_at)
        VALUES(?,?,?,?,?,?)""",
        (project_id, "Fenêtre", "Objet", b"image", NOW(), NOW()),
    ).lastrowid
    window.active_project = project_id
    window.db.set_setting("active_project", project_id)
    window.show_theme()
    app.processEvents()
    assert window.theme_tabs.count() == 5
    assert [window.theme_tabs.tabText(index) for index in range(4)] == [
        "Question", "Positions", "Expression", "Motifs"
    ]

    window.theme_profile_fields["theme_word"].setText("Confiance")
    window.theme_profile_fields["central_question"].setPlainText(
        "Peut-on protéger sans contrôler ?"
    )
    window.theme_profile_fields["ending_response"].setPlainText(
        "Mina accepte de ne pas tout savoir."
    )
    window._save_theme_profile()
    assert window.db.one(
        "SELECT central_question FROM theme_profiles WHERE project_id=?", (project_id,)
    )[0] == "Peut-on protéger sans contrôler ?"

    window.theme_tabs.setCurrentIndex(1)
    window.theme_position_fields["label"].setText("Contrôler protège")
    window.theme_position_fields["stance"].setPlainText("Mina le croit au début.")
    position_character = window.theme_position_characters.item(0)
    assert int(position_character.data(Qt.ItemDataRole.UserRole)) == character_id
    position_character.setCheckState(Qt.CheckState.Checked)
    window._save_theme_position()
    position_id = int(window.db.one(
        "SELECT id FROM theme_positions WHERE project_id=?", (project_id,)
    )[0])
    assert window.db.one(
        "SELECT COUNT(*) FROM theme_position_characters WHERE position_id=?", (position_id,)
    )[0] == 1

    window.theme_tabs.setCurrentIndex(3)
    window.theme_motif_fields["name"].setText("La fenêtre")
    window.theme_motif_fields["motif_type"].setCurrentText("Objet")
    window.theme_motif_fields["meaning"].setPlainText("Ouverture ou contrôle.")
    for key, target_id in (
        ("locations", location_id),
        ("events", event_id),
        ("images", image_id),
    ):
        picker = window.theme_motif_connection_lists[key]
        item = next(
            picker.item(index)
            for index in range(picker.count())
            if int(picker.item(index).data(Qt.ItemDataRole.UserRole)) == target_id
        )
        item.setCheckState(Qt.CheckState.Checked)
    window._save_theme_motif()
    motif_id = int(window.db.one(
        "SELECT id FROM theme_motifs WHERE project_id=?", (project_id,)
    )[0])
    for table in ("theme_motif_locations", "theme_motif_events", "theme_motif_images"):
        assert window.db.one(f"SELECT COUNT(*) FROM {table} WHERE motif_id=?", (motif_id,))[0] == 1

    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_conflict_workspace_prefills_and_connects_project_elements(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "conflict-ui.db")
    project_id = window._create_empty_project(
        {
            "title": "La ville fermée",
            "project_type": "film",
            "story_format": "short",
            "target_duration": 18,
            "start_mode": "free",
        }
    )
    window.db.run(
        """UPDATE projects SET protagonist=?,objective=?,opposition=?,stakes=?,change_note=? WHERE id=?""",
        ("Mina", "Livrer la lettre", "Le Conseil ferme les portes", "Son frère sera condamné", "Mina choisit d’agir", project_id),
    )
    character_id = window.db.run(
        "INSERT INTO characters(project_id,name,role,created_at,updated_at) VALUES(?,?,?,?,?)",
        (project_id, "Mina", "Protagoniste", NOW(), NOW()),
    ).lastrowid
    group_id = window.db.run(
        "INSERT INTO character_groups(project_id,name,group_type,created_at,updated_at) VALUES(?,?,?,?,?)",
        (project_id, "Conseil", "Faction", NOW(), NOW()),
    ).lastrowid
    scene_id = window.db.run(
        "INSERT INTO scene_rows(project_id,position,title,created_at,updated_at) VALUES(?,?,?,?,?)",
        (project_id, 0, "La porte refuse de s’ouvrir", NOW(), NOW()),
    ).lastrowid
    node_id = window.db.create_story_map_node(
        project_id, "Premier refus", "Le Conseil bloque Mina.", "obstacle", 100, 100
    )
    track_id = int(window.db.ensure_timeline_track(project_id, "Intrigue principale")["id"])
    event_id = window.db.run(
        "INSERT INTO timeline_events(project_id,track_id,title,created_at,updated_at) VALUES(?,?,?,?,?)",
        (project_id, track_id, "Fermeture des portes", NOW(), NOW()),
    ).lastrowid
    theme_position_id = window.db.run(
        """INSERT INTO theme_positions(
        project_id,position,position_type,label,stance,nuance,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?)""",
        (project_id, 0, "main", "Obéir protège", "Le Conseil le croit.", "L’ordre enferme.", NOW(), NOW()),
    ).lastrowid
    for key, answer in (
        ("disrupting_event", "Les portes ferment à l’aube."),
        ("escalation", "Mina devient recherchée."),
        ("final_confrontation", "Mina lit la lettre en public."),
        ("resolution_change", "Une enquête commence."),
    ):
        window.db.save_story_map_answer(project_id, key, answer)
    window.active_project = project_id
    window.db.set_setting("active_project", project_id)
    window.show_conflicts()
    app.processEvents()

    assert window.conflict_tabs.count() == 4
    assert [window.conflict_tabs.tabText(index) for index in range(4)] == [
        "Noyau", "Forces", "Progression", "Connexions"
    ]
    assert window.conflict_fields["title"].text() == "Conflit principal"
    assert window.conflict_fields["side_a_label"].text() == "Mina"
    assert window.conflict_fields["side_a_goal"].toPlainText() == "Livrer la lettre"
    assert window.conflict_fields["trigger_note"].toPlainText().startswith("Les portes")
    assert int(
        window.conflict_side_lists[("characters", "a")].item(0).data(Qt.ItemDataRole.UserRole)
    ) == character_id
    assert window.conflict_side_lists[("characters", "a")].item(0).checkState() == Qt.CheckState.Checked

    window.conflict_fields["side_b_goal"].setPlainText("Empêcher la révélation du crime")
    window.conflict_fields["incompatibility"].setPlainText("La lettre accuse directement le Conseil.")
    window.conflict_fields["difficult_choice"].setPlainText("Sauver son alliée ou atteindre le juge.")
    for picker_key, target_id in (
        (("groups", "b"), group_id),
    ):
        picker = window.conflict_side_lists[picker_key]
        item = next(
            picker.item(index)
            for index in range(picker.count())
            if int(picker.item(index).data(Qt.ItemDataRole.UserRole)) == target_id
        )
        item.setCheckState(Qt.CheckState.Checked)
    for key, target_id in (
        ("scenes", scene_id),
        ("nodes", node_id),
        ("events", event_id),
        ("theme_positions", theme_position_id),
    ):
        picker = window.conflict_connection_lists[key]
        item = next(
            picker.item(index)
            for index in range(picker.count())
            if int(picker.item(index).data(Qt.ItemDataRole.UserRole)) == target_id
        )
        item.setCheckState(Qt.CheckState.Checked)
    window._save_conflict()
    conflict = window.db.one("SELECT * FROM conflicts WHERE project_id=?", (project_id,))
    assert conflict["importance"] == "primary"
    assert conflict["side_b_goal"].startswith("Empêcher")
    assert window.conflict_list.count() == 1
    for table in (
        "conflict_characters", "conflict_groups", "conflict_scenes",
        "conflict_story_nodes", "conflict_events", "conflict_theme_positions",
    ):
        assert window.db.one(
            f"SELECT COUNT(*) FROM {table} WHERE conflict_id=?", (int(conflict["id"]),)
        )[0] == 1

    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_character_arcs_compare_sync_and_connect_project_elements(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "arcs-ui.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage,updated_at) VALUES(?,?,?,?)",
        (NOW(), "La mue", "Développement", NOW()),
    ).lastrowid
    character_id = window.db.run(
        """INSERT INTO characters(
        project_id,name,role,start_situation,arc,end_situation,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?)""",
        (
            project_id,
            "Mina",
            "Protagoniste",
            "Mina évite toute responsabilité.",
            "",
            "",
            NOW(),
            NOW(),
        ),
    ).lastrowid
    scene_id = window.db.run(
        """INSERT INTO scene_rows(project_id,position,title,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, 0, "Le choix de Mina", NOW(), NOW()),
    ).lastrowid
    node_id = window.db.create_story_map_node(
        project_id,
        "Mina revient",
        "Elle choisit de revenir malgré le danger.",
        "choice",
    )
    track_id = int(window.db.ensure_timeline_track(project_id)["id"])
    event_id = window.db.run(
        """INSERT INTO timeline_events(project_id,track_id,title,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, track_id, "Retour de Mina", NOW(), NOW()),
    ).lastrowid
    conflict_id = window.db.run(
        """INSERT INTO conflicts(project_id,position,title,importance,nature,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?)""",
        (project_id, 0, "Fuir ou assumer", "main", "internal", NOW(), NOW()),
    ).lastrowid
    window.active_project = project_id
    window.db.set_setting("active_project", project_id)
    window.show_arcs()
    window.show()
    app.processEvents()

    assert window.arc_character_id == character_id
    assert [window.arc_tabs.tabText(index) for index in range(window.arc_tabs.count())] == [
        "Vue d’ensemble", "Trajectoire", "Connexions"
    ]
    assert window.arc_overview_table.rowCount() == 1
    assert window.arc_fields["start_situation"].toPlainText().startswith("Mina évite")
    window.arc_fields["arc_type"].setCurrentText("Transformation positive")
    window.arc_fields["initial_belief"].setPlainText("Demander de l’aide est une faiblesse.")
    window.arc_fields["main_trial"].setPlainText("Son frère reste enfermé à cause de sa fuite.")
    window.arc_fields["breaking_point"].setPlainText("Elle découvre qu’il l’a protégée.")
    window.arc_fields["decisive_choice"].setPlainText("Elle revient témoigner.")
    window.arc_fields["transformation"].setPlainText("Mina accepte d’agir avec les autres.")
    window.arc_fields["end_situation"].setPlainText("Mina assume publiquement sa décision.")
    window.arc_fields["visible_proof"].setPlainText("Elle demande de l’aide au lieu de partir seule.")
    for key, target_id in (
        ("scenes", scene_id),
        ("story_nodes", node_id),
        ("events", event_id),
        ("conflicts", conflict_id),
    ):
        picker = window.arc_connection_lists[key]
        item = next(
            picker.item(index)
            for index in range(picker.count())
            if int(picker.item(index).data(Qt.ItemDataRole.UserRole)) == target_id
        )
        item.setCheckState(Qt.CheckState.Checked)
    window._save_character_arc()

    character = window.db.one(
        "SELECT start_situation,arc,end_situation FROM characters WHERE id=?",
        (character_id,),
    )
    arc = window.db.one("SELECT * FROM character_arcs WHERE character_id=?", (character_id,))
    assert character["arc"].startswith("Mina accepte")
    assert character["end_situation"].startswith("Mina assume")
    assert arc["arc_type"] == "Transformation positive"
    assert arc["decisive_choice"] == "Elle revient témoigner."
    for table in (
        "character_arc_scenes",
        "character_arc_story_nodes",
        "character_arc_events",
        "character_arc_conflicts",
    ):
        assert window.db.one(
            f"SELECT COUNT(*) FROM {table} WHERE arc_id=?", (int(arc["id"]),)
        )[0] == 1
    assert window.arc_diagnostic.text() == "6/6 REPÈRES"

    window.show_characters()
    app.processEvents()
    assert window.character_fields["arc"].toPlainText().startswith("Mina accepte")
    assert window.character_fields["end_situation"].toPlainText().startswith("Mina assume")

    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()


def test_hook_promises_and_desired_moments_connect_to_project(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "promises-ui.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage,updated_at) VALUES(?,?,?,?)",
        (NOW(), "Les portes", "Développement", NOW()),
    ).lastrowid
    node_id = window.db.create_story_map_node(project_id, "La porte close", "Mina frappe.", "obstacle")
    sequence_id = window.db.create_sequence_block(project_id, 0, "Le refus")
    scene_id = window.db.run(
        "INSERT INTO scene_rows(project_id,position,title,created_at,updated_at) VALUES(?,?,?,?,?)",
        (project_id, 0, "La porte", NOW(), NOW()),
    ).lastrowid
    track_id = int(window.db.ensure_timeline_track(project_id)["id"])
    event_id = window.db.run(
        "INSERT INTO timeline_events(project_id,track_id,title,created_at,updated_at) VALUES(?,?,?,?,?)",
        (project_id, track_id, "La ville ferme", NOW(), NOW()),
    ).lastrowid
    conflict_id = window.db.run(
        """INSERT INTO conflicts(project_id,position,title,importance,nature,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?)""",
        (project_id, 0, "Mina contre le Conseil", "main", "social", NOW(), NOW()),
    ).lastrowid
    window.active_project = project_id
    window.db.set_setting("active_project", project_id)
    window.show_promises()
    window.show()
    app.processEvents()

    assert [window.promise_tabs.tabText(index) for index in range(window.promise_tabs.count())] == [
        "Accroche", "Promesses", "Moments forts", "Vue de contrôle"
    ]
    window.hook_fields["hook_question"].setPlainText("Pourquoi la ville refuse-t-elle de rouvrir ses portes ?")
    window.hook_fields["unusual_situation"].setPlainText("Une lettre arrive après la fermeture définitive.")
    window.hook_fields["audience_question"].setPlainText("Mina réussira-t-elle à la livrer ?")
    window.hook_fields["withheld_answer"].setPlainText("Ce que contient réellement la lettre.")
    window._save_hook_profile()
    assert window.db.one("SELECT hook_question FROM hook_profiles WHERE project_id=?", (project_id,))[0].startswith("Pourquoi")

    window._new_story_promise()
    window.story_promise_fields["title"].setText("La lettre changera la ville")
    window.story_promise_fields["promise_type"].setCurrentText("Mystère")
    window.story_promise_fields["status"].setCurrentText("Développée")
    window.story_promise_fields["description"].setPlainText("Son contenu aura une conséquence publique.")
    window.story_promise_fields["planted_note"].setPlainText("La lettre est scellée.")
    window.story_promise_fields["development_note"].setPlainText("Plusieurs groupes tentent de la prendre.")
    window.story_promise_fields["payoff_note"].setPlainText("Mina la lit devant le Conseil.")
    for key, target_id in (("story_nodes", node_id), ("scenes", scene_id)):
        picker = window.story_promise_connections[key]
        item = next(
            picker.item(index)
            for index in range(picker.count())
            if int(picker.item(index).data(Qt.ItemDataRole.UserRole)) == target_id
        )
        item.setCheckState(Qt.CheckState.Checked)
    window._save_story_promise()
    promise = window.db.one("SELECT * FROM story_promises WHERE project_id=?", (project_id,))
    assert promise["promise_type"] == "Mystère"
    assert window.db.one("SELECT COUNT(*) FROM story_promise_story_nodes WHERE promise_id=?", (promise["id"],))[0] == 1
    assert window.db.one("SELECT COUNT(*) FROM story_promise_scenes WHERE promise_id=?", (promise["id"],))[0] == 1

    window._new_story_moment()
    window.story_moment_fields["title"].setText("Mina lit la lettre")
    window.story_moment_fields["moment_type"].setCurrentText("Climax")
    window.story_moment_fields["description"].setPlainText("Elle révèle les noms inscrits dans la lettre.")
    window.story_moment_fields["narrative_function"].setPlainText("Résoudre le conflit public.")
    window.story_moment_fields["placement_note"].setPlainText("Après l’affrontement avec le Conseil.")
    for key, target_id in (("sequences", sequence_id), ("events", event_id), ("conflicts", conflict_id)):
        picker = window.story_moment_connections[key]
        item = next(
            picker.item(index)
            for index in range(picker.count())
            if int(picker.item(index).data(Qt.ItemDataRole.UserRole)) == target_id
        )
        item.setCheckState(Qt.CheckState.Checked)
    window._save_story_moment()
    moment = window.db.one("SELECT * FROM story_moments WHERE project_id=?", (project_id,))
    assert moment["moment_type"] == "Climax"
    for table in ("story_moment_sequences", "story_moment_events", "story_moment_conflicts"):
        assert window.db.one(f"SELECT COUNT(*) FROM {table} WHERE moment_id=?", (moment["id"],))[0] == 1

    window._convert_story_moment("story_node")
    window._convert_story_moment("sequence")
    window._convert_story_moment("scene")
    assert window.db.one("SELECT COUNT(*) FROM story_moment_story_nodes WHERE moment_id=?", (moment["id"],))[0] == 1
    assert window.db.one("SELECT COUNT(*) FROM story_moment_sequences WHERE moment_id=?", (moment["id"],))[0] == 2
    assert window.db.one("SELECT COUNT(*) FROM story_moment_scenes WHERE moment_id=?", (moment["id"],))[0] == 1
    assert window.story_moment_fields["status"].currentText() == "Placée"

    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()
