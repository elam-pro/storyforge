"""Learning persistence and progression, independent from Qt widgets.

Keep existing mastery semantics and legacy mirrors during this extraction.
Application target selection and navigation remain in the UI.
"""
from db import NOW, Database
from learning_content import LearningSession

CHARACTER_GUIDE_FIELDS = {
    'situation': ('start_situation', 'Situation initiale'),
    'objective': ('objective', 'Objectif'),
    'motivation': ('desire', 'Désir et motivation'),
    'contradiction': ('contradictions', 'Contradictions'),
    'test': ('notes', 'Notes · idée de scène'),
    'evolution': ('arc', 'Arc et transformation'),
}


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
            inferred = requested or (saved['status'] if saved['status'] in {'complete', 'skipped'} else 'draft')
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

    def apply_to_tool(self, run_id, session, index, draft, target_type, target_id, target_field):
        """Record evidence and return context together, before UI navigation."""
        with self.db.transaction():
            run, step = self._step(run_id, session, index)
            if not run['project_id']:
                raise ValueError('Un projet est nécessaire pour appliquer cette notion')
            self.save_answer(run_id, session, index, draft)
            evidence = draft.strip()
            project_id = int(run['project_id'])
            self.db.save_guided_application(run_id, step.key, project_id, target_type,
                                           target_id, target_field, 'en pratique', evidence)
            self.db.set_concept_mastery(step.concept_key, step.concept_label, 'en pratique', evidence)
            self.db.set_setting('learning_return_run', str(run_id))
            self.db.set_setting('learning_return_step', str(index))
            self.db.set_setting('active_project', str(project_id))
            return project_id

    def set_mastery(self, run_id, session, index, draft, status):
        with self.db.transaction():
            run, step = self._step(run_id, session, index)
            application = self.db.guided_application(run_id, step.key)
            if status == 'acquis' and not application:
                raise ValueError('Ouvre d’abord l’outil du projet et confronte ta réponse au travail réel.')
            self.save_answer(run_id, session, index, draft)
            evidence = draft.strip()
            self.db.set_concept_mastery(step.concept_key, step.concept_label, status, evidence)
            if application:
                self.db.save_guided_application(run_id, step.key, int(application['project_id']),
                                               application['target_type'], int(application['target_id'] or 0),
                                               application['target_field'], status, evidence)

    def apply_character_answer(self, run_id, session, index, draft, character_id,
                               expected_text, mode='append'):
        """Apply an explicitly previewed answer, scoped to this run's project."""
        with self.db.transaction():
            run, step = self._step(run_id, session, index)
            if (run['guide_key'] != 'build_character' or session.key != 'build_character'
                    or step.key not in CHARACTER_GUIDE_FIELDS):
                raise ValueError('Cette application est réservée au guide Personnage.')
            if not draft.strip() or mode not in {'append', 'replace'}:
                raise ValueError('Une réponse et un mode d’application valides sont nécessaires.')
            field, _label = CHARACTER_GUIDE_FIELDS[step.key]
            character = self.db.one('SELECT * FROM characters WHERE id=? AND project_id=?',
                                    (character_id, run['project_id']))
            if not character:
                raise ValueError('Choisis un personnage de ce projet.')
            current = character[field] or ''
            if current != expected_text:
                raise ValueError('La fiche a changé. Rouvre l’aperçu avant de confirmer.')
            proposed = draft.strip()
            if mode == 'append' and current.strip():
                proposed = current + '\n\n' + proposed
            self.db.run(f'UPDATE characters SET {field}=?,updated_at=? WHERE id=? AND project_id=?',
                        (proposed, NOW(), character_id, run['project_id']))
            self.apply_to_tool(run_id, session, index, draft, 'character', character_id, field)

    def skip_step(self, run_id, session, index, draft=''):
        with self.db.transaction():
            _run, step = self._step(run_id, session, index)
            if not step.optional:
                raise ValueError('Cette étape demande une réponse.')
            self.save_answer(run_id, session, index, draft, 'skipped')
            finish = index == len(session.steps) - 1
            target = index if finish else index + 1
            self.db.update_guided_run(run_id, current_step=target,
                                      status='completed' if finish else 'ongoing')
            self.mirror_progress(run_id, target, 'terminée' if finish else 'en cours')
            return finish

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
