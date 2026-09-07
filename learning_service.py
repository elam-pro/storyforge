"""Learning persistence and progression, independent from Qt widgets.

Keep existing mastery semantics and legacy mirrors during this extraction.
Application target selection and navigation remain in the UI for now.
"""
from db import NOW, Database
from learning_content import LearningSession


class LearningService:
    def __init__(self, db: Database):
        self.db = db

    def _step(self, run_id, session, index):
        run = self.db.guided_run(run_id)
        if not run or not 0 <= index < len(session.steps):
            raise ValueError('Parcours ou étape introuvable')
        return run, session.steps[index]

    def save_answer(self, run_id: int, session: LearningSession, index: int,
                    draft: str, status: str | None = None):
        with self.db.transaction():
            run, step = self._step(run_id, session, index)
            draft = draft.strip()
            saved = self.db.ensure_guided_answer(run_id, step.key, index)
            requested = {'terminé': 'complete', 'brouillon': 'draft'}.get(status or '', status)
            inferred = requested or ('complete' if saved['status'] == 'complete' else 'draft')
            self.db.save_guided_answer(run_id, step.key, index, draft, inferred)
            mastery = self.db.one('SELECT status,evidence FROM concept_mastery WHERE concept_key=?', (step.concept_key,))
            state = ('acquis' if mastery and mastery['status'] == 'acquis' and mastery['evidence'] == draft
                     else 'en pratique' if draft else 'découverte')
            self.db.set_concept_mastery(step.concept_key, step.concept_label, state, draft)
            if run['legacy_session_key']:
                legacy = self.db.ensure_learning_work(run['legacy_session_key'], index, step.concept_key)
                self.db.save_learning_work(run['legacy_session_key'], index, step.concept_key,
                                          draft, legacy['feedback'], legacy['revision'], legacy['takeaway'],
                                          legacy['mastery'], 'terminé' if inferred == 'complete' else 'brouillon')

    def mirror_progress(self, run_id, index, status):
        run = self.db.guided_run(run_id)
        if run and run['legacy_session_key']:
            self.db.run('''INSERT INTO progress(session_key,step_index,status,updated_at)
                VALUES(?,?,?,?) ON CONFLICT(session_key) DO UPDATE SET
                step_index=excluded.step_index,status=excluded.status,updated_at=excluded.updated_at''',
                        (run['legacy_session_key'], index, status, NOW()))

    def move(self, run_id, session, index):
        self._step(run_id, session, index)
        with self.db.transaction():
            self.db.update_guided_run(run_id, current_step=index, status='ongoing')
            self.mirror_progress(run_id, index, 'en cours')

    def mark_incomplete(self, run_id, session, index, draft):
        with self.db.transaction():
            self.save_answer(run_id, session, index, draft, 'draft')
            self.move(run_id, session, index)

    def complete_step(self, run_id, session, index, draft) -> bool:
        if not draft.strip():
            raise ValueError('Une réponse est nécessaire pour terminer une étape')
        with self.db.transaction():
            self.save_answer(run_id, session, index, draft, 'complete')
            finish = index == len(session.steps) - 1
            target = index if finish else index + 1
            self.db.update_guided_run(run_id, current_step=target, status='completed' if finish else 'ongoing')
            self.mirror_progress(run_id, target, 'terminée' if finish else 'en cours')
            return finish
