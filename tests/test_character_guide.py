from pathlib import Path

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QComboBox, QDialog, QPushButton, QScrollArea

from app import GUIDE_SESSIONS, GUIDE_ORDER, LEARNING_TOOL_LINKS, StoryForgeWindow
from db import Database, NOW
from learning_service import CHARACTER_GUIDE_FIELDS, LearningService


def setup_project(db):
    pid = db.run('INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)',
                 (NOW(), 'Guide test', 'Idée')).lastrowid
    cid = db.run('INSERT INTO characters(project_id,name,role,created_at,updated_at) VALUES(?,?,?,?,?)',
                 (pid, 'Mina', 'Alliée', NOW(), NOW())).lastrowid
    run = db.create_guided_run('build_character', 'Mina', project_id=pid)
    return pid, cid, run


@pytest.fixture
def context(tmp_path):
    db = Database(tmp_path / 'guide.db')
    pid, cid, run = setup_project(db)
    yield db, LearningService(db), GUIDE_SESSIONS['build_character'], pid, cid, run
    db.conn.close()


def test_content_and_existing_field_targets(context):
    db, _, session, _, _, _ = context
    assert 'build_character' in GUIDE_ORDER
    assert len(session.steps) == 6
    columns = {row['name'] for row in db.q('PRAGMA table_info(characters)')}
    for step in session.steps:
        assert step.optional and step.review and step.example and step.tips
        field, _ = CHARACTER_GUIDE_FIELDS[step.key]
        assert field in columns
        assert LEARNING_TOOL_LINKS['build_character'][step.key][4] == field


def test_apply_is_scoped_and_preserves_existing_text(context):
    db, service, session, pid, cid, run = context
    db.run('UPDATE characters SET start_situation=? WHERE id=?', ('Texte original', cid))
    service.apply_character_answer(run, session, 0, 'Nouvelle piste', cid, 'Texte original')
    assert db.one('SELECT start_situation FROM characters WHERE id=?', (cid,))[0] == 'Texte original\n\nNouvelle piste'
    application = db.guided_application(run, 'situation')
    assert (application['project_id'], application['target_id']) == (pid, cid)
    assert application['status'] == 'en pratique'
    with pytest.raises(ValueError, match='changé'):
        service.apply_character_answer(run, session, 0, 'Remplacement', cid, 'Texte original', 'replace')
    current = 'Texte original\n\nNouvelle piste'
    service.apply_character_answer(run, session, 0, 'Version retenue', cid, current, 'replace')
    assert db.one('SELECT start_situation FROM characters WHERE id=?', (cid,))[0] == 'Version retenue'
    _, other, _ = setup_project(db)
    with pytest.raises(ValueError, match='ce projet'):
        service.apply_character_answer(run, session, 0, 'Interdit', other, '')
    with pytest.raises(ValueError):
        service.apply_character_answer(run, session, 0, ' ', cid, 'Version retenue')


def test_application_rolls_back_character_and_evidence(context, monkeypatch):
    db, service, session, _, cid, run = context
    def fail(*args):
        raise RuntimeError('failure')
    monkeypatch.setattr(db, 'save_guided_application', fail)
    with pytest.raises(RuntimeError):
        service.apply_character_answer(run, session, 0, 'Essai', cid, '')
    assert not db.one('SELECT start_situation FROM characters WHERE id=?', (cid,))[0]
    assert not db.q('SELECT * FROM guided_answers')


def test_optional_steps_resume_without_implying_mastery(context):
    db, service, session, _, _, run = context
    for index in range(6):
        assert service.skip_step(run, session, index, 'Piste' if index == 0 else '') == (index == 5)
    assert db.guided_run(run)['status'] == 'completed'
    assert all(row['status'] == 'skipped' for row in db.q('SELECT * FROM guided_answers'))
    service.save_answer(run, session, 5, '')  # UI autosave must preserve the skip marker.
    assert db.one('SELECT status FROM guided_answers WHERE step_index=5')[0] == 'skipped'
    assert not db.q("SELECT * FROM concept_mastery WHERE status='acquis'")
    service.move(run, session, 0)
    service.complete_step(run, session, 0, 'Version précisée')
    assert db.one('SELECT status FROM guided_answers WHERE step_index=0')[0] == 'complete'


def test_ui_preview_cancel_confirm_and_target_reuse(tmp_path):
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / 'ui.db')
    pid, cid, run = setup_project(window.db)
    window.active_project = pid
    window.resize(1280, 800)
    window.show()
    window.show_learning(run_id=run)
    app.processEvents()
    scroll = window.findChild(QScrollArea, 'CharacterGuideScroll')
    assert scroll is not None
    assert scroll.widget().height() >= scroll.widget().minimumSizeHint().height()
    window.learning_draft.setPlainText('Répare des vélos.')
    window.learning_target_combo.setCurrentIndex(window.learning_target_combo.findData(cid))
    errors = []
    def interact(confirm=False):
        dialog = app.activeModalWidget()
        try:
            assert isinstance(dialog, QDialog)
            assert dialog.objectName() == 'CharacterGuidePreview'
            assert dialog.findChild(QComboBox, 'CharacterGuideApplyMode').currentData() == 'append'
            if confirm:
                next(b for b in dialog.findChildren(QPushButton) if b.text() == 'Confirmer l’application').click()
            else:
                dialog.reject()
        except Exception as exc:
            errors.append(exc)
            if dialog:
                dialog.reject()
    QTimer.singleShot(0, interact)
    window._preview_character_answer()
    assert not errors
    assert not window.db.one('SELECT start_situation FROM characters WHERE id=?', (cid,))[0]
    QTimer.singleShot(0, lambda: interact(True))
    window._preview_character_answer()
    assert not errors
    assert window.db.one('SELECT start_situation FROM characters WHERE id=?', (cid,))[0] == 'Répare des vélos.'
    window._learning_step(1)
    assert window.learning_target_combo.currentData() == cid
    window._open_learning_tool()
    app.processEvents()
    assert window.current_view == 'characters'
    assert window.character_tabs.currentIndex() == 1
    window._return_to_learning()
    assert window._learning_idx == 1
    window.close()
    app.processEvents()


def test_export_import_preserves_guide_and_remaps_character(context, tmp_path):
    db, service, session, pid, cid, run = context
    service.apply_character_answer(run, session, 0, 'Situation retenue', cid, '')
    service.skip_step(run, session, 1)
    exported = tmp_path / 'guide.storyforge.json'
    db.export_project(pid, exported)
    imported_pid = db.import_project(exported)
    imported_run = db.one('SELECT * FROM guided_runs WHERE project_id=?', (imported_pid,))
    imported_character = db.one('SELECT * FROM characters WHERE project_id=?', (imported_pid,))
    assert imported_run['guide_key'] == 'build_character'
    assert imported_character['start_situation'] == 'Situation retenue'
    assert db.guided_application(imported_run['id'], 'situation')['target_id'] == imported_character['id']
    assert db.one('SELECT status FROM guided_answers WHERE run_id=? AND step_key=?',
                  (imported_run['id'], 'objective'))[0] == 'skipped'
