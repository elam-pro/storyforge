import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QComboBox, QDialog, QPushButton, QScrollArea, QTextEdit

from storyforge.app import GUIDE_ORDER, GUIDE_SESSIONS, LEARNING_TOOL_LINKS, StoryForgeWindow
from storyforge.db import Database, NOW
from storyforge.learning_service import CONFLICT_GUIDE_FIELDS, LearningService


def setup_project(db):
    pid = db.run('INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)',
                 (NOW(), 'Projet fictif', 'Idée')).lastrowid
    cid = db.run('INSERT INTO conflicts(project_id,title,created_at,updated_at) VALUES(?,?,?,?)',
                 (pid, 'L’atelier et le repos', NOW(), NOW())).lastrowid
    run = db.create_guided_run('build_conflict', 'Explorer le désaccord', project_id=pid)
    return pid, cid, run


@pytest.fixture
def context(tmp_path):
    db = Database(tmp_path / 'conflict-guide.db')
    pid, cid, run = setup_project(db)
    yield db, LearningService(db), GUIDE_SESSIONS['build_conflict'], pid, cid, run
    db.conn.close()


def test_content_and_all_target_fields(context):
    db, service, session, _, cid, run = context
    assert 'build_conflict' in GUIDE_ORDER
    assert len(session.steps) == 7
    for index, step in enumerate(session.steps):
        assert step.optional and step.review and step.example and step.tips
        field, _ = CONFLICT_GUIDE_FIELDS[step.key]
        assert LEARNING_TOOL_LINKS['build_conflict'][step.key][4] == field
        service.apply_field_answer(run, session, index, f'Essai {index}', cid, '')
        row = db.one('SELECT * FROM conflicts WHERE id=?', (cid,))
        assert row[field] == f'Essai {index}'
        assert row['title'] == 'L’atelier et le repos'
        application = db.guided_application(run, step.key)
        assert application['target_type'] == 'conflict'
        assert application['target_id'] == cid
        assert application['status'] == 'en pratique'


def test_confirmation_scope_and_stale_preview(context):
    db, service, session, _, cid, run = context
    db.run('UPDATE conflicts SET side_a_goal=? WHERE id=?', ('Original', cid))
    service.apply_field_answer(run, session, 0, 'Piste', cid, 'Original')
    assert db.one('SELECT side_a_goal FROM conflicts WHERE id=?', (cid,))[0] == 'Original\n\nPiste'
    with pytest.raises(ValueError, match='changé'):
        service.apply_field_answer(run, session, 0, 'Révision', cid, 'Original', 'replace')
    service.apply_field_answer(run, session, 0, 'Révision', cid, 'Original\n\nPiste', 'replace')
    assert db.one('SELECT side_a_goal FROM conflicts WHERE id=?', (cid,))[0] == 'Révision'
    _, other, _ = setup_project(db)
    with pytest.raises(ValueError, match='ce projet'):
        service.apply_field_answer(run, session, 0, 'Interdit', other, '')
    with pytest.raises(ValueError):
        service.apply_field_answer(run, GUIDE_SESSIONS['build_character'], 0, 'Interdit', cid, '')
    for draft, mode in [('  ', 'append'), ('Texte', 'invalid')]:
        with pytest.raises(ValueError):
            service.apply_field_answer(run, session, 0, draft, cid, 'Révision', mode)
    db.run('DELETE FROM conflicts WHERE id=?', (cid,))
    with pytest.raises(ValueError):
        service.apply_field_answer(run, session, 0, 'Interdit', cid, 'Révision')


def test_field_and_evidence_roll_back_together(context, monkeypatch):
    db, service, session, _, cid, run = context
    def fail(*args):
        raise RuntimeError('Échec simulé')
    monkeypatch.setattr(db, 'save_guided_application', fail)
    with pytest.raises(RuntimeError):
        service.apply_field_answer(run, session, 0, 'Essai', cid, '')
    assert not db.one('SELECT side_a_goal FROM conflicts WHERE id=?', (cid,))[0]
    assert not db.q('SELECT * FROM guided_answers')


def test_skip_resume_export_and_remapped_target(context, tmp_path):
    db, service, session, pid, cid, run = context
    service.apply_field_answer(run, session, 0, 'Terminer la commande', cid, '')
    service.complete_step(run, session, 0, 'Terminer la commande')
    for index in range(1, 7):
        assert service.skip_step(run, session, index) == (index == 6)
    assert db.guided_run(run)['status'] == 'completed'
    assert not db.q("SELECT * FROM concept_mastery WHERE status='acquis'")
    path = tmp_path / 'project.json'
    db.export_project(pid, path)
    imported = db.import_project(path)
    imported_run = db.one('SELECT * FROM guided_runs WHERE project_id=?', (imported,))
    imported_target = db.one('SELECT * FROM conflicts WHERE project_id=?', (imported,))
    assert imported_target['side_a_goal'] == 'Terminer la commande'
    assert db.guided_application(imported_run['id'], 'first_will')['target_id'] == imported_target['id']
    assert db.one('SELECT status FROM guided_answers WHERE run_id=? AND step_key=?',
                  (imported_run['id'], 'outcome'))[0] == 'skipped'
    service.move(imported_run['id'], session, 1)
    service.complete_step(imported_run['id'], session, 1, 'Dormir')
    assert db.one('SELECT answer FROM guided_answers WHERE run_id=? AND step_key=?',
                  (run, 'opposing_force'))[0] == ''


def test_ui_preview_and_navigation(tmp_path):
    app = QApplication.instance() or QApplication([])
    w = StoryForgeWindow(tmp_path / 'ui.db')
    pid, cid, run = setup_project(w.db)
    w.active_project = pid
    w.resize(1280, 800)
    w.show()
    w.show_learning(run_id=run)
    app.processEvents()
    assert w.findChild(QScrollArea, 'ConflictGuideScroll')
    w.learning_draft.setPlainText('Terminer la commande')
    w.learning_target_combo.setCurrentIndex(w.learning_target_combo.findData(cid))
    errors = []
    def interact(confirm=False):
        dialog = app.activeModalWidget()
        try:
            assert isinstance(dialog, QDialog) and dialog.objectName() == 'ConflictGuidePreview'
            mode = dialog.findChild(QComboBox, 'ConflictGuideApplyMode')
            assert mode.currentData() == 'append'
            assert 'Terminer la commande' in dialog.findChild(QTextEdit).toPlainText()
            if confirm:
                next(b for b in dialog.findChildren(QPushButton) if b.text() == 'Confirmer l’application').click()
            else:
                dialog.reject()
        except Exception as exc:
            errors.append(exc)
            if dialog:
                dialog.reject()
    QTimer.singleShot(0, interact)
    w._preview_field_answer()
    assert not errors
    assert not w.db.one('SELECT side_a_goal FROM conflicts WHERE id=?', (cid,))[0]
    QTimer.singleShot(0, lambda: interact(True))
    w._preview_field_answer()
    assert not errors
    for index, tab in [(4, 2), (2, 0)]:
        w._learning_step(index)
        assert w.learning_target_combo.currentData() == cid
        w._open_learning_tool()
        app.processEvents()
        assert w.current_view == 'conflicts'
        assert w.conflict_tabs.currentIndex() == tab
        w._return_to_learning()
        assert w._learning_idx == index
    w.close()
    app.processEvents()
