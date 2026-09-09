from pathlib import Path

import pytest
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QComboBox, QDialog, QPushButton, QScrollArea, QTextEdit

from storyforge.app import GUIDE_ORDER, GUIDE_SESSIONS, LEARNING_TOOL_LINKS, StoryForgeWindow
from storyforge.db import Database, NOW
from storyforge.learning_service import LearningService, OUTLINE_GUIDE_FIELDS


def setup_project(db: Database):
    project_id = db.run(
        'INSERT INTO projects(created_at,title,stage,updated_at) VALUES(?,?,?,?)',
        (NOW(), 'Projet fictif', 'Plan', NOW()),
    ).lastrowid
    item_id = db.create_outline_item(project_id, 0, 'beat', 'Décision initiale')
    run_id = db.create_guided_run(
        'build_outline', 'Plan de travail', project_id=project_id,
    )
    return project_id, item_id, run_id


@pytest.fixture
def context(tmp_path: Path):
    db = Database(tmp_path / 'outline-guide.db')
    project_id, item_id, run_id = setup_project(db)
    yield db, LearningService(db), GUIDE_SESSIONS['build_outline'], project_id, item_id, run_id
    db.conn.close()


def test_content_distinguishes_diagnostic_and_applied_steps(context):
    _, service, session, _, item_id, run_id = context
    assert 'build_outline' in GUIDE_ORDER
    assert len(session.steps) == 7
    assert set(OUTLINE_GUIDE_FIELDS) == {
        'unit_title', 'unit_function', 'unit_content', 'unit_consequence',
    }
    for step in session.steps:
        assert step.optional and step.review and step.example and step.tips
        link = LEARNING_TOOL_LINKS['build_outline'][step.key]
        assert link[:2] == ('development', 'outline')
        if step.key in OUTLINE_GUIDE_FIELDS:
            assert link[3:5] == ('outline_item', OUTLINE_GUIDE_FIELDS[step.key][0])
        else:
            assert link[3:5] == ('project', '')
    with pytest.raises(ValueError):
        service.apply_field_answer(run_id, session, 0, 'Diagnostic', item_id, '')


def test_confirmed_answers_update_only_the_selected_outline_fields(context):
    db, service, session, project_id, item_id, run_id = context
    for index, step in enumerate(session.steps[1:5], 1):
        field, _label = OUTLINE_GUIDE_FIELDS[step.key]
        before = db.one('SELECT * FROM outline_items WHERE id=?', (item_id,))[field] or ''
        mode = 'replace' if field == 'title' else 'append'
        service.apply_field_answer(run_id, session, index, f'Essai {index}', item_id, before, mode)
        item = db.one('SELECT * FROM outline_items WHERE id=?', (item_id,))
        assert item[field] == f'Essai {index}'
        application = db.guided_application(run_id, step.key)
        assert (application['target_type'], application['target_id'], application['target_field']) == (
            'outline_item', item_id, field,
        )

    with pytest.raises(ValueError, match='changé'):
        service.apply_field_answer(run_id, session, 1, 'Autre titre', item_id, 'Décision initiale')
    other_project, other_item, _ = setup_project(db)
    assert other_project != project_id
    with pytest.raises(ValueError, match='ce projet'):
        service.apply_field_answer(run_id, session, 1, 'Interdit', other_item, '')


def test_linked_sequences_and_scenes_remain_synchronized(context):
    db, service, session, project_id, _, run_id = context
    sequence_id = db.create_sequence_block(
        project_id, 0, 'Séquence', purpose='But', events='Événements', consequence='Suite',
    )
    sequence_item = db.create_outline_item(
        project_id, 1, 'sequence', 'Séquence', 'Événements', 'But', 'Suite',
        source_sequence_id=sequence_id,
    )
    scene_id = db.run(
        '''INSERT INTO scene_rows(
        project_id,position,title,objective,opposition,change_note,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?)''',
        (project_id, 0, 'Scène', 'Objectif', 'Opposition', 'Changement', NOW(), NOW()),
    ).lastrowid
    scene_item = db.create_outline_item(
        project_id, 2, 'scene', 'Scène', 'Opposition', 'Objectif', 'Changement',
        source_scene_id=scene_id,
    )

    service.apply_field_answer(run_id, session, 2, 'Nouvelle fonction', sequence_item, 'But', 'replace')
    service.apply_field_answer(run_id, session, 3, 'Nouvelle opposition', scene_item, 'Opposition', 'replace')
    assert db.one('SELECT purpose FROM sequence_blocks WHERE id=?', (sequence_id,))[0] == 'Nouvelle fonction'
    assert db.one('SELECT opposition FROM scene_rows WHERE id=?', (scene_id,))[0] == 'Nouvelle opposition'


def test_application_is_atomic_and_export_remaps_the_outline_target(context, tmp_path: Path, monkeypatch):
    db, service, session, project_id, item_id, run_id = context

    def fail(*_args):
        raise RuntimeError('Échec simulé')

    monkeypatch.setattr(db, 'save_guided_application', fail)
    with pytest.raises(RuntimeError):
        service.apply_field_answer(run_id, session, 1, 'Nouveau titre', item_id, 'Décision initiale')
    assert db.one('SELECT title FROM outline_items WHERE id=?', (item_id,))[0] == 'Décision initiale'
    assert not db.q('SELECT * FROM guided_answers')
    monkeypatch.undo()

    service.apply_field_answer(run_id, session, 1, 'Nouveau titre', item_id, 'Décision initiale', 'replace')
    path = tmp_path / 'project.storyforge.json'
    db.export_project(project_id, path)
    imported_project = db.import_project(path)
    imported_run = db.one(
        "SELECT * FROM guided_runs WHERE project_id=? AND guide_key='build_outline'",
        (imported_project,),
    )
    imported_item = db.one(
        "SELECT * FROM outline_items WHERE project_id=? AND title='Nouveau titre'",
        (imported_project,),
    )
    application = db.guided_application(imported_run['id'], 'unit_title')
    assert application['target_id'] == imported_item['id']


def test_ui_preview_confirmation_and_navigation_to_the_selected_cell(tmp_path: Path):
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / 'ui.db')
    project_id, item_id, run_id = setup_project(window.db)
    window.active_project = project_id
    window.db.set_setting('active_project', project_id)
    window.resize(1280, 800)
    window.show()
    window.show_learning(run_id=run_id)
    app.processEvents()
    assert window.findChild(QScrollArea, 'OutlineGuideScroll')
    assert window.learning_target_combo is None
    assert not any(
        button.text() == 'Prévisualiser la réponse'
        for button in window.findChildren(QPushButton)
    )

    window._learning_step(1)
    window.learning_draft.setPlainText('Mina accepte la commande')
    window.learning_target_combo.setCurrentIndex(window.learning_target_combo.findData(item_id))
    errors = []

    def confirm_preview():
        dialog = app.activeModalWidget()
        try:
            assert isinstance(dialog, QDialog)
            assert dialog.objectName() == 'OutlineGuidePreview'
            assert dialog.findChild(QComboBox, 'OutlineGuideApplyMode').currentData() == 'replace'
            assert 'Mina accepte' in dialog.findChild(QTextEdit).toPlainText()
            next(
                button for button in dialog.findChildren(QPushButton)
                if button.text() == 'Confirmer l’application'
            ).click()
        except Exception as exc:
            errors.append(exc)
            if dialog:
                dialog.reject()

    QTimer.singleShot(0, confirm_preview)
    window._preview_field_answer()
    assert not errors
    assert window.db.one('SELECT title FROM outline_items WHERE id=?', (item_id,))[0] == 'Mina accepte la commande'
    assert 'Mina accepte la commande' in window.db.one(
        "SELECT content FROM project_docs WHERE project_id=? AND doc_type='outline'",
        (project_id,),
    )[0]

    window._learning_step(3)
    window.learning_draft.setPlainText('Une pièce manque.')
    window.learning_target_combo.setCurrentIndex(window.learning_target_combo.findData(item_id))
    window._open_learning_tool()
    app.processEvents()
    assert window.current_view == 'development'
    assert window.development_doc_type == 'outline'
    assert window.db.setting(f'outline_mode_{project_id}') == 'global'
    assert int(window.outline_tree.currentItem().data(0, Qt.ItemDataRole.UserRole)) == item_id
    assert window.outline_tree.currentColumn() == 2
    window._return_to_learning()
    assert window._learning_idx == 3
    window.close()
    app.processEvents()
