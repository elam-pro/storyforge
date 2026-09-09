from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QComboBox, QScrollArea

from storyforge.app import GUIDE_ORDER, GUIDE_SESSIONS, LEARNING_TOOL_LINKS, StoryForgeWindow
from storyforge.db import Database, NOW
from storyforge.learning_service import (
    LearningService,
    RELATIONSHIP_GUIDE_FIELDS,
    THEME_GUIDE_FIELDS,
    UNIVERSE_GUIDE_FIELDS,
)


def create_project(db: Database) -> int:
    return int(db.run(
        "INSERT INTO projects(created_at,title,stage,updated_at) VALUES(?,?,?,?)",
        (NOW(), "Projet guidé", "Idée", NOW()),
    ).lastrowid)


@pytest.mark.parametrize(
    ("guide_key", "expected_steps"),
    (
        ("build_universe", 7),
        ("build_relationship", 5),
        ("build_theme", 6),
        ("rewrite_pass", 6),
    ),
)
def test_extended_guide_content_is_complete_and_connected(guide_key: str, expected_steps: int) -> None:
    session = GUIDE_SESSIONS[guide_key]
    assert guide_key in GUIDE_ORDER
    assert len(session.steps) == expected_steps
    assert set(LEARNING_TOOL_LINKS[guide_key]) == {step.key for step in session.steps}
    for step in session.steps:
        assert step.optional
        assert step.question and step.why and step.example and step.placeholder
        assert step.tips and step.review


@pytest.mark.parametrize(
    ("guide_key", "fields", "table"),
    (
        ("build_universe", UNIVERSE_GUIDE_FIELDS, "world_profiles"),
        ("build_theme", THEME_GUIDE_FIELDS, "theme_profiles"),
    ),
)
def test_project_profile_guides_create_and_update_only_confirmed_fields(
    tmp_path: Path,
    guide_key: str,
    fields: dict[str, tuple[str, str]],
    table: str,
) -> None:
    db = Database(tmp_path / f"{guide_key}.db")
    project_id = create_project(db)
    run_id = db.create_guided_run(guide_key, "Essai", project_id=project_id)
    service = LearningService(db)
    session = GUIDE_SESSIONS[guide_key]
    step_index = next(index for index, step in enumerate(session.steps) if step.key in fields)
    step = session.steps[step_index]
    field, _label = fields[step.key]

    service.apply_field_answer(run_id, session, step_index, "Première piste", project_id, "")
    assert db.one(f"SELECT {field} FROM {table} WHERE project_id=?", (project_id,))[0] == "Première piste"
    service.apply_field_answer(
        run_id, session, step_index, "Version retenue", project_id, "Première piste", "replace",
    )
    assert db.one(f"SELECT {field} FROM {table} WHERE project_id=?", (project_id,))[0] == "Version retenue"
    other_project = create_project(db)
    with pytest.raises(ValueError, match="ce projet"):
        service.apply_field_answer(run_id, session, step_index, "Interdit", other_project, "")
    db.conn.close()


def test_relationship_guide_targets_one_directional_relation(tmp_path: Path) -> None:
    db = Database(tmp_path / "relationship-guide.db")
    project_id = create_project(db)
    first = db.run(
        "INSERT INTO characters(project_id,name,created_at,updated_at) VALUES(?,?,?,?)",
        (project_id, "Mina", NOW(), NOW()),
    ).lastrowid
    second = db.run(
        "INSERT INTO characters(project_id,name,created_at,updated_at) VALUES(?,?,?,?)",
        (project_id, "Sarah", NOW(), NOW()),
    ).lastrowid
    relation_id = db.run(
        """INSERT INTO character_relationships(
        project_id,character_a_id,character_b_id,relationship_type,created_at,updated_at
        ) VALUES(?,?,?,?,?,?)""",
        (project_id, first, second, "Respect", NOW(), NOW()),
    ).lastrowid
    run_id = db.create_guided_run("build_relationship", "Mina et Sarah", project_id=project_id)
    session = GUIDE_SESSIONS["build_relationship"]
    service = LearningService(db)
    index = next(index for index, step in enumerate(session.steps) if step.key == "tension")

    service.apply_field_answer(run_id, session, index, "Elles veulent toutes deux décider.", relation_id, "")
    row = db.one("SELECT * FROM character_relationships WHERE id=?", (relation_id,))
    assert row["tension"] == "Elles veulent toutes deux décider."
    application = db.guided_application(run_id, "tension")
    assert (application["target_type"], application["target_id"]) == ("relationship", relation_id)
    db.conn.close()


def test_extended_guides_render_their_connected_controls(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "extended-guides-ui.db")
    project_id = create_project(window.db)
    window.active_project = project_id

    universe_run = window.db.create_guided_run(
        "build_universe", "Monde", project_id=project_id,
    )
    window.show_learning(run_id=universe_run)
    app.processEvents()
    assert window.findChild(QScrollArea, "UniverseGuideScroll")
    assert window.learning_target_combo is None

    first = window.db.run(
        "INSERT INTO characters(project_id,name,created_at,updated_at) VALUES(?,?,?,?)",
        (project_id, "Mina", NOW(), NOW()),
    ).lastrowid
    second = window.db.run(
        "INSERT INTO characters(project_id,name,created_at,updated_at) VALUES(?,?,?,?)",
        (project_id, "Sarah", NOW(), NOW()),
    ).lastrowid
    relation_id = window.db.run(
        """INSERT INTO character_relationships(
        project_id,character_a_id,character_b_id,relationship_type,created_at,updated_at
        ) VALUES(?,?,?,?,?,?)""",
        (project_id, first, second, "Respect", NOW(), NOW()),
    ).lastrowid
    relation_run = window.db.create_guided_run(
        "build_relationship", "Lien", project_id=project_id,
    )
    window.db.update_guided_run(relation_run, current_step=1)
    window.show_learning(run_id=relation_run)
    app.processEvents()
    assert window.findChild(QScrollArea, "RelationshipGuideScroll")
    assert isinstance(window.learning_target_combo, QComboBox)
    assert window.learning_target_combo.findData(relation_id) > 0

    window.autosave_timer.stop()
    window.db.conn.close()
    window.deleteLater()
    app.processEvents()
