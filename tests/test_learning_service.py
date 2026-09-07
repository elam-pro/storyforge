from pathlib import Path

import pytest

from db import Database
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
