import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QComboBox, QDialog, QPushButton, QScrollArea, QTextEdit

from storyforge.app import GUIDE_ORDER, GUIDE_SESSIONS, LEARNING_TOOL_LINKS, SYNOPSIS_STEPS, StoryForgeWindow
from storyforge.db import Database, NOW
from storyforge.learning_service import LearningService, SYNOPSIS_GUIDE_STEPS


def setup_project(db):
    project_id = db.run(
        'INSERT INTO projects(created_at,title,stage,updated_at) VALUES(?,?,?,?)',
        (NOW(), 'Projet fictif', 'Carte', NOW()),
    ).lastrowid
    run_id = db.create_guided_run(
        'build_synopsis', 'Premier synopsis', project_id=project_id,
    )
    return project_id, run_id


@pytest.fixture
def context(tmp_path):
    db = Database(tmp_path / 'synopsis-guide.db')
    project_id, run_id = setup_project(db)
    yield db, LearningService(db), GUIDE_SESSIONS['build_synopsis'], project_id, run_id
    db.conn.close()


def test_content_matches_the_existing_synopsis_workspace(context):
    _, _, session, _, _ = context
    assert 'build_synopsis' in GUIDE_ORDER
    assert len(session.steps) == len(SYNOPSIS_STEPS) == 6
    assert list(SYNOPSIS_GUIDE_STEPS) == [step['key'] for step in SYNOPSIS_STEPS]
    for step in session.steps:
        assert step.optional and step.review and step.example and step.tips
        link = LEARNING_TOOL_LINKS['build_synopsis'][step.key]
        assert link[:2] == ('development', 'synopsis')
        assert link[3:] == ('project', step.key, link[5])


def test_confirmed_passage_adds_or_replaces_without_touching_final_text(context):
    db, service, session, project_id, run_id = context
    db.save_synopsis_answer(project_id, 'opening_situation', 'Passage existant')
    db.ensure_doc(project_id, 'synopsis', 'Synopsis')
    db.save_doc(project_id, 'synopsis', 'Synopsis final conservé')

    service.apply_synopsis_answer(
        run_id, session, 0, 'Nouvelle piste', 'Passage existant', 'append',
    )
    assert db.one(
        "SELECT answer FROM synopsis_answers WHERE project_id=? AND step_key='opening_situation'",
        (project_id,),
    )[0] == 'Passage existant\n\nNouvelle piste'
    assert db.one(
        "SELECT content FROM project_docs WHERE project_id=? AND doc_type='synopsis'",
        (project_id,),
    )[0] == 'Synopsis final conservé'
    application = db.guided_application(run_id, 'opening_situation')
    assert (application['target_type'], application['target_id'], application['target_field']) == (
        'project', 0, 'opening_situation',
    )

    with pytest.raises(ValueError, match='changé'):
        service.apply_synopsis_answer(
            run_id, session, 0, 'Révision', 'Passage existant', 'replace',
        )
    service.apply_synopsis_answer(
        run_id, session, 0, 'Révision', 'Passage existant\n\nNouvelle piste', 'replace',
    )
    assert db.one(
        "SELECT answer FROM synopsis_answers WHERE project_id=? AND step_key='opening_situation'",
        (project_id,),
    )[0] == 'Révision'


def test_invalid_application_and_failure_leave_the_passage_intact(context, monkeypatch):
    db, service, session, project_id, run_id = context
    for draft, mode in [(' ', 'append'), ('Piste', 'invalid')]:
        with pytest.raises(ValueError):
            service.apply_synopsis_answer(run_id, session, 0, draft, '', mode)
    with pytest.raises(ValueError):
        service.apply_synopsis_answer(
            run_id, GUIDE_SESSIONS['build_character'], 0, 'Piste', '', 'append',
        )

    def fail(*args):
        raise RuntimeError('Échec simulé')

    monkeypatch.setattr(db, 'save_guided_application', fail)
    with pytest.raises(RuntimeError):
        service.apply_synopsis_answer(run_id, session, 0, 'Piste', '', 'append')
    assert not db.q(
        "SELECT * FROM synopsis_answers WHERE project_id=? AND step_key='opening_situation'",
        (project_id,),
    )
    assert not db.q('SELECT * FROM guided_answers')


def test_export_import_keeps_passages_and_guide_progress(context, tmp_path):
    db, service, session, project_id, run_id = context
    service.apply_synopsis_answer(run_id, session, 0, 'Situation retenue', '')
    service.skip_step(run_id, session, 1)
    path = tmp_path / 'project.storyforge.json'
    db.export_project(project_id, path)
    imported_project = db.import_project(path)
    imported_run = db.one(
        "SELECT * FROM guided_runs WHERE project_id=? AND guide_key='build_synopsis'",
        (imported_project,),
    )
    assert db.one(
        "SELECT answer FROM synopsis_answers WHERE project_id=? AND step_key='opening_situation'",
        (imported_project,),
    )[0] == 'Situation retenue'
    assert db.one(
        "SELECT status FROM guided_answers WHERE run_id=? AND step_key='disruption_direction'",
        (imported_run['id'],),
    )[0] == 'skipped'
    application = db.guided_application(imported_run['id'], 'opening_situation')
    assert (application['target_type'], application['target_id']) == ('project', 0)


def test_ui_preview_cancel_confirm_and_open_matching_passage(tmp_path):
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / 'ui.db')
    project_id, run_id = setup_project(window.db)
    window.active_project = project_id
    window.db.set_setting('active_project', project_id)
    window.resize(1280, 800)
    window.show()
    window.show_learning(run_id=run_id)
    app.processEvents()
    assert window.findChild(QScrollArea, 'SynopsisGuideScroll')
    window.learning_draft.setPlainText('Mina répare des vélos.')
    errors = []

    def interact(confirm=False):
        dialog = app.activeModalWidget()
        try:
            assert isinstance(dialog, QDialog)
            assert dialog.objectName() == 'SynopsisGuidePreview'
            assert dialog.findChild(QComboBox, 'SynopsisGuideApplyMode').currentData() == 'append'
            assert 'Mina répare' in dialog.findChild(QTextEdit).toPlainText()
            if confirm:
                next(
                    button for button in dialog.findChildren(QPushButton)
                    if button.text() == 'Confirmer le passage'
                ).click()
            else:
                dialog.reject()
        except Exception as exc:
            errors.append(exc)
            if dialog:
                dialog.reject()

    QTimer.singleShot(0, interact)
    window._preview_synopsis_answer()
    assert not errors
    assert not window.db.q('SELECT * FROM synopsis_answers')
    QTimer.singleShot(0, lambda: interact(True))
    window._preview_synopsis_answer()
    assert not errors
    assert window.db.one(
        "SELECT answer FROM synopsis_answers WHERE project_id=? AND step_key='opening_situation'",
        (project_id,),
    )[0] == 'Mina répare des vélos.'

    window._learning_step(3)
    window.learning_draft.setPlainText('Les options diminuent.')
    window._open_learning_tool()
    app.processEvents()
    assert window.current_view == 'development'
    assert window.development_doc_type == 'synopsis'
    assert window.synopsis_mode == 'guide'
    assert window.synopsis_step_index == 3
    assert isinstance(window.synopsis_answer_text, QTextEdit)
    window._return_to_learning()
    assert window._learning_idx == 3
    window.close()
    app.processEvents()
