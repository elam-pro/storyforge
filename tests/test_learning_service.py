from pathlib import Path

import pytest

from db import Database, NOW
from learning_content import load_session
from learning_service import LearningService


@pytest.fixture
def learning(tmp_path):
    db = Database(tmp_path / 'learning.db')
    session = load_session(Path(__file__).resolve().parents[1] / 'content/sessions/session_01.json')
    run = db.create_guided_run('seed', 'Test', legacy_session_key=session.key)
    yield db, LearningService(db), session, run
    db.conn.close()


def test_save_preserves_legacy_feedback_and_mastery_semantics(learning):
    db, service, session, run = learning
    step = session.steps[0]
    service.save_answer(run, session, 0, ' Essai ', 'terminé')
    db.run('UPDATE learning_work SET feedback=?,revision=?,takeaway=?', ('Retour', 'Révision', 'Leçon'))
    db.set_concept_mastery(step.concept_key, step.concept_label, 'acquis', 'Essai')
    service.save_answer(run, session, 0, 'Essai')
    assert db.one('SELECT status FROM concept_mastery')[0] == 'acquis'
    assert db.one('SELECT status FROM guided_answers')[0] == 'complete'
    service.save_answer(run, session, 0, 'Autre essai')
    assert db.one('SELECT status FROM concept_mastery')[0] == 'en pratique'
    row = db.one('SELECT * FROM learning_work')
    assert (row['feedback'], row['revision'], row['takeaway']) == ('Retour', 'Révision', 'Leçon')


def test_completion_and_reopening(learning):
    db, service, session, run = learning
    assert not service.complete_step(run, session, 0, 'Premier essai')
    assert db.guided_run(run)['current_step'] == 1
    last = len(session.steps) - 1
    assert service.complete_step(run, session, last, 'Conclusion')
    assert db.guided_run(run)['status'] == 'completed'
    assert db.one('SELECT status FROM progress')[0] == 'terminée'
    service.mark_incomplete(run, session, last, 'À revoir')
    assert db.guided_run(run)['status'] == 'ongoing'
    assert db.one('SELECT status FROM progress')[0] == 'en cours'
    assert db.one('SELECT status FROM guided_answers WHERE step_index=?', (last,))[0] == 'draft'


def test_failure_rolls_back_answer_mastery_and_progress(learning, monkeypatch):
    db, service, session, run = learning
    def fail(*args, **kwargs):
        raise RuntimeError('Simulated failure')
    monkeypatch.setattr(db, 'update_guided_run', fail)
    with pytest.raises(RuntimeError):
        service.complete_step(run, session, 0, 'Essai')
    for table in ('guided_answers', 'learning_work', 'concept_mastery', 'progress'):
        assert db.one(f'SELECT COUNT(*) FROM {table}')[0] == 0
    assert db.guided_run(run)['current_step'] == 0


def test_empty_answer_and_invalid_step_do_not_write(learning):
    db, service, session, run = learning
    with pytest.raises(ValueError):
        service.complete_step(run, session, 0, '  ')
    with pytest.raises(ValueError):
        service.move(run, session, -1)
    assert db.one('SELECT COUNT(*) FROM guided_answers')[0] == 0


def test_two_runs_keep_answers_separate(learning):
    db, service, session, first = learning
    second = db.create_guided_run('seed', 'Second')
    service.save_answer(first, session, 0, 'Premier')
    service.save_answer(second, session, 0, 'Second')
    assert db.one('SELECT answer FROM guided_answers WHERE run_id=?', (first,))[0] == 'Premier'
    assert db.one('SELECT answer FROM guided_answers WHERE run_id=?', (second,))[0] == 'Second'
    assert db.one('SELECT draft FROM learning_work')[0] == 'Premier'


def attach_project(db, run):
    pid = db.run('INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)', (NOW(), 'Projet', 'Idée')).lastrowid
    db.update_guided_run(run, project_id=pid)
    return pid


def test_application_and_explicit_mastery(learning):
    db, service, session, run = learning
    pid = attach_project(db, run)
    assert service.apply_to_tool(run, session, 0, ' Preuve ', 'project', 0, 'desire') == pid
    application = db.guided_application(run, session.steps[0].key)
    assert application['evidence'] == 'Preuve'
    assert application['status'] == 'en pratique'
    assert db.setting('learning_return_run') == str(run)
    assert db.setting('learning_return_step') == '0'
    assert db.setting('active_project') == str(pid)
    assert [(row['event_kind'], row['status']) for row in db.guided_application_history(
        run, session.steps[0].key
    )] == [('applied', 'en pratique')]
    service.set_mastery(run, session, 0, 'Preuve affinée', 'acquis')
    application = db.guided_application(run, session.steps[0].key)
    assert application['status'] == 'acquis'
    assert application['evidence'] == 'Preuve affinée'
    assert application['target_field'] == 'desire'
    assert db.one('SELECT status FROM concept_mastery')[0] == 'acquis'
    service.set_mastery(run, session, 0, 'Preuve affinée', 'à revoir')
    assert db.guided_application(run, session.steps[0].key)['status'] == 'à revoir'
    assert [(row['event_kind'], row['status']) for row in db.guided_application_history(
        run, session.steps[0].key
    )] == [
        ('applied', 'en pratique'),
        ('mastery', 'acquis'),
        ('mastery', 'à revoir'),
    ]


def test_reapplying_a_step_keeps_each_contextual_trace(learning):
    db, service, session, run = learning
    attach_project(db, run)
    service.apply_to_tool(run, session, 0, 'Première confrontation', 'character', 12, 'desire')
    service.apply_to_tool(run, session, 0, 'Deuxième confrontation', 'scene', 34, 'objective')

    current = db.guided_application(run, session.steps[0].key)
    history = db.guided_application_history(run, session.steps[0].key)
    assert (current['target_type'], current['target_id']) == ('scene', 34)
    assert [(row['target_type'], row['target_id'], row['evidence']) for row in history] == [
        ('character', 12, 'Première confrontation'),
        ('scene', 34, 'Deuxième confrontation'),
    ]


def test_mastery_requires_application_and_application_requires_project(learning):
    db, service, session, run = learning
    with pytest.raises(ValueError):
        service.set_mastery(run, session, 0, 'Essai', 'acquis')
    with pytest.raises(ValueError):
        service.apply_to_tool(run, session, 0, 'Essai', 'project', 0, '')
    assert db.one('SELECT COUNT(*) FROM guided_answers')[0] == 0


def test_application_failure_rolls_back_context_and_evidence(learning, monkeypatch):
    db, service, session, run = learning
    attach_project(db, run)
    original = db.set_setting
    def fail(key, value):
        if key == 'active_project':
            raise RuntimeError('failure')
        original(key, value)
    monkeypatch.setattr(db, 'set_setting', fail)
    with pytest.raises(RuntimeError):
        service.apply_to_tool(run, session, 0, 'Essai', 'project', 0, '')
    assert db.guided_application(run, session.steps[0].key) is None
    assert db.setting('learning_return_run', 'missing') == 'missing'
    assert db.one('SELECT COUNT(*) FROM guided_answers')[0] == 0


def test_mastery_failure_preserves_previous_evidence(learning, monkeypatch):
    db, service, session, run = learning
    attach_project(db, run)
    service.apply_to_tool(run, session, 0, 'Avant', 'project', 0, '')
    def fail(*args, **kwargs):
        raise RuntimeError('failure')
    monkeypatch.setattr(db, 'save_guided_application', fail)
    with pytest.raises(RuntimeError):
        service.set_mastery(run, session, 0, 'Après', 'acquis')
    assert db.one('SELECT answer FROM guided_answers')[0] == 'Avant'
    assert db.one('SELECT status FROM concept_mastery')[0] == 'en pratique'
