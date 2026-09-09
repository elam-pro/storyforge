import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel

from app import StoryForgeWindow
from db import NOW, Database


def _project(db: Database, title: str = "Projet guidé") -> int:
    return int(
        db.run(
            "INSERT INTO projects(created_at,title,stage,updated_at) VALUES(?,?,?,?)",
            (NOW(), title, "Noyau", NOW()),
        ).lastrowid
    )


def test_a_learning_step_opens_its_project_tool_and_returns_to_the_guide(
    tmp_path: Path,
) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "connected.db")
    window.show()
    app.processEvents()
    project_id = _project(window.db)
    character_id = int(
        window.db.run(
            """INSERT INTO characters(project_id,name,role,created_at,updated_at)
            VALUES(?,?,?,?,?)""",
            (project_id, "Mina", "Protagoniste", NOW(), NOW()),
        ).lastrowid
    )
    run_id = window.db.create_guided_run(
        "seed", "Graine reliée", project_id=project_id, assistance_level="guided"
    )
    window.db.update_guided_run(run_id, current_step=2)
    window.active_project = project_id
    window.db.set_setting("active_project", project_id)
    window._update_project_chips()

    window.show_learning(run_id=run_id)
    window.learning_draft.setPlainText("Mina, gardienne de nuit qui protège sa sœur.")
    target_index = window.learning_target_combo.findData(character_id)
    assert target_index >= 0
    window.learning_target_combo.setCurrentIndex(target_index)
    window._open_learning_tool()
    app.processEvents()

    assert window.current_view == "characters"
    assert window.db.setting(f"last_character_{project_id}") == str(character_id)
    assert window.guide_return_button.isVisible()
    application = window.db.guided_application(run_id, "protagonist")
    assert application["project_id"] == project_id
    assert application["target_type"] == "character"
    assert application["target_id"] == character_id
    assert application["status"] == "en pratique"
    assert window.db.one(
        "SELECT status FROM concept_mastery WHERE concept_key='protagoniste'"
    )["status"] == "en pratique"

    window._return_to_learning()
    app.processEvents()
    assert window.current_view == "learning"
    assert window._learning_idx == 2
    assert not window.guide_return_button.isVisible()
    assert window.findChild(QLabel, "LearningApplicationHistoryCount").text().startswith("1 trace")
    window._set_learning_mastery("acquis")
    assert window.db.one(
        "SELECT status FROM concept_mastery WHERE concept_key='protagoniste'"
    )["status"] == "acquis"
    assert window.db.guided_application(run_id, "protagonist")["status"] == "acquis"
    assert window.findChild(QLabel, "LearningApplicationHistoryCount").text().startswith("2 traces")
    window.close()


def test_guided_applications_follow_a_project_export_and_import(tmp_path: Path) -> None:
    db = Database(tmp_path / "source.db")
    project_id = _project(db, "Histoire exportée")
    character_id = int(
        db.run(
            """INSERT INTO characters(project_id,name,role,created_at,updated_at)
            VALUES(?,?,?,?,?)""",
            (project_id, "Mina", "Protagoniste", NOW(), NOW()),
        ).lastrowid
    )
    run_id = db.create_guided_run("seed", "Guide", project_id=project_id)
    db.save_guided_answer(run_id, "protagonist", 2, "Une gardienne", "complete")
    db.save_guided_application(
        run_id,
        "protagonist",
        project_id,
        "character",
        character_id,
        "description",
        "acquis",
        "Une gardienne",
    )
    db.record_guided_application_event(
        run_id, "protagonist", project_id, "character", character_id,
        "description", "applied", "en pratique", "Première version",
    )
    db.record_guided_application_event(
        run_id, "protagonist", project_id, "character", character_id,
        "description", "mastery", "acquis", "Une gardienne",
    )
    exported = tmp_path / "project.storyforge.json"
    db.export_project(project_id, exported)

    imported_project_id = db.import_project(exported)
    imported_run = db.one(
        "SELECT id FROM guided_runs WHERE project_id=?", (imported_project_id,)
    )
    imported_application = db.guided_application(imported_run["id"], "protagonist")
    imported_character = db.one(
        "SELECT id FROM characters WHERE project_id=? AND name='Mina'",
        (imported_project_id,),
    )
    assert imported_application["target_id"] == imported_character["id"]
    assert imported_application["status"] == "acquis"
    imported_history = db.guided_application_history(imported_run["id"], "protagonist")
    assert [row["event_kind"] for row in imported_history] == ["applied", "mastery"]
    assert all(row["target_id"] == imported_character["id"] for row in imported_history)
    db.conn.close()
