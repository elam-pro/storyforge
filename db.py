from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

NOW = lambda: datetime.now().isoformat(timespec="seconds")  # noqa: DTZ005 - local desktop timestamps

class Database:
    def __init__(self, path: Path):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._transaction_depth = 0
        self.conn.execute("PRAGMA foreign_keys=ON")
        # Back up an existing schema before additive migrations. One restorable
        # copy is enough when an older database needs several additions at once.
        migration_labels = []
        columns = {row[1] for row in self.conn.execute('PRAGMA table_info(doc_versions)')}
        if columns and 'snapshot_json' not in columns:
            migration_labels.append('structured_versions')
        tables = {
            row[0] for row in self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if (
            tables
            and 'guided_applications' in tables
            and 'guided_application_history' not in tables
        ):
            migration_labels.append('connected_learning_history')
        if migration_labels:
            backup_dir = Path(path).parent / 'backups'
            backup_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            label = '_'.join(migration_labels)
            backup_path = backup_dir / f'{Path(path).stem}_before_{label}_{stamp}.db'
            destination = sqlite3.connect(backup_path)
            try:
                self.conn.backup(destination)
            finally:
                destination.close()
        self._init()

    def _init(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS ideas(
            id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, title TEXT NOT NULL,
            seed TEXT NOT NULL DEFAULT '', attraction TEXT NOT NULL DEFAULT '', potential TEXT NOT NULL DEFAULT 'inconnu',
            status TEXT NOT NULL DEFAULT 'brute', idea_type TEXT NOT NULL DEFAULT 'unclassified',
            what_if TEXT NOT NULL DEFAULT '',
            attachment_name TEXT NOT NULL DEFAULT '', attachment_mime TEXT NOT NULL DEFAULT '',
            attachment_data BLOB);
        CREATE TABLE IF NOT EXISTS projects(
            id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, title TEXT NOT NULL,
            stage TEXT NOT NULL DEFAULT 'Idée', protagonist TEXT NOT NULL DEFAULT '', desire TEXT NOT NULL DEFAULT '',
            objective TEXT NOT NULL DEFAULT '', opposition TEXT NOT NULL DEFAULT '', stakes TEXT NOT NULL DEFAULT '',
            change_note TEXT NOT NULL DEFAULT '', ending TEXT NOT NULL DEFAULT '', current_document TEXT NOT NULL DEFAULT '',
            main_problem TEXT NOT NULL DEFAULT '', next_decision TEXT NOT NULL DEFAULT '', open_questions TEXT NOT NULL DEFAULT '',
            project_type TEXT NOT NULL DEFAULT 'film', story_format TEXT NOT NULL DEFAULT 'free',
            target_duration INTEGER NOT NULL DEFAULT 0, start_mode TEXT NOT NULL DEFAULT 'free',
            project_status TEXT NOT NULL DEFAULT 'ongoing', archived INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT '');
        CREATE TABLE IF NOT EXISTS project_docs(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL, doc_type TEXT NOT NULL,
            title TEXT NOT NULL, content TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL,
            UNIQUE(project_id, doc_type), FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS doc_versions(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL, doc_type TEXT NOT NULL,
            label TEXT NOT NULL, content TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS learning_answers(
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_key TEXT NOT NULL, step_index INTEGER NOT NULL,
            answer TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL, UNIQUE(session_key, step_index));
        CREATE TABLE IF NOT EXISTS progress(
            session_key TEXT PRIMARY KEY, step_index INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'en cours', updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS learning_work(
            session_key TEXT NOT NULL, step_index INTEGER NOT NULL, concept_key TEXT NOT NULL,
            draft TEXT NOT NULL DEFAULT '', feedback TEXT NOT NULL DEFAULT '', revision TEXT NOT NULL DEFAULT '',
            takeaway TEXT NOT NULL DEFAULT '', mastery TEXT NOT NULL DEFAULT 'à revoir',
            status TEXT NOT NULL DEFAULT 'brouillon', updated_at TEXT NOT NULL,
            PRIMARY KEY(session_key, step_index));
        CREATE TABLE IF NOT EXISTS guided_runs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guide_key TEXT NOT NULL, title TEXT NOT NULL DEFAULT '',
            project_id INTEGER, idea_id INTEGER,
            assistance_level TEXT NOT NULL DEFAULT 'discovery',
            current_step INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'ongoing',
            legacy_session_key TEXT NOT NULL DEFAULT '',
            applied_at TEXT NOT NULL DEFAULT '',
            applied_target_id INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE SET NULL,
            FOREIGN KEY(idea_id) REFERENCES ideas(id) ON DELETE SET NULL);
        CREATE TABLE IF NOT EXISTS guided_answers(
            run_id INTEGER NOT NULL, step_key TEXT NOT NULL,
            step_index INTEGER NOT NULL DEFAULT 0,
            answer TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'draft', updated_at TEXT NOT NULL,
            PRIMARY KEY(run_id, step_key),
            FOREIGN KEY(run_id) REFERENCES guided_runs(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS concept_mastery(
            concept_key TEXT PRIMARY KEY, label TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'à revoir',
            evidence TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS guided_applications(
            run_id INTEGER NOT NULL, step_key TEXT NOT NULL,
            project_id INTEGER NOT NULL, target_type TEXT NOT NULL DEFAULT '',
            target_id INTEGER NOT NULL DEFAULT 0, target_field TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'en pratique', evidence TEXT NOT NULL DEFAULT '',
            applied_at TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL,
            PRIMARY KEY(run_id, step_key),
            FOREIGN KEY(run_id) REFERENCES guided_runs(id) ON DELETE CASCADE,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS guided_application_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL, step_key TEXT NOT NULL,
            project_id INTEGER NOT NULL, target_type TEXT NOT NULL DEFAULT '',
            target_id INTEGER NOT NULL DEFAULT 0, target_field TEXT NOT NULL DEFAULT '',
            event_kind TEXT NOT NULL DEFAULT 'applied',
            status TEXT NOT NULL DEFAULT 'en pratique', evidence TEXT NOT NULL DEFAULT '',
            occurred_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(run_id) REFERENCES guided_runs(id) ON DELETE CASCADE,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS project_questions(
            project_id INTEGER NOT NULL, question_key TEXT NOT NULL, answer TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL,
            PRIMARY KEY(project_id, question_key), FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS story_map_answers(
            project_id INTEGER NOT NULL, step_key TEXT NOT NULL, answer TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL,
            PRIMARY KEY(project_id, step_key), FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS synopsis_answers(
            project_id INTEGER NOT NULL, step_key TEXT NOT NULL, answer TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL,
            PRIMARY KEY(project_id, step_key), FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS story_map_nodes(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            title TEXT NOT NULL DEFAULT '', content TEXT NOT NULL DEFAULT '', kind TEXT NOT NULL DEFAULT 'idea',
            source_step_key TEXT NOT NULL DEFAULT '', x REAL NOT NULL DEFAULT 80, y REAL NOT NULL DEFAULT 80,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS story_map_links(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            source_id INTEGER NOT NULL, target_id INTEGER NOT NULL, label TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL,
            UNIQUE(project_id, source_id, target_id),
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY(source_id) REFERENCES story_map_nodes(id) ON DELETE CASCADE,
            FOREIGN KEY(target_id) REFERENCES story_map_nodes(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS sequence_blocks(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            position INTEGER NOT NULL DEFAULT 0, title TEXT NOT NULL DEFAULT '',
            purpose TEXT NOT NULL DEFAULT '', events TEXT NOT NULL DEFAULT '',
            consequence TEXT NOT NULL DEFAULT '', source_node_id INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS scene_rows(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            position INTEGER NOT NULL DEFAULT 0, title TEXT NOT NULL DEFAULT '',
            duration REAL NOT NULL DEFAULT 0, objective TEXT NOT NULL DEFAULT '',
            opposition TEXT NOT NULL DEFAULT '', change_note TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'idea', moment_label TEXT NOT NULL DEFAULT '',
            driver_character_id INTEGER, character_objective TEXT NOT NULL DEFAULT '',
            conflict_note TEXT NOT NULL DEFAULT '', information_revealed TEXT NOT NULL DEFAULT '',
            entry_state TEXT NOT NULL DEFAULT '', exit_state TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            source_sequence_id INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS outline_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            parent_id INTEGER, position INTEGER NOT NULL DEFAULT 0,
            item_type TEXT NOT NULL DEFAULT 'beat', title TEXT NOT NULL DEFAULT '',
            summary TEXT NOT NULL DEFAULT '', function_note TEXT NOT NULL DEFAULT '',
            consequence TEXT NOT NULL DEFAULT '', collapsed INTEGER NOT NULL DEFAULT 0,
            source_sequence_id INTEGER NOT NULL DEFAULT 0,
            source_scene_id INTEGER NOT NULL DEFAULT 0,
            source_node_id INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY(parent_id) REFERENCES outline_items(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS development_status(
            project_id INTEGER NOT NULL, doc_type TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft', updated_at TEXT NOT NULL,
            PRIMARY KEY(project_id, doc_type),
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS characters(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            name TEXT NOT NULL DEFAULT '', role TEXT NOT NULL DEFAULT '',
            gender TEXT NOT NULL DEFAULT 'unspecified',
            story_function TEXT NOT NULL DEFAULT '', desire TEXT NOT NULL DEFAULT '',
            conflict TEXT NOT NULL DEFAULT '', arc TEXT NOT NULL DEFAULT '', notes TEXT NOT NULL DEFAULT '',
            age TEXT NOT NULL DEFAULT '', occupation TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '', appearance TEXT NOT NULL DEFAULT '',
            personality TEXT NOT NULL DEFAULT '', objective TEXT NOT NULL DEFAULT '',
            need TEXT NOT NULL DEFAULT '', fear TEXT NOT NULL DEFAULT '', weakness TEXT NOT NULL DEFAULT '',
            wound TEXT NOT NULL DEFAULT '', values_note TEXT NOT NULL DEFAULT '', beliefs TEXT NOT NULL DEFAULT '',
            contradictions TEXT NOT NULL DEFAULT '', secrets TEXT NOT NULL DEFAULT '', backstory TEXT NOT NULL DEFAULT '',
            start_situation TEXT NOT NULL DEFAULT '', end_situation TEXT NOT NULL DEFAULT '',
            speaking_style TEXT NOT NULL DEFAULT '', portrait_name TEXT NOT NULL DEFAULT '',
            portrait_mime TEXT NOT NULL DEFAULT '', portrait_data BLOB,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS world_profiles(
            project_id INTEGER PRIMARY KEY,
            epoch TEXT NOT NULL DEFAULT '', places TEXT NOT NULL DEFAULT '',
            society TEXT NOT NULL DEFAULT '', culture TEXT NOT NULL DEFAULT '',
            worldview TEXT NOT NULL DEFAULT '', originality TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS world_rules(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            category TEXT NOT NULL DEFAULT 'Autre', title TEXT NOT NULL DEFAULT '',
            rule_text TEXT NOT NULL DEFAULT '', scope TEXT NOT NULL DEFAULT '',
            limitation TEXT NOT NULL DEFAULT '', cost TEXT NOT NULL DEFAULT '',
            exceptions TEXT NOT NULL DEFAULT '', consequence TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'draft', created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS world_terms(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            category TEXT NOT NULL DEFAULT 'Autre', term TEXT NOT NULL DEFAULT '',
            definition TEXT NOT NULL DEFAULT '', usage TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS theme_profiles(
            project_id INTEGER PRIMARY KEY,
            theme_word TEXT NOT NULL DEFAULT '', central_question TEXT NOT NULL DEFAULT '',
            personal_interest TEXT NOT NULL DEFAULT '', avoid_message TEXT NOT NULL DEFAULT '',
            opening_view TEXT NOT NULL DEFAULT '', decisions_note TEXT NOT NULL DEFAULT '',
            consequences_note TEXT NOT NULL DEFAULT '', conflicts_note TEXT NOT NULL DEFAULT '',
            ending_response TEXT NOT NULL DEFAULT '', notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS theme_positions(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            position INTEGER NOT NULL DEFAULT 0, position_type TEXT NOT NULL DEFAULT 'nuance',
            label TEXT NOT NULL DEFAULT '', stance TEXT NOT NULL DEFAULT '', nuance TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS theme_position_characters(
            position_id INTEGER NOT NULL, character_id INTEGER NOT NULL,
            PRIMARY KEY(position_id,character_id),
            FOREIGN KEY(position_id) REFERENCES theme_positions(id) ON DELETE CASCADE,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS theme_motifs(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            position INTEGER NOT NULL DEFAULT 0, name TEXT NOT NULL DEFAULT '',
            motif_type TEXT NOT NULL DEFAULT 'Objet', meaning TEXT NOT NULL DEFAULT '',
            appearances TEXT NOT NULL DEFAULT '', evolution TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS theme_motif_locations(
            motif_id INTEGER NOT NULL, location_id INTEGER NOT NULL,
            PRIMARY KEY(motif_id,location_id),
            FOREIGN KEY(motif_id) REFERENCES theme_motifs(id) ON DELETE CASCADE,
            FOREIGN KEY(location_id) REFERENCES locations(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS theme_motif_events(
            motif_id INTEGER NOT NULL, event_id INTEGER NOT NULL,
            PRIMARY KEY(motif_id,event_id),
            FOREIGN KEY(motif_id) REFERENCES theme_motifs(id) ON DELETE CASCADE,
            FOREIGN KEY(event_id) REFERENCES timeline_events(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS theme_motif_images(
            motif_id INTEGER NOT NULL, image_id INTEGER NOT NULL,
            PRIMARY KEY(motif_id,image_id),
            FOREIGN KEY(motif_id) REFERENCES theme_motifs(id) ON DELETE CASCADE,
            FOREIGN KEY(image_id) REFERENCES image_library(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS conflicts(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            position INTEGER NOT NULL DEFAULT 0, title TEXT NOT NULL DEFAULT '',
            importance TEXT NOT NULL DEFAULT 'secondary', nature TEXT NOT NULL DEFAULT 'external',
            side_a_label TEXT NOT NULL DEFAULT '', side_a_goal TEXT NOT NULL DEFAULT '',
            side_a_strategy TEXT NOT NULL DEFAULT '', side_a_advantage TEXT NOT NULL DEFAULT '',
            side_a_vulnerability TEXT NOT NULL DEFAULT '', side_a_loss TEXT NOT NULL DEFAULT '',
            side_b_label TEXT NOT NULL DEFAULT '', side_b_goal TEXT NOT NULL DEFAULT '',
            side_b_strategy TEXT NOT NULL DEFAULT '', side_b_advantage TEXT NOT NULL DEFAULT '',
            side_b_vulnerability TEXT NOT NULL DEFAULT '', side_b_loss TEXT NOT NULL DEFAULT '',
            incompatibility TEXT NOT NULL DEFAULT '', stakes TEXT NOT NULL DEFAULT '',
            trigger_note TEXT NOT NULL DEFAULT '', first_actions TEXT NOT NULL DEFAULT '',
            escalation TEXT NOT NULL DEFAULT '', closing_options TEXT NOT NULL DEFAULT '',
            difficult_choice TEXT NOT NULL DEFAULT '', decisive_confrontation TEXT NOT NULL DEFAULT '',
            outcome TEXT NOT NULL DEFAULT '', winner TEXT NOT NULL DEFAULT '',
            loser TEXT NOT NULL DEFAULT '', cost TEXT NOT NULL DEFAULT '',
            change_note TEXT NOT NULL DEFAULT '', notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS conflict_characters(
            conflict_id INTEGER NOT NULL, character_id INTEGER NOT NULL,
            side TEXT NOT NULL DEFAULT 'affected',
            PRIMARY KEY(conflict_id,character_id,side),
            FOREIGN KEY(conflict_id) REFERENCES conflicts(id) ON DELETE CASCADE,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS conflict_groups(
            conflict_id INTEGER NOT NULL, group_id INTEGER NOT NULL,
            side TEXT NOT NULL DEFAULT 'affected',
            PRIMARY KEY(conflict_id,group_id,side),
            FOREIGN KEY(conflict_id) REFERENCES conflicts(id) ON DELETE CASCADE,
            FOREIGN KEY(group_id) REFERENCES character_groups(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS conflict_scenes(
            conflict_id INTEGER NOT NULL, scene_id INTEGER NOT NULL,
            PRIMARY KEY(conflict_id,scene_id),
            FOREIGN KEY(conflict_id) REFERENCES conflicts(id) ON DELETE CASCADE,
            FOREIGN KEY(scene_id) REFERENCES scene_rows(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS conflict_story_nodes(
            conflict_id INTEGER NOT NULL, node_id INTEGER NOT NULL,
            PRIMARY KEY(conflict_id,node_id),
            FOREIGN KEY(conflict_id) REFERENCES conflicts(id) ON DELETE CASCADE,
            FOREIGN KEY(node_id) REFERENCES story_map_nodes(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS conflict_events(
            conflict_id INTEGER NOT NULL, event_id INTEGER NOT NULL,
            PRIMARY KEY(conflict_id,event_id),
            FOREIGN KEY(conflict_id) REFERENCES conflicts(id) ON DELETE CASCADE,
            FOREIGN KEY(event_id) REFERENCES timeline_events(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS conflict_theme_positions(
            conflict_id INTEGER NOT NULL, position_id INTEGER NOT NULL,
            PRIMARY KEY(conflict_id,position_id),
            FOREIGN KEY(conflict_id) REFERENCES conflicts(id) ON DELETE CASCADE,
            FOREIGN KEY(position_id) REFERENCES theme_positions(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS character_arcs(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            character_id INTEGER NOT NULL UNIQUE,
            arc_type TEXT NOT NULL DEFAULT '', initial_belief TEXT NOT NULL DEFAULT '',
            main_trial TEXT NOT NULL DEFAULT '', pressures TEXT NOT NULL DEFAULT '',
            breaking_point TEXT NOT NULL DEFAULT '', decisive_choice TEXT NOT NULL DEFAULT '',
            cost TEXT NOT NULL DEFAULT '', visible_proof TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS character_arc_scenes(
            arc_id INTEGER NOT NULL, scene_id INTEGER NOT NULL,
            PRIMARY KEY(arc_id,scene_id),
            FOREIGN KEY(arc_id) REFERENCES character_arcs(id) ON DELETE CASCADE,
            FOREIGN KEY(scene_id) REFERENCES scene_rows(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS character_arc_story_nodes(
            arc_id INTEGER NOT NULL, node_id INTEGER NOT NULL,
            PRIMARY KEY(arc_id,node_id),
            FOREIGN KEY(arc_id) REFERENCES character_arcs(id) ON DELETE CASCADE,
            FOREIGN KEY(node_id) REFERENCES story_map_nodes(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS character_arc_events(
            arc_id INTEGER NOT NULL, event_id INTEGER NOT NULL,
            PRIMARY KEY(arc_id,event_id),
            FOREIGN KEY(arc_id) REFERENCES character_arcs(id) ON DELETE CASCADE,
            FOREIGN KEY(event_id) REFERENCES timeline_events(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS character_arc_conflicts(
            arc_id INTEGER NOT NULL, conflict_id INTEGER NOT NULL,
            PRIMARY KEY(arc_id,conflict_id),
            FOREIGN KEY(arc_id) REFERENCES character_arcs(id) ON DELETE CASCADE,
            FOREIGN KEY(conflict_id) REFERENCES conflicts(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS hook_profiles(
            project_id INTEGER PRIMARY KEY,
            hook_question TEXT NOT NULL DEFAULT '', unusual_situation TEXT NOT NULL DEFAULT '',
            audience_question TEXT NOT NULL DEFAULT '', withheld_answer TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS story_promises(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            position INTEGER NOT NULL DEFAULT 0, promise_type TEXT NOT NULL DEFAULT 'Concept',
            title TEXT NOT NULL DEFAULT '', description TEXT NOT NULL DEFAULT '',
            planted_note TEXT NOT NULL DEFAULT '', development_note TEXT NOT NULL DEFAULT '',
            payoff_note TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'À placer',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS story_promise_story_nodes(
            promise_id INTEGER NOT NULL, node_id INTEGER NOT NULL,
            PRIMARY KEY(promise_id,node_id),
            FOREIGN KEY(promise_id) REFERENCES story_promises(id) ON DELETE CASCADE,
            FOREIGN KEY(node_id) REFERENCES story_map_nodes(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS story_promise_scenes(
            promise_id INTEGER NOT NULL, scene_id INTEGER NOT NULL,
            PRIMARY KEY(promise_id,scene_id),
            FOREIGN KEY(promise_id) REFERENCES story_promises(id) ON DELETE CASCADE,
            FOREIGN KEY(scene_id) REFERENCES scene_rows(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS story_moments(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            position INTEGER NOT NULL DEFAULT 0, moment_type TEXT NOT NULL DEFAULT 'Moment fort',
            title TEXT NOT NULL DEFAULT '', description TEXT NOT NULL DEFAULT '',
            narrative_function TEXT NOT NULL DEFAULT '', placement_note TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Idée', created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS story_moment_story_nodes(
            moment_id INTEGER NOT NULL, node_id INTEGER NOT NULL,
            PRIMARY KEY(moment_id,node_id),
            FOREIGN KEY(moment_id) REFERENCES story_moments(id) ON DELETE CASCADE,
            FOREIGN KEY(node_id) REFERENCES story_map_nodes(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS story_moment_sequences(
            moment_id INTEGER NOT NULL, sequence_id INTEGER NOT NULL,
            PRIMARY KEY(moment_id,sequence_id),
            FOREIGN KEY(moment_id) REFERENCES story_moments(id) ON DELETE CASCADE,
            FOREIGN KEY(sequence_id) REFERENCES sequence_blocks(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS story_moment_scenes(
            moment_id INTEGER NOT NULL, scene_id INTEGER NOT NULL,
            PRIMARY KEY(moment_id,scene_id),
            FOREIGN KEY(moment_id) REFERENCES story_moments(id) ON DELETE CASCADE,
            FOREIGN KEY(scene_id) REFERENCES scene_rows(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS story_moment_events(
            moment_id INTEGER NOT NULL, event_id INTEGER NOT NULL,
            PRIMARY KEY(moment_id,event_id),
            FOREIGN KEY(moment_id) REFERENCES story_moments(id) ON DELETE CASCADE,
            FOREIGN KEY(event_id) REFERENCES timeline_events(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS story_moment_conflicts(
            moment_id INTEGER NOT NULL, conflict_id INTEGER NOT NULL,
            PRIMARY KEY(moment_id,conflict_id),
            FOREIGN KEY(moment_id) REFERENCES story_moments(id) ON DELETE CASCADE,
            FOREIGN KEY(conflict_id) REFERENCES conflicts(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS world_rule_characters(
            rule_id INTEGER NOT NULL, character_id INTEGER NOT NULL,
            PRIMARY KEY(rule_id,character_id),
            FOREIGN KEY(rule_id) REFERENCES world_rules(id) ON DELETE CASCADE,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS world_rule_groups(
            rule_id INTEGER NOT NULL, group_id INTEGER NOT NULL,
            PRIMARY KEY(rule_id,group_id),
            FOREIGN KEY(rule_id) REFERENCES world_rules(id) ON DELETE CASCADE,
            FOREIGN KEY(group_id) REFERENCES character_groups(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS world_rule_events(
            rule_id INTEGER NOT NULL, event_id INTEGER NOT NULL,
            PRIMARY KEY(rule_id,event_id),
            FOREIGN KEY(rule_id) REFERENCES world_rules(id) ON DELETE CASCADE,
            FOREIGN KEY(event_id) REFERENCES timeline_events(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS world_rule_images(
            rule_id INTEGER NOT NULL, image_id INTEGER NOT NULL,
            PRIMARY KEY(rule_id,image_id),
            FOREIGN KEY(rule_id) REFERENCES world_rules(id) ON DELETE CASCADE,
            FOREIGN KEY(image_id) REFERENCES image_library(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS relationship_maps(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            name TEXT NOT NULL DEFAULT 'Relations générales', map_type TEXT NOT NULL DEFAULT 'general',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            UNIQUE(project_id,name),
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS character_relationships(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            map_id INTEGER,
            character_a_id INTEGER NOT NULL, character_b_id INTEGER NOT NULL,
            relationship_type TEXT NOT NULL DEFAULT 'Autre', description TEXT NOT NULL DEFAULT '',
            tension TEXT NOT NULL DEFAULT '', secret TEXT NOT NULL DEFAULT '',
            evolution TEXT NOT NULL DEFAULT '', color TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY(map_id) REFERENCES relationship_maps(id) ON DELETE CASCADE,
            FOREIGN KEY(character_a_id) REFERENCES characters(id) ON DELETE CASCADE,
            FOREIGN KEY(character_b_id) REFERENCES characters(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS relationship_map_nodes(
            map_id INTEGER NOT NULL, character_id INTEGER NOT NULL,
            x REAL NOT NULL DEFAULT 100, y REAL NOT NULL DEFAULT 100,
            PRIMARY KEY(map_id,character_id),
            FOREIGN KEY(map_id) REFERENCES relationship_maps(id) ON DELETE CASCADE,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS character_groups(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            name TEXT NOT NULL DEFAULT '', group_type TEXT NOT NULL DEFAULT 'Groupe',
            description TEXT NOT NULL DEFAULT '', color TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS character_group_members(
            group_id INTEGER NOT NULL, character_id INTEGER NOT NULL,
            role_in_group TEXT NOT NULL DEFAULT '',
            PRIMARY KEY(group_id,character_id),
            FOREIGN KEY(group_id) REFERENCES character_groups(id) ON DELETE CASCADE,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS character_references(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL, character_id INTEGER NOT NULL,
            title TEXT NOT NULL DEFAULT '', category TEXT NOT NULL DEFAULT 'Référence',
            notes TEXT NOT NULL DEFAULT '', file_name TEXT NOT NULL DEFAULT '',
            mime_type TEXT NOT NULL DEFAULT '', image_data BLOB NOT NULL,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS character_custom_fields(
            id INTEGER PRIMARY KEY AUTOINCREMENT, character_id INTEGER NOT NULL,
            label TEXT NOT NULL DEFAULT '', value TEXT NOT NULL DEFAULT '', position INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS form_templates(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL DEFAULT 'Nouveau modèle',
            target_type TEXT NOT NULL DEFAULT 'character',
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS form_template_sections(
            id INTEGER PRIMARY KEY AUTOINCREMENT, template_id INTEGER NOT NULL,
            title TEXT NOT NULL DEFAULT 'Section', position INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(template_id) REFERENCES form_templates(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS form_template_fields(
            id INTEGER PRIMARY KEY AUTOINCREMENT, template_id INTEGER NOT NULL,
            section_id INTEGER NOT NULL, label TEXT NOT NULL DEFAULT 'Nouveau champ',
            field_type TEXT NOT NULL DEFAULT 'text_short', options_json TEXT NOT NULL DEFAULT '[]',
            help_text TEXT NOT NULL DEFAULT '', default_value TEXT NOT NULL DEFAULT '',
            required INTEGER NOT NULL DEFAULT 0, position INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(template_id) REFERENCES form_templates(id) ON DELETE CASCADE,
            FOREIGN KEY(section_id) REFERENCES form_template_sections(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS project_form_templates(
            project_id INTEGER NOT NULL, target_type TEXT NOT NULL, template_id INTEGER NOT NULL,
            PRIMARY KEY(project_id,target_type),
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY(template_id) REFERENCES form_templates(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS form_field_values(
            project_id INTEGER NOT NULL, target_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL DEFAULT 0, field_id INTEGER NOT NULL,
            value_text TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL,
            PRIMARY KEY(project_id,target_type,entity_id,field_id),
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY(field_id) REFERENCES form_template_fields(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS tags(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL DEFAULT 0,
            name TEXT COLLATE NOCASE NOT NULL DEFAULT '',
            color TEXT NOT NULL DEFAULT '#D84A32',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            UNIQUE(project_id,name));
        CREATE TABLE IF NOT EXISTS entity_tags(
            tag_id INTEGER NOT NULL, target_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            PRIMARY KEY(tag_id,target_type,entity_id),
            FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS scene_characters(
            scene_id INTEGER NOT NULL, character_id INTEGER NOT NULL,
            PRIMARY KEY(scene_id,character_id),
            FOREIGN KEY(scene_id) REFERENCES scene_rows(id) ON DELETE CASCADE,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS scene_events(
            scene_id INTEGER NOT NULL, event_id INTEGER NOT NULL,
            PRIMARY KEY(scene_id,event_id),
            FOREIGN KEY(scene_id) REFERENCES scene_rows(id) ON DELETE CASCADE,
            FOREIGN KEY(event_id) REFERENCES timeline_events(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS scene_story_nodes(
            scene_id INTEGER NOT NULL, node_id INTEGER NOT NULL,
            PRIMARY KEY(scene_id,node_id),
            FOREIGN KEY(scene_id) REFERENCES scene_rows(id) ON DELETE CASCADE,
            FOREIGN KEY(node_id) REFERENCES story_map_nodes(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS scene_theme_positions(
            scene_id INTEGER NOT NULL, position_id INTEGER NOT NULL,
            PRIMARY KEY(scene_id,position_id),
            FOREIGN KEY(scene_id) REFERENCES scene_rows(id) ON DELETE CASCADE,
            FOREIGN KEY(position_id) REFERENCES theme_positions(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS scene_theme_motifs(
            scene_id INTEGER NOT NULL, motif_id INTEGER NOT NULL,
            PRIMARY KEY(scene_id,motif_id),
            FOREIGN KEY(scene_id) REFERENCES scene_rows(id) ON DELETE CASCADE,
            FOREIGN KEY(motif_id) REFERENCES theme_motifs(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS story_map_node_characters(
            node_id INTEGER NOT NULL, character_id INTEGER NOT NULL,
            PRIMARY KEY(node_id,character_id),
            FOREIGN KEY(node_id) REFERENCES story_map_nodes(id) ON DELETE CASCADE,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS timeline_tracks(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            name TEXT NOT NULL DEFAULT 'Intrigue principale', color TEXT NOT NULL DEFAULT '#3D8EF7',
            position INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            UNIQUE(project_id,name),
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS timeline_events(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            track_id INTEGER,
            title TEXT NOT NULL DEFAULT '', time_hours REAL NOT NULL DEFAULT 0,
            display_label TEXT NOT NULL DEFAULT '', category TEXT NOT NULL DEFAULT 'Intrigue principale',
            description TEXT NOT NULL DEFAULT '', place TEXT NOT NULL DEFAULT '', consequence TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY(track_id) REFERENCES timeline_tracks(id) ON DELETE SET NULL);
        CREATE TABLE IF NOT EXISTS timeline_event_characters(
            event_id INTEGER NOT NULL, character_id INTEGER NOT NULL,
            PRIMARY KEY(event_id,character_id),
            FOREIGN KEY(event_id) REFERENCES timeline_events(id) ON DELETE CASCADE,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS script_meta(
            project_id INTEGER PRIMARY KEY, title TEXT NOT NULL DEFAULT '',
            author TEXT NOT NULL DEFAULT '', contact TEXT NOT NULL DEFAULT '',
            draft_date TEXT NOT NULL DEFAULT '', based_on TEXT NOT NULL DEFAULT '',
            copyright_notice TEXT NOT NULL DEFAULT '',
            include_title_page INTEGER NOT NULL DEFAULT 1,
            document_json TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS image_library(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            title TEXT NOT NULL DEFAULT '', category TEXT NOT NULL DEFAULT 'reference',
            notes TEXT NOT NULL DEFAULT '', file_name TEXT NOT NULL DEFAULT '',
            mime_type TEXT NOT NULL DEFAULT '', image_data BLOB NOT NULL,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS locations(
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
            position INTEGER NOT NULL DEFAULT 0, name TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL DEFAULT 'Autre', region TEXT NOT NULL DEFAULT '',
            epoch TEXT NOT NULL DEFAULT '', tags TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '', narrative_function TEXT NOT NULL DEFAULT '',
            atmosphere TEXT NOT NULL DEFAULT '', constraints_note TEXT NOT NULL DEFAULT '',
            evolution TEXT NOT NULL DEFAULT '', notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS location_characters(
            location_id INTEGER NOT NULL, character_id INTEGER NOT NULL,
            PRIMARY KEY(location_id,character_id),
            FOREIGN KEY(location_id) REFERENCES locations(id) ON DELETE CASCADE,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS location_events(
            location_id INTEGER NOT NULL, event_id INTEGER NOT NULL,
            PRIMARY KEY(location_id,event_id),
            FOREIGN KEY(location_id) REFERENCES locations(id) ON DELETE CASCADE,
            FOREIGN KEY(event_id) REFERENCES timeline_events(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS location_scenes(
            location_id INTEGER NOT NULL, scene_id INTEGER NOT NULL,
            PRIMARY KEY(location_id,scene_id),
            FOREIGN KEY(location_id) REFERENCES locations(id) ON DELETE CASCADE,
            FOREIGN KEY(scene_id) REFERENCES scene_rows(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS location_images(
            location_id INTEGER NOT NULL, image_id INTEGER NOT NULL,
            position INTEGER NOT NULL DEFAULT 0, is_primary INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY(location_id,image_id),
            FOREIGN KEY(location_id) REFERENCES locations(id) ON DELETE CASCADE,
            FOREIGN KEY(image_id) REFERENCES image_library(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS diagnostics(
            project_id INTEGER NOT NULL, doc_type TEXT NOT NULL, item_key TEXT NOT NULL, checked INTEGER NOT NULL DEFAULT 0,
            note TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL,
            PRIMARY KEY(project_id, doc_type, item_key), FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS ai_messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, project_id INTEGER,
            role TEXT NOT NULL, mode TEXT NOT NULL DEFAULT 'coach', content TEXT NOT NULL DEFAULT '', response_id TEXT NOT NULL DEFAULT '',
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE SET NULL);
        CREATE TABLE IF NOT EXISTS ai_notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, project_id INTEGER,
            kind TEXT NOT NULL DEFAULT 'feedback', content TEXT NOT NULL DEFAULT '',
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        """)
        node_columns = {row[1] for row in self.conn.execute("PRAGMA table_info(story_map_nodes)")}
        if "source_step_key" not in node_columns:
            self.conn.execute("ALTER TABLE story_map_nodes ADD COLUMN source_step_key TEXT NOT NULL DEFAULT ''")
        idea_columns = {row[1] for row in self.conn.execute("PRAGMA table_info(ideas)")}
        if "idea_type" not in idea_columns:
            self.conn.execute("ALTER TABLE ideas ADD COLUMN idea_type TEXT NOT NULL DEFAULT 'unclassified'")
        if "attachment_name" not in idea_columns:
            self.conn.execute("ALTER TABLE ideas ADD COLUMN attachment_name TEXT NOT NULL DEFAULT ''")
        if "attachment_mime" not in idea_columns:
            self.conn.execute("ALTER TABLE ideas ADD COLUMN attachment_mime TEXT NOT NULL DEFAULT ''")
        if "attachment_data" not in idea_columns:
            self.conn.execute("ALTER TABLE ideas ADD COLUMN attachment_data BLOB")
        if "what_if" not in idea_columns:
            self.conn.execute("ALTER TABLE ideas ADD COLUMN what_if TEXT NOT NULL DEFAULT ''")
        guided_run_columns = {row[1] for row in self.conn.execute("PRAGMA table_info(guided_runs)")}
        if "applied_target_id" not in guided_run_columns:
            self.conn.execute(
                "ALTER TABLE guided_runs ADD COLUMN applied_target_id INTEGER NOT NULL DEFAULT 0"
            )
        script_meta_columns = {
            row[1] for row in self.conn.execute("PRAGMA table_info(script_meta)")
        }
        for column, declaration in (
            ("based_on", "TEXT NOT NULL DEFAULT ''"),
            ("copyright_notice", "TEXT NOT NULL DEFAULT ''"),
            ("include_title_page", "INTEGER NOT NULL DEFAULT 1"),
            ("document_json", "TEXT NOT NULL DEFAULT ''"),
        ):
            if column not in script_meta_columns:
                self.conn.execute(
                    f"ALTER TABLE script_meta ADD COLUMN {column} {declaration}"
                )
        project_columns = {row[1] for row in self.conn.execute("PRAGMA table_info(projects)")}
        for column, declaration in (
            ("project_type", "TEXT NOT NULL DEFAULT 'film'"),
            ("story_format", "TEXT NOT NULL DEFAULT 'free'"),
            ("target_duration", "INTEGER NOT NULL DEFAULT 0"),
            ("start_mode", "TEXT NOT NULL DEFAULT 'free'"),
            ("project_status", "TEXT NOT NULL DEFAULT 'ongoing'"),
            ("archived", "INTEGER NOT NULL DEFAULT 0"),
            ("updated_at", "TEXT NOT NULL DEFAULT ''"),
        ):
            if column not in project_columns:
                self.conn.execute(f"ALTER TABLE projects ADD COLUMN {column} {declaration}")
        self.conn.execute(
            "UPDATE projects SET updated_at=created_at WHERE TRIM(updated_at)=''"
        )
        scene_columns = {row[1] for row in self.conn.execute("PRAGMA table_info(scene_rows)")}
        for column, declaration in (
            ("objective", "TEXT NOT NULL DEFAULT ''"),
            ("opposition", "TEXT NOT NULL DEFAULT ''"),
            ("change_note", "TEXT NOT NULL DEFAULT ''"),
            ("status", "TEXT NOT NULL DEFAULT 'idea'"),
            ("moment_label", "TEXT NOT NULL DEFAULT ''"),
            ("driver_character_id", "INTEGER"),
            ("character_objective", "TEXT NOT NULL DEFAULT ''"),
            ("conflict_note", "TEXT NOT NULL DEFAULT ''"),
            ("information_revealed", "TEXT NOT NULL DEFAULT ''"),
            ("entry_state", "TEXT NOT NULL DEFAULT ''"),
            ("exit_state", "TEXT NOT NULL DEFAULT ''"),
            ("notes", "TEXT NOT NULL DEFAULT ''"),
            ("source_sequence_id", "INTEGER NOT NULL DEFAULT 0"),
        ):
            if column not in scene_columns:
                self.conn.execute(f"ALTER TABLE scene_rows ADD COLUMN {column} {declaration}")
        character_columns = {row[1] for row in self.conn.execute("PRAGMA table_info(characters)")}
        for column, declaration in (
            ("gender", "TEXT NOT NULL DEFAULT 'unspecified'"),
            ("age", "TEXT NOT NULL DEFAULT ''"),
            ("occupation", "TEXT NOT NULL DEFAULT ''"),
            ("description", "TEXT NOT NULL DEFAULT ''"),
            ("appearance", "TEXT NOT NULL DEFAULT ''"),
            ("personality", "TEXT NOT NULL DEFAULT ''"),
            ("objective", "TEXT NOT NULL DEFAULT ''"),
            ("need", "TEXT NOT NULL DEFAULT ''"),
            ("fear", "TEXT NOT NULL DEFAULT ''"),
            ("weakness", "TEXT NOT NULL DEFAULT ''"),
            ("wound", "TEXT NOT NULL DEFAULT ''"),
            ("values_note", "TEXT NOT NULL DEFAULT ''"),
            ("beliefs", "TEXT NOT NULL DEFAULT ''"),
            ("contradictions", "TEXT NOT NULL DEFAULT ''"),
            ("secrets", "TEXT NOT NULL DEFAULT ''"),
            ("backstory", "TEXT NOT NULL DEFAULT ''"),
            ("start_situation", "TEXT NOT NULL DEFAULT ''"),
            ("end_situation", "TEXT NOT NULL DEFAULT ''"),
            ("speaking_style", "TEXT NOT NULL DEFAULT ''"),
            ("portrait_name", "TEXT NOT NULL DEFAULT ''"),
            ("portrait_mime", "TEXT NOT NULL DEFAULT ''"),
            ("portrait_data", "BLOB"),
        ):
            if column not in character_columns:
                self.conn.execute(f"ALTER TABLE characters ADD COLUMN {column} {declaration}")
        relationship_columns = {
            row[1] for row in self.conn.execute("PRAGMA table_info(character_relationships)")
        }
        for column, declaration in (
            ("map_id", "INTEGER"),
            ("secret", "TEXT NOT NULL DEFAULT ''"),
            ("evolution", "TEXT NOT NULL DEFAULT ''"),
            ("color", "TEXT NOT NULL DEFAULT ''"),
        ):
            if column not in relationship_columns:
                self.conn.execute(
                    f"ALTER TABLE character_relationships ADD COLUMN {column} {declaration}"
                )
        for project in self.conn.execute(
            "SELECT DISTINCT project_id FROM character_relationships WHERE map_id IS NULL OR map_id=0"
        ).fetchall():
            project_id = int(project[0])
            row = self.conn.execute(
                "SELECT id FROM relationship_maps WHERE project_id=? ORDER BY id LIMIT 1",
                (project_id,),
            ).fetchone()
            if row:
                map_id = int(row[0])
            else:
                map_id = self.conn.execute(
                    """INSERT INTO relationship_maps(project_id,name,map_type,created_at,updated_at)
                    VALUES(?,?,?,?,?)""",
                    (project_id, "Relations générales", "general", NOW(), NOW()),
                ).lastrowid
            self.conn.execute(
                "UPDATE character_relationships SET map_id=? WHERE project_id=? AND (map_id IS NULL OR map_id=0)",
                (map_id, project_id),
            )
        timeline_columns = {row[1] for row in self.conn.execute("PRAGMA table_info(timeline_events)")}
        if "track_id" not in timeline_columns:
            self.conn.execute("ALTER TABLE timeline_events ADD COLUMN track_id INTEGER")
        for legacy_track in self.conn.execute(
            """SELECT DISTINCT project_id,COALESCE(NULLIF(TRIM(category),''),'Intrigue principale') name
            FROM timeline_events WHERE track_id IS NULL OR track_id=0"""
        ).fetchall():
            project_id = int(legacy_track[0])
            name = str(legacy_track[1])
            existing = self.conn.execute(
                "SELECT id FROM timeline_tracks WHERE project_id=? AND name=?",
                (project_id, name),
            ).fetchone()
            if existing:
                track_id = int(existing[0])
            else:
                position = int(self.conn.execute(
                    "SELECT COUNT(*) FROM timeline_tracks WHERE project_id=?",
                    (project_id,),
                ).fetchone()[0])
                track_id = self.conn.execute(
                    """INSERT INTO timeline_tracks(project_id,name,color,position,created_at,updated_at)
                    VALUES(?,?,?,?,?,?)""",
                    (project_id, name, "#3D8EF7", position, NOW(), NOW()),
                ).lastrowid
            self.conn.execute(
                """UPDATE timeline_events SET track_id=?
                WHERE project_id=? AND COALESCE(NULLIF(TRIM(category),''),'Intrigue principale')=?
                AND (track_id IS NULL OR track_id=0)""",
                (track_id, project_id, name),
            )
        for table in (
            "project_docs",
            "doc_versions",
            "project_questions",
            "story_map_answers",
            "synopsis_answers",
            "story_map_nodes",
            "story_map_links",
            "sequence_blocks",
            "scene_rows",
            "outline_items",
            "development_status",
            "characters",
            "world_profiles",
            "world_rules",
            "world_terms",
            "theme_profiles",
            "theme_positions",
            "theme_motifs",
            "conflicts",
            "character_arcs",
            "hook_profiles",
            "story_promises",
            "story_moments",
            "relationship_maps",
            "character_relationships",
            "character_groups",
            "character_references",
            "timeline_tracks",
            "timeline_events",
            "image_library",
            "script_meta",
        ):
            self.conn.executescript(
                f"""
                CREATE TRIGGER IF NOT EXISTS touch_{table}_insert
                AFTER INSERT ON {table}
                BEGIN
                    UPDATE projects SET updated_at=datetime('now','localtime') WHERE id=NEW.project_id;
                END;
                CREATE TRIGGER IF NOT EXISTS touch_{table}_update
                AFTER UPDATE ON {table}
                BEGIN
                    UPDATE projects SET updated_at=datetime('now','localtime') WHERE id=NEW.project_id;
                END;
                CREATE TRIGGER IF NOT EXISTS touch_{table}_delete
                AFTER DELETE ON {table}
                BEGIN
                    UPDATE projects SET updated_at=datetime('now','localtime') WHERE id=OLD.project_id;
                END;
                """
            )
        self.conn.executescript(
            """
            CREATE TRIGGER IF NOT EXISTS touch_relationship_map_nodes_insert
            AFTER INSERT ON relationship_map_nodes
            BEGIN
                UPDATE relationship_maps SET updated_at=datetime('now','localtime') WHERE id=NEW.map_id;
                UPDATE projects SET updated_at=datetime('now','localtime')
                WHERE id=(SELECT project_id FROM relationship_maps WHERE id=NEW.map_id);
            END;
            CREATE TRIGGER IF NOT EXISTS touch_relationship_map_nodes_update
            AFTER UPDATE ON relationship_map_nodes
            BEGIN
                UPDATE relationship_maps SET updated_at=datetime('now','localtime') WHERE id=NEW.map_id;
                UPDATE projects SET updated_at=datetime('now','localtime')
                WHERE id=(SELECT project_id FROM relationship_maps WHERE id=NEW.map_id);
            END;
            CREATE TRIGGER IF NOT EXISTS touch_relationship_map_nodes_delete
            AFTER DELETE ON relationship_map_nodes
            BEGIN
                UPDATE relationship_maps SET updated_at=datetime('now','localtime') WHERE id=OLD.map_id;
                UPDATE projects SET updated_at=datetime('now','localtime')
                WHERE id=(SELECT project_id FROM relationship_maps WHERE id=OLD.map_id);
            END;
            CREATE TRIGGER IF NOT EXISTS touch_guided_runs_insert
            AFTER INSERT ON guided_runs WHEN NEW.project_id IS NOT NULL
            BEGIN
                UPDATE projects SET updated_at=datetime('now','localtime') WHERE id=NEW.project_id;
            END;
            CREATE TRIGGER IF NOT EXISTS touch_guided_runs_update
            AFTER UPDATE ON guided_runs WHEN NEW.project_id IS NOT NULL
            BEGIN
                UPDATE projects SET updated_at=datetime('now','localtime') WHERE id=NEW.project_id;
            END;
            CREATE TRIGGER IF NOT EXISTS touch_guided_answers_insert
            AFTER INSERT ON guided_answers
            BEGIN
                UPDATE projects SET updated_at=datetime('now','localtime')
                WHERE id=(SELECT project_id FROM guided_runs WHERE id=NEW.run_id);
            END;
            CREATE TRIGGER IF NOT EXISTS touch_guided_answers_update
            AFTER UPDATE ON guided_answers
            BEGIN
                UPDATE projects SET updated_at=datetime('now','localtime')
                WHERE id=(SELECT project_id FROM guided_runs WHERE id=NEW.run_id);
            END;
            """
        )
        migration_key = "development_status_explicit_v1"
        migrated = self.conn.execute(
            "SELECT value FROM settings WHERE key=?",
            (migration_key,),
        ).fetchone()
        if not migrated:
            # Existing versions considered a non-empty document completed.
            # Seed these states once, then require an explicit user choice.
            self.conn.execute(
                """INSERT OR IGNORE INTO development_status(project_id,doc_type,status,updated_at)
                SELECT project_id,doc_type,'complete',? FROM project_docs
                WHERE TRIM(content)<>'' AND doc_type<>'story_map'""",
                (NOW(),),
            )
            self.conn.execute(
                """INSERT OR IGNORE INTO development_status(project_id,doc_type,status,updated_at)
                SELECT project_id,'story_map','complete',? FROM story_map_nodes
                WHERE TRIM(content)<>'' OR (TRIM(title)<>'' AND title<>'Carte sans titre')
                GROUP BY project_id""",
                (NOW(),),
            )
            self.conn.execute(
                """INSERT OR IGNORE INTO development_status(project_id,doc_type,status,updated_at)
                SELECT project_id,'story_map','complete',? FROM story_map_answers
                WHERE TRIM(answer)<>'' GROUP BY project_id HAVING COUNT(*)>=9""",
                (NOW(),),
            )
            self.conn.execute(
                """INSERT OR IGNORE INTO development_status(project_id,doc_type,status,updated_at)
                SELECT project_id,'outline','complete',? FROM sequence_blocks
                WHERE TRIM(title)<>'' OR TRIM(purpose)<>'' OR TRIM(events)<>'' OR TRIM(consequence)<>''
                GROUP BY project_id""",
                (NOW(),),
            )
            self.conn.execute(
                """INSERT OR IGNORE INTO development_status(project_id,doc_type,status,updated_at)
                SELECT project_id,'scenes','complete',? FROM scene_rows
                WHERE TRIM(title)<>'' GROUP BY project_id""",
                (NOW(),),
            )
            self.conn.execute(
                "INSERT INTO settings(key,value) VALUES(?,?)",
                (migration_key, "1"),
            )
        if 'snapshot_json' not in {row[1] for row in self.conn.execute('PRAGMA table_info(doc_versions)')}:
            self.conn.execute("ALTER TABLE doc_versions ADD COLUMN snapshot_json TEXT NOT NULL DEFAULT ''")
        self.conn.execute(
            """INSERT INTO guided_application_history(
            run_id,step_key,project_id,target_type,target_id,target_field,
            event_kind,status,evidence,occurred_at,updated_at)
            SELECT current.run_id,current.step_key,current.project_id,current.target_type,
            current.target_id,current.target_field,'legacy',current.status,current.evidence,
            current.applied_at,current.updated_at
            FROM guided_applications current
            WHERE NOT EXISTS(
                SELECT 1 FROM guided_application_history history
                WHERE history.run_id=current.run_id AND history.step_key=current.step_key
            )"""
        )
        self.conn.commit()

    def q(self, sql, params=()): return self.conn.execute(sql, params).fetchall()
    def one(self, sql, params=()): return self.conn.execute(sql, params).fetchone()
    def run(self, sql, params=()):
        cur = self.conn.execute(sql, params)
        if not self._transaction_depth:
            self.conn.commit()
        return cur

    @contextmanager
    def transaction(self):
        """Nestable savepoints; helpers must not commit the caller's work."""
        name = f'storyforge_{self._transaction_depth}'
        self.conn.execute(f'SAVEPOINT {name}')
        self._transaction_depth += 1
        try:
            yield
            self.conn.execute(f'RELEASE SAVEPOINT {name}')
        except BaseException:
            self.conn.execute(f'ROLLBACK TO SAVEPOINT {name}')
            self.conn.execute(f'RELEASE SAVEPOINT {name}')
            raise
        finally:
            self._transaction_depth -= 1
    def setting(self, key, default=""):
        row=self.one("SELECT value FROM settings WHERE key=?",(key,)); return row[0] if row else default
    def set_setting(self,key,value):
        self.run("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(key,str(value)))
    def entity_tag_names(self, project_id, target_type, entity_id):
        return [
            row["name"]
            for row in self.q(
                """SELECT tag.name FROM entity_tags link
                JOIN tags tag ON tag.id=link.tag_id
                WHERE tag.project_id=? AND link.target_type=? AND link.entity_id=?
                ORDER BY tag.name COLLATE NOCASE""",
                (int(project_id or 0), target_type, int(entity_id or 0)),
            )
        ]
    def set_entity_tags(self, project_id, target_type, entity_id, names):
        project_id = int(project_id or 0)
        entity_id = int(entity_id or 0)
        cleaned = []
        for raw_name in names:
            name = str(raw_name).strip().lstrip("#").strip()
            if name and name.casefold() not in {value.casefold() for value in cleaned}:
                cleaned.append(name)
        with self.transaction():
            self.conn.execute(
                """DELETE FROM entity_tags WHERE target_type=? AND entity_id=?
                AND tag_id IN (SELECT id FROM tags WHERE project_id=?)""",
                (target_type, entity_id, project_id),
            )
            for name in cleaned:
                self.conn.execute(
                    """INSERT INTO tags(project_id,name,color,created_at,updated_at)
                    VALUES(?,?,?,?,?) ON CONFLICT(project_id,name)
                    DO UPDATE SET updated_at=excluded.updated_at""",
                    (project_id, name, "#D84A32", NOW(), NOW()),
                )
                tag_id = self.conn.execute(
                    "SELECT id FROM tags WHERE project_id=? AND name=? COLLATE NOCASE",
                    (project_id, name),
                ).fetchone()[0]
                self.conn.execute(
                    """INSERT OR IGNORE INTO entity_tags(tag_id,target_type,entity_id)
                    VALUES(?,?,?)""",
                    (tag_id, target_type, entity_id),
                )
    def ensure_relationship_map(self, pid, name="Relations générales", map_type="general"):
        row = self.one(
            "SELECT * FROM relationship_maps WHERE project_id=? ORDER BY id LIMIT 1",
            (pid,),
        )
        if not row:
            map_id = self.run(
                """INSERT INTO relationship_maps(project_id,name,map_type,created_at,updated_at)
                VALUES(?,?,?,?,?)""",
                (pid, name, map_type, NOW(), NOW()),
            ).lastrowid
            row = self.one("SELECT * FROM relationship_maps WHERE id=?", (map_id,))
        self.run(
            """UPDATE character_relationships SET map_id=?
            WHERE project_id=? AND (map_id IS NULL OR map_id=0)""",
            (row["id"], pid),
        )
        return row
    def ensure_timeline_track(self, pid, name="Intrigue principale", color="#3D8EF7"):
        row = self.one(
            "SELECT * FROM timeline_tracks WHERE project_id=? AND name=?",
            (pid, name),
        )
        if not row:
            position = int(self.one(
                "SELECT COUNT(*) FROM timeline_tracks WHERE project_id=?",
                (pid,),
            )[0])
            track_id = self.run(
                """INSERT INTO timeline_tracks(project_id,name,color,position,created_at,updated_at)
                VALUES(?,?,?,?,?,?)""",
                (pid, name, color, position, NOW(), NOW()),
            ).lastrowid
            row = self.one("SELECT * FROM timeline_tracks WHERE id=?", (track_id,))
        return row
    def ensure_doc(self,pid,doc_type,title):
        self.run("INSERT OR IGNORE INTO project_docs(project_id,doc_type,title,content,updated_at) VALUES(?,?,?,?,?)",(pid,doc_type,title,"",NOW()))
        return self.one("SELECT * FROM project_docs WHERE project_id=? AND doc_type=?",(pid,doc_type))
    def save_doc(self,pid,doc_type,content):
        self.run("UPDATE project_docs SET content=?,updated_at=? WHERE project_id=? AND doc_type=?",(content,NOW(),pid,doc_type))
    def snapshot(self,pid,doc_type,content,label=None,snapshot_json=""):
        n=self.one("SELECT COUNT(*) c FROM doc_versions WHERE project_id=? AND doc_type=?",(pid,doc_type))[0]+1
        return self.run("INSERT INTO doc_versions(project_id,doc_type,label,content,created_at,snapshot_json) VALUES(?,?,?,?,?,?)",(pid,doc_type,label or f"V{n}",content,NOW(),snapshot_json)).lastrowid
    def save_screenplay(self, pid, document_json, *, title_meta=None):
        from screenplay_model import ScreenplayDocument
        document = ScreenplayDocument.from_json(document_json)
        if document is None:
            raise ValueError('Scénario structuré invalide')
        with self.transaction():
            project = self.one('SELECT title FROM projects WHERE id=?', (pid,))
            if not project:
                raise ValueError('Projet introuvable')
            self.ensure_doc(pid, 'script', 'Scénario')
            self.save_doc(pid, 'script', document.to_plain_text())
            self.run('INSERT OR IGNORE INTO script_meta(project_id,title,updated_at) VALUES(?,?,?)',
                     (pid, project['title'], NOW()))
            self.run('UPDATE script_meta SET document_json=?,updated_at=? WHERE project_id=?',
                     (document.to_json(), NOW(), pid))
            if title_meta is not None:
                fields = ('title', 'author', 'contact', 'draft_date', 'based_on', 'copyright_notice', 'include_title_page')
                for field in fields:
                    if field in title_meta:
                        self.run(f'UPDATE script_meta SET {field}=? WHERE project_id=?', (title_meta[field], pid))
            self.run("UPDATE projects SET current_document='script' WHERE id=?", (pid,))

    def snapshot_screenplay(self, pid, label=None):
        with self.transaction():
            meta = self.one('SELECT * FROM script_meta WHERE project_id=?', (pid,))
            doc = self.one("SELECT content FROM project_docs WHERE project_id=? AND doc_type='script'", (pid,))
            if not meta or not doc:
                raise ValueError('Scénario introuvable')
            payload = json.dumps({'format': 'storyforge-script-snapshot-v1', 'meta': dict(meta)}, ensure_ascii=False)
            return self.snapshot(pid, 'script', doc['content'], label, payload)

    def restore_screenplay_version(self, pid, version_id):
        from screenplay_model import ScreenplayDocument
        with self.transaction():
            row = self.one("SELECT * FROM doc_versions WHERE id=? AND project_id=? AND doc_type='script'", (version_id, pid))
            if not row:
                raise ValueError('Version de scénario introuvable')
            meta = None
            if row['snapshot_json']:
                payload = json.loads(row['snapshot_json'])
                if payload.get('format') != 'storyforge-script-snapshot-v1':
                    raise ValueError('Format de version inconnu')
                meta = payload['meta']
                document = ScreenplayDocument.from_json(meta['document_json'])
                if document is None:
                    raise ValueError('Version structurée invalide')
            else:
                document = ScreenplayDocument.from_legacy_text(row['content'], project_id=pid)
            if self.one('SELECT project_id FROM script_meta WHERE project_id=?', (pid,)):
                self.snapshot_screenplay(pid, 'Avant restauration')
            self.save_screenplay(pid, document.to_json(), title_meta=meta)

    def ensure_learning_work(self, session_key, step_index, concept_key):
        previous = self.one(
            "SELECT answer FROM learning_answers WHERE session_key=? AND step_index=?",
            (session_key, step_index),
        )
        self.run(
            "INSERT OR IGNORE INTO learning_work(session_key,step_index,concept_key,draft,updated_at) VALUES(?,?,?,?,?)",
            (session_key, step_index, concept_key, previous[0] if previous else "", NOW()),
        )
        return self.one(
            "SELECT * FROM learning_work WHERE session_key=? AND step_index=?",
            (session_key, step_index),
        )
    def save_learning_work(self, session_key, step_index, concept_key, draft, feedback, revision, takeaway, mastery, status):
        self.run(
            """INSERT INTO learning_work(
                session_key,step_index,concept_key,draft,feedback,revision,takeaway,mastery,status,updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(session_key,step_index) DO UPDATE SET
                concept_key=excluded.concept_key,draft=excluded.draft,feedback=excluded.feedback,
                revision=excluded.revision,takeaway=excluded.takeaway,mastery=excluded.mastery,
                status=excluded.status,updated_at=excluded.updated_at""",
            (session_key, step_index, concept_key, draft, feedback, revision, takeaway, mastery, status, NOW()),
        )
        self.run(
            """INSERT INTO learning_answers(session_key,step_index,answer,updated_at) VALUES(?,?,?,?)
            ON CONFLICT(session_key,step_index) DO UPDATE SET answer=excluded.answer,updated_at=excluded.updated_at""",
            (session_key, step_index, revision or draft, NOW()),
        )
    def set_concept_mastery(self, concept_key, label, status, evidence=""):
        self.run(
            """INSERT INTO concept_mastery(concept_key,label,status,evidence,updated_at) VALUES(?,?,?,?,?)
            ON CONFLICT(concept_key) DO UPDATE SET label=excluded.label,status=excluded.status,
            evidence=excluded.evidence,updated_at=excluded.updated_at""",
            (concept_key, label, status, evidence, NOW()),
        )
    def guided_application(self, run_id, step_key):
        return self.one(
            "SELECT * FROM guided_applications WHERE run_id=? AND step_key=?",
            (run_id, step_key),
        )
    def guided_application_history(self, run_id, step_key):
        return self.q(
            """SELECT * FROM guided_application_history
            WHERE run_id=? AND step_key=? ORDER BY id""",
            (run_id, step_key),
        )
    def record_guided_application_event(
        self,
        run_id,
        step_key,
        project_id,
        target_type="",
        target_id=0,
        target_field="",
        event_kind="applied",
        status="en pratique",
        evidence="",
        occurred_at="",
    ):
        now = NOW()
        self.run(
            """INSERT INTO guided_application_history(
            run_id,step_key,project_id,target_type,target_id,target_field,
            event_kind,status,evidence,occurred_at,updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (
                run_id,
                step_key,
                project_id,
                target_type,
                int(target_id or 0),
                target_field,
                event_kind,
                status,
                evidence,
                occurred_at or now,
                now,
            ),
        )
    def save_guided_application(
        self,
        run_id,
        step_key,
        project_id,
        target_type="",
        target_id=0,
        target_field="",
        status="en pratique",
        evidence="",
    ):
        now = NOW()
        self.run(
            """INSERT INTO guided_applications(
            run_id,step_key,project_id,target_type,target_id,target_field,status,evidence,applied_at,updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(run_id,step_key) DO UPDATE SET
            project_id=excluded.project_id,target_type=excluded.target_type,
            target_id=excluded.target_id,target_field=excluded.target_field,
            status=excluded.status,evidence=excluded.evidence,
            applied_at=excluded.applied_at,updated_at=excluded.updated_at""",
            (
                run_id,
                step_key,
                project_id,
                target_type,
                int(target_id or 0),
                target_field,
                status,
                evidence,
                now,
                now,
            ),
        )
        self.run("UPDATE guided_runs SET updated_at=? WHERE id=?", (now, run_id))
    def create_guided_run(
        self,
        guide_key,
        title,
        project_id=None,
        idea_id=None,
        assistance_level="discovery",
        legacy_session_key="",
    ):
        return self.run(
            """INSERT INTO guided_runs(
            guide_key,title,project_id,idea_id,assistance_level,current_step,status,
            legacy_session_key,applied_at,created_at,updated_at
            ) VALUES(?,?,?,?,?,0,'ongoing',?,'',?,?)""",
            (
                guide_key,
                title,
                project_id,
                idea_id,
                assistance_level,
                legacy_session_key,
                NOW(),
                NOW(),
            ),
        ).lastrowid
    def guided_run(self, run_id):
        return self.one("SELECT * FROM guided_runs WHERE id=?", (run_id,))
    def ensure_guided_answer(self, run_id, step_key, step_index):
        self.run(
            """INSERT OR IGNORE INTO guided_answers(
            run_id,step_key,step_index,answer,status,updated_at
            ) VALUES(?,?,?,'','draft',?)""",
            (run_id, step_key, step_index, NOW()),
        )
        return self.one(
            "SELECT * FROM guided_answers WHERE run_id=? AND step_key=?",
            (run_id, step_key),
        )
    def save_guided_answer(self, run_id, step_key, step_index, answer, status="draft"):
        self.run(
            """INSERT INTO guided_answers(
            run_id,step_key,step_index,answer,status,updated_at
            ) VALUES(?,?,?,?,?,?) ON CONFLICT(run_id,step_key) DO UPDATE SET
            step_index=excluded.step_index,answer=excluded.answer,
            status=excluded.status,updated_at=excluded.updated_at""",
            (run_id, step_key, step_index, answer, status, NOW()),
        )
        self.run("UPDATE guided_runs SET updated_at=? WHERE id=?", (NOW(), run_id))
    def update_guided_run(self, run_id, **values):
        allowed = {
            "title", "project_id", "idea_id", "assistance_level", "current_step",
            "status", "legacy_session_key", "applied_at", "applied_target_id",
        }
        changes = {key: value for key, value in values.items() if key in allowed}
        if not changes:
            return
        changes["updated_at"] = NOW()
        columns = ",".join(f"{key}=?" for key in changes)
        self.run(
            f"UPDATE guided_runs SET {columns} WHERE id=?",
            (*changes.values(), run_id),
        )
    def save_story_map_answer(self, project_id, step_key, answer):
        self.run(
            """INSERT INTO story_map_answers(project_id,step_key,answer,updated_at) VALUES(?,?,?,?)
            ON CONFLICT(project_id,step_key) DO UPDATE SET answer=excluded.answer,updated_at=excluded.updated_at""",
            (project_id, step_key, answer, NOW()),
        )
    def save_synopsis_answer(self, project_id, step_key, answer):
        self.run(
            """INSERT INTO synopsis_answers(project_id,step_key,answer,updated_at) VALUES(?,?,?,?)
            ON CONFLICT(project_id,step_key) DO UPDATE SET answer=excluded.answer,updated_at=excluded.updated_at""",
            (project_id, step_key, answer, NOW()),
        )
    def create_story_map_node(self, project_id, title, content="", kind="idea", x=80, y=80, source_step_key=""):
        return self.run(
            "INSERT INTO story_map_nodes(project_id,title,content,kind,source_step_key,x,y,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
            (project_id, title, content, kind, source_step_key, x, y, NOW(), NOW()),
        ).lastrowid
    def update_story_map_node(self, node_id, title, content, kind):
        self.run(
            "UPDATE story_map_nodes SET title=?,content=?,kind=?,updated_at=? WHERE id=?",
            (title, content, kind, NOW(), node_id),
        )
    def move_story_map_node(self, node_id, x, y):
        self.run("UPDATE story_map_nodes SET x=?,y=?,updated_at=? WHERE id=?", (x, y, NOW(), node_id))
    def create_story_map_link(self, project_id, source_id, target_id):
        return self.run(
            "INSERT OR IGNORE INTO story_map_links(project_id,source_id,target_id,label,created_at) VALUES(?,?,?,?,?)",
            (project_id, source_id, target_id, "", NOW()),
        ).lastrowid
    def create_sequence_block(
        self,
        project_id,
        position,
        title,
        purpose="",
        events="",
        consequence="",
        source_node_id=0,
    ):
        return self.run(
            "INSERT INTO sequence_blocks(project_id,position,title,purpose,events,consequence,source_node_id,created_at,updated_at) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (project_id, position, title, purpose, events, consequence, source_node_id, NOW(), NOW()),
        ).lastrowid
    def update_sequence_block(self, block_id, title, purpose, events, consequence):
        self.run(
            "UPDATE sequence_blocks SET title=?,purpose=?,events=?,consequence=?,updated_at=? WHERE id=?",
            (title, purpose, events, consequence, NOW(), block_id),
        )
    def reorder_sequence_blocks(self, project_id, ordered_ids):
        with self.transaction():
            for position, block_id in enumerate(ordered_ids):
                self.conn.execute(
                    "UPDATE sequence_blocks SET position=?,updated_at=? WHERE id=? AND project_id=?",
                    (position, NOW(), block_id, project_id),
                )
    def create_outline_item(
        self,
        project_id,
        position,
        item_type,
        title="",
        summary="",
        function_note="",
        consequence="",
        parent_id=None,
        collapsed=0,
        source_sequence_id=0,
        source_scene_id=0,
        source_node_id=0,
    ):
        return self.run(
            """INSERT INTO outline_items(
            project_id,parent_id,position,item_type,title,summary,function_note,consequence,
            collapsed,source_sequence_id,source_scene_id,source_node_id,created_at,updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                project_id, parent_id, position, item_type, title, summary, function_note,
                consequence, int(bool(collapsed)), source_sequence_id, source_scene_id,
                source_node_id, NOW(), NOW(),
            ),
        ).lastrowid
    def update_outline_item(
        self,
        item_id,
        title,
        summary,
        function_note,
        consequence,
        item_type=None,
    ):
        if item_type is None:
            self.run(
                """UPDATE outline_items SET title=?,summary=?,function_note=?,consequence=?,updated_at=?
                WHERE id=?""",
                (title, summary, function_note, consequence, NOW(), item_id),
            )
        else:
            self.run(
                """UPDATE outline_items SET item_type=?,title=?,summary=?,function_note=?,consequence=?,updated_at=?
                WHERE id=?""",
                (item_type, title, summary, function_note, consequence, NOW(), item_id),
            )
    def save_outline_structure(self, project_id, placements):
        with self.transaction():
            for item_id, parent_id, position in placements:
                self.conn.execute(
                    """UPDATE outline_items SET parent_id=?,position=?,updated_at=?
                    WHERE id=? AND project_id=?""",
                    (parent_id, position, NOW(), item_id, project_id),
                )
    def backup_to(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        target = sqlite3.connect(path)
        try:
            self.conn.backup(target)
        finally:
            target.close()
    def export_project(self,pid,path:Path):
        p=dict(self.one("SELECT * FROM projects WHERE id=?",(pid,)))
        docs=[dict(r) for r in self.q("SELECT * FROM project_docs WHERE project_id=?",(pid,))]
        qs=[dict(r) for r in self.q("SELECT * FROM project_questions WHERE project_id=?",(pid,))]
        story_map=[dict(r) for r in self.q("SELECT * FROM story_map_answers WHERE project_id=?",(pid,))]
        synopsis_answers=[dict(r) for r in self.q("SELECT * FROM synopsis_answers WHERE project_id=?",(pid,))]
        map_nodes=[dict(r) for r in self.q("SELECT * FROM story_map_nodes WHERE project_id=?",(pid,))]
        map_links=[dict(r) for r in self.q("SELECT * FROM story_map_links WHERE project_id=?",(pid,))]
        sequence_blocks=[dict(r) for r in self.q("SELECT * FROM sequence_blocks WHERE project_id=? ORDER BY position,id",(pid,))]
        scene_rows=[dict(r) for r in self.q("SELECT * FROM scene_rows WHERE project_id=? ORDER BY position,id",(pid,))]
        outline_items=[dict(r) for r in self.q(
            "SELECT * FROM outline_items WHERE project_id=? ORDER BY parent_id,position,id", (pid,)
        )]
        development_status=[dict(r) for r in self.q("SELECT * FROM development_status WHERE project_id=?",(pid,))]
        characters=[dict(r) for r in self.q("SELECT * FROM characters WHERE project_id=? ORDER BY id",(pid,))]
        world_profile_row=self.one("SELECT * FROM world_profiles WHERE project_id=?",(pid,))
        world_profile=dict(world_profile_row) if world_profile_row else {}
        world_rules=[dict(r) for r in self.q("SELECT * FROM world_rules WHERE project_id=? ORDER BY id",(pid,))]
        world_terms=[dict(r) for r in self.q("SELECT * FROM world_terms WHERE project_id=? ORDER BY category,term,id",(pid,))]
        theme_profile_row=self.one("SELECT * FROM theme_profiles WHERE project_id=?",(pid,))
        theme_profile=dict(theme_profile_row) if theme_profile_row else {}
        theme_positions=[dict(r) for r in self.q(
            "SELECT * FROM theme_positions WHERE project_id=? ORDER BY position,id", (pid,)
        )]
        theme_position_characters=[dict(r) for r in self.q(
            """SELECT link.* FROM theme_position_characters link
            JOIN theme_positions item ON item.id=link.position_id WHERE item.project_id=?""",
            (pid,),
        )]
        theme_motifs=[dict(r) for r in self.q(
            "SELECT * FROM theme_motifs WHERE project_id=? ORDER BY position,id", (pid,)
        )]
        theme_motif_locations=[dict(r) for r in self.q(
            """SELECT link.* FROM theme_motif_locations link
            JOIN theme_motifs motif ON motif.id=link.motif_id WHERE motif.project_id=?""",
            (pid,),
        )]
        theme_motif_events=[dict(r) for r in self.q(
            """SELECT link.* FROM theme_motif_events link
            JOIN theme_motifs motif ON motif.id=link.motif_id WHERE motif.project_id=?""",
            (pid,),
        )]
        theme_motif_images=[dict(r) for r in self.q(
            """SELECT link.* FROM theme_motif_images link
            JOIN theme_motifs motif ON motif.id=link.motif_id WHERE motif.project_id=?""",
            (pid,),
        )]
        conflicts=[dict(r) for r in self.q(
            "SELECT * FROM conflicts WHERE project_id=? ORDER BY position,id", (pid,)
        )]
        conflict_characters=[dict(r) for r in self.q(
            """SELECT link.* FROM conflict_characters link
            JOIN conflicts item ON item.id=link.conflict_id WHERE item.project_id=?""", (pid,)
        )]
        conflict_groups=[dict(r) for r in self.q(
            """SELECT link.* FROM conflict_groups link
            JOIN conflicts item ON item.id=link.conflict_id WHERE item.project_id=?""", (pid,)
        )]
        conflict_scenes=[dict(r) for r in self.q(
            """SELECT link.* FROM conflict_scenes link
            JOIN conflicts item ON item.id=link.conflict_id WHERE item.project_id=?""", (pid,)
        )]
        conflict_story_nodes=[dict(r) for r in self.q(
            """SELECT link.* FROM conflict_story_nodes link
            JOIN conflicts item ON item.id=link.conflict_id WHERE item.project_id=?""", (pid,)
        )]
        conflict_events=[dict(r) for r in self.q(
            """SELECT link.* FROM conflict_events link
            JOIN conflicts item ON item.id=link.conflict_id WHERE item.project_id=?""", (pid,)
        )]
        conflict_theme_positions=[dict(r) for r in self.q(
            """SELECT link.* FROM conflict_theme_positions link
            JOIN conflicts item ON item.id=link.conflict_id WHERE item.project_id=?""", (pid,)
        )]
        character_arcs=[dict(r) for r in self.q(
            "SELECT * FROM character_arcs WHERE project_id=? ORDER BY id", (pid,)
        )]
        character_arc_scenes=[dict(r) for r in self.q(
            """SELECT link.* FROM character_arc_scenes link
            JOIN character_arcs arc ON arc.id=link.arc_id WHERE arc.project_id=?""", (pid,)
        )]
        character_arc_story_nodes=[dict(r) for r in self.q(
            """SELECT link.* FROM character_arc_story_nodes link
            JOIN character_arcs arc ON arc.id=link.arc_id WHERE arc.project_id=?""", (pid,)
        )]
        character_arc_events=[dict(r) for r in self.q(
            """SELECT link.* FROM character_arc_events link
            JOIN character_arcs arc ON arc.id=link.arc_id WHERE arc.project_id=?""", (pid,)
        )]
        character_arc_conflicts=[dict(r) for r in self.q(
            """SELECT link.* FROM character_arc_conflicts link
            JOIN character_arcs arc ON arc.id=link.arc_id WHERE arc.project_id=?""", (pid,)
        )]
        hook_profile_row=self.one("SELECT * FROM hook_profiles WHERE project_id=?",(pid,))
        hook_profile=dict(hook_profile_row) if hook_profile_row else {}
        story_promises=[dict(r) for r in self.q(
            "SELECT * FROM story_promises WHERE project_id=? ORDER BY position,id", (pid,)
        )]
        story_promise_story_nodes=[dict(r) for r in self.q(
            """SELECT link.* FROM story_promise_story_nodes link
            JOIN story_promises item ON item.id=link.promise_id WHERE item.project_id=?""", (pid,)
        )]
        story_promise_scenes=[dict(r) for r in self.q(
            """SELECT link.* FROM story_promise_scenes link
            JOIN story_promises item ON item.id=link.promise_id WHERE item.project_id=?""", (pid,)
        )]
        story_moments=[dict(r) for r in self.q(
            "SELECT * FROM story_moments WHERE project_id=? ORDER BY position,id", (pid,)
        )]
        story_moment_story_nodes=[dict(r) for r in self.q(
            """SELECT link.* FROM story_moment_story_nodes link
            JOIN story_moments item ON item.id=link.moment_id WHERE item.project_id=?""", (pid,)
        )]
        story_moment_sequences=[dict(r) for r in self.q(
            """SELECT link.* FROM story_moment_sequences link
            JOIN story_moments item ON item.id=link.moment_id WHERE item.project_id=?""", (pid,)
        )]
        story_moment_scenes=[dict(r) for r in self.q(
            """SELECT link.* FROM story_moment_scenes link
            JOIN story_moments item ON item.id=link.moment_id WHERE item.project_id=?""", (pid,)
        )]
        story_moment_events=[dict(r) for r in self.q(
            """SELECT link.* FROM story_moment_events link
            JOIN story_moments item ON item.id=link.moment_id WHERE item.project_id=?""", (pid,)
        )]
        story_moment_conflicts=[dict(r) for r in self.q(
            """SELECT link.* FROM story_moment_conflicts link
            JOIN story_moments item ON item.id=link.moment_id WHERE item.project_id=?""", (pid,)
        )]
        world_rule_characters=[dict(r) for r in self.q(
            """SELECT link.* FROM world_rule_characters link JOIN world_rules rule ON rule.id=link.rule_id
            WHERE rule.project_id=?""", (pid,)
        )]
        world_rule_groups=[dict(r) for r in self.q(
            """SELECT link.* FROM world_rule_groups link JOIN world_rules rule ON rule.id=link.rule_id
            WHERE rule.project_id=?""", (pid,)
        )]
        world_rule_events=[dict(r) for r in self.q(
            """SELECT link.* FROM world_rule_events link JOIN world_rules rule ON rule.id=link.rule_id
            WHERE rule.project_id=?""", (pid,)
        )]
        world_rule_images=[dict(r) for r in self.q(
            """SELECT link.* FROM world_rule_images link JOIN world_rules rule ON rule.id=link.rule_id
            WHERE rule.project_id=?""", (pid,)
        )]
        relationship_maps=[dict(r) for r in self.q(
            "SELECT * FROM relationship_maps WHERE project_id=? ORDER BY id", (pid,)
        )]
        relationship_map_nodes=[dict(r) for r in self.q(
            """SELECT node.* FROM relationship_map_nodes node
            JOIN relationship_maps map_row ON map_row.id=node.map_id
            WHERE map_row.project_id=? ORDER BY node.map_id,node.character_id""",
            (pid,),
        )]
        relationships=[dict(r) for r in self.q("SELECT * FROM character_relationships WHERE project_id=? ORDER BY id",(pid,))]
        character_groups=[dict(r) for r in self.q("SELECT * FROM character_groups WHERE project_id=? ORDER BY id",(pid,))]
        character_group_members=[dict(r) for r in self.q(
            """SELECT member.* FROM character_group_members member
            JOIN character_groups group_row ON group_row.id=member.group_id WHERE group_row.project_id=?""",
            (pid,),
        )]
        character_references=[dict(r) for r in self.q(
            "SELECT * FROM character_references WHERE project_id=? ORDER BY id", (pid,)
        )]
        character_custom_fields=[dict(r) for r in self.q(
            """SELECT field.* FROM character_custom_fields field
            JOIN characters character ON character.id=field.character_id WHERE character.project_id=?
            ORDER BY field.character_id,field.position,field.id""",
            (pid,),
        )]
        form_templates=[dict(r) for r in self.q(
            """SELECT template.* FROM form_templates template
            JOIN project_form_templates assignment ON assignment.template_id=template.id
            WHERE assignment.project_id=? ORDER BY template.id""",
            (pid,),
        )]
        form_template_ids=[int(row["id"]) for row in form_templates]
        form_template_sections=[]
        form_template_fields=[]
        if form_template_ids:
            placeholders=",".join("?" * len(form_template_ids))
            form_template_sections=[dict(r) for r in self.q(
                f"SELECT * FROM form_template_sections WHERE template_id IN ({placeholders}) ORDER BY template_id,position,id",
                form_template_ids,
            )]
            form_template_fields=[dict(r) for r in self.q(
                f"SELECT * FROM form_template_fields WHERE template_id IN ({placeholders}) ORDER BY template_id,section_id,position,id",
                form_template_ids,
            )]
        project_form_templates=[dict(r) for r in self.q(
            "SELECT * FROM project_form_templates WHERE project_id=? ORDER BY target_type",
            (pid,),
        )]
        form_field_values=[dict(r) for r in self.q(
            "SELECT * FROM form_field_values WHERE project_id=? ORDER BY target_type,entity_id,field_id",
            (pid,),
        )]
        tags=[dict(r) for r in self.q(
            "SELECT * FROM tags WHERE project_id=? ORDER BY name COLLATE NOCASE", (pid,)
        )]
        tag_ids=[int(row["id"]) for row in tags]
        entity_tags=[]
        if tag_ids:
            placeholders=",".join("?" * len(tag_ids))
            entity_tags=[dict(r) for r in self.q(
                f"SELECT * FROM entity_tags WHERE tag_id IN ({placeholders}) ORDER BY tag_id,target_type,entity_id",
                tag_ids,
            )]
        scene_characters=[dict(r) for r in self.q(
            "SELECT link.* FROM scene_characters link JOIN scene_rows scene ON scene.id=link.scene_id WHERE scene.project_id=?",
            (pid,),
        )]
        scene_events=[dict(r) for r in self.q(
            """SELECT link.* FROM scene_events link JOIN scene_rows scene ON scene.id=link.scene_id
            WHERE scene.project_id=?""", (pid,)
        )]
        scene_story_nodes=[dict(r) for r in self.q(
            """SELECT link.* FROM scene_story_nodes link JOIN scene_rows scene ON scene.id=link.scene_id
            WHERE scene.project_id=?""", (pid,)
        )]
        scene_theme_positions=[dict(r) for r in self.q(
            """SELECT link.* FROM scene_theme_positions link JOIN scene_rows scene ON scene.id=link.scene_id
            WHERE scene.project_id=?""", (pid,)
        )]
        scene_theme_motifs=[dict(r) for r in self.q(
            """SELECT link.* FROM scene_theme_motifs link JOIN scene_rows scene ON scene.id=link.scene_id
            WHERE scene.project_id=?""", (pid,)
        )]
        map_characters=[dict(r) for r in self.q(
            "SELECT link.* FROM story_map_node_characters link JOIN story_map_nodes node ON node.id=link.node_id WHERE node.project_id=?",
            (pid,),
        )]
        timeline_tracks=[dict(r) for r in self.q(
            "SELECT * FROM timeline_tracks WHERE project_id=? ORDER BY position,id", (pid,)
        )]
        timeline_events=[dict(r) for r in self.q(
            "SELECT * FROM timeline_events WHERE project_id=? ORDER BY time_hours,id", (pid,)
        )]
        timeline_event_characters=[dict(r) for r in self.q(
            """SELECT link.* FROM timeline_event_characters link
            JOIN timeline_events event ON event.id=link.event_id WHERE event.project_id=?""",
            (pid,),
        )]
        script_meta_row=self.one("SELECT * FROM script_meta WHERE project_id=?",(pid,))
        script_meta=dict(script_meta_row) if script_meta_row else {}
        images=[dict(r) for r in self.q("SELECT * FROM image_library WHERE project_id=? ORDER BY id",(pid,))]
        locations=[dict(r) for r in self.q("SELECT * FROM locations WHERE project_id=? ORDER BY position,id",(pid,))]
        location_characters=[dict(r) for r in self.q(
            """SELECT link.* FROM location_characters link JOIN locations location ON location.id=link.location_id
            WHERE location.project_id=?""", (pid,)
        )]
        location_events=[dict(r) for r in self.q(
            """SELECT link.* FROM location_events link JOIN locations location ON location.id=link.location_id
            WHERE location.project_id=?""", (pid,)
        )]
        location_scenes=[dict(r) for r in self.q(
            """SELECT link.* FROM location_scenes link JOIN locations location ON location.id=link.location_id
            WHERE location.project_id=?""", (pid,)
        )]
        location_images=[dict(r) for r in self.q(
            """SELECT link.* FROM location_images link JOIN locations location ON location.id=link.location_id
            WHERE location.project_id=? ORDER BY link.location_id,link.position,link.image_id""", (pid,)
        )]
        versions=[dict(r) for r in self.q("SELECT * FROM doc_versions WHERE project_id=?",(pid,))]
        guided_runs=[dict(r) for r in self.q(
            "SELECT * FROM guided_runs WHERE project_id=? ORDER BY created_at,id",
            (pid,),
        )]
        guided_answers=[]
        guided_applications=[]
        guided_application_history=[]
        for run in guided_runs:
            guided_answers.extend(
                dict(row) for row in self.q(
                    "SELECT * FROM guided_answers WHERE run_id=? ORDER BY step_index",
                    (run["id"],),
                )
            )
            guided_applications.extend(
                dict(row) for row in self.q(
                    "SELECT * FROM guided_applications WHERE run_id=? ORDER BY updated_at,step_key",
                    (run["id"],),
                )
            )
            guided_application_history.extend(
                dict(row) for row in self.q(
                    """SELECT * FROM guided_application_history
                    WHERE run_id=? ORDER BY id""",
                    (run["id"],),
                )
            )
        for image in images:
            image["image_data"] = bytes(image["image_data"]).hex()
        for character in characters:
            portrait_data = character.get("portrait_data")
            character["portrait_data"] = bytes(portrait_data).hex() if portrait_data else ""
        for reference in character_references:
            reference["image_data"] = bytes(reference["image_data"]).hex()
        path.write_text(json.dumps({"format":"storyforge-project-v1","project":p,"docs":docs,"questions":qs,"story_map":story_map,"synopsis_answers":synopsis_answers,"story_map_nodes":map_nodes,"story_map_links":map_links,"sequence_blocks":sequence_blocks,"scene_rows":scene_rows,"outline_items":outline_items,"development_status":development_status,"characters":characters,"world_profile":world_profile,"world_rules":world_rules,"world_terms":world_terms,"theme_profile":theme_profile,"theme_positions":theme_positions,"theme_position_characters":theme_position_characters,"theme_motifs":theme_motifs,"theme_motif_locations":theme_motif_locations,"theme_motif_events":theme_motif_events,"theme_motif_images":theme_motif_images,"conflicts":conflicts,"conflict_characters":conflict_characters,"conflict_groups":conflict_groups,"conflict_scenes":conflict_scenes,"conflict_story_nodes":conflict_story_nodes,"conflict_events":conflict_events,"conflict_theme_positions":conflict_theme_positions,"character_arcs":character_arcs,"character_arc_scenes":character_arc_scenes,"character_arc_story_nodes":character_arc_story_nodes,"character_arc_events":character_arc_events,"character_arc_conflicts":character_arc_conflicts,"hook_profile":hook_profile,"story_promises":story_promises,"story_promise_story_nodes":story_promise_story_nodes,"story_promise_scenes":story_promise_scenes,"story_moments":story_moments,"story_moment_story_nodes":story_moment_story_nodes,"story_moment_sequences":story_moment_sequences,"story_moment_scenes":story_moment_scenes,"story_moment_events":story_moment_events,"story_moment_conflicts":story_moment_conflicts,"world_rule_characters":world_rule_characters,"world_rule_groups":world_rule_groups,"world_rule_events":world_rule_events,"world_rule_images":world_rule_images,"relationship_maps":relationship_maps,"relationship_map_nodes":relationship_map_nodes,"character_relationships":relationships,"character_groups":character_groups,"character_group_members":character_group_members,"character_references":character_references,"character_custom_fields":character_custom_fields,"form_templates":form_templates,"form_template_sections":form_template_sections,"form_template_fields":form_template_fields,"project_form_templates":project_form_templates,"form_field_values":form_field_values,"tags":tags,"entity_tags":entity_tags,"scene_characters":scene_characters,"scene_events":scene_events,"scene_story_nodes":scene_story_nodes,"scene_theme_positions":scene_theme_positions,"scene_theme_motifs":scene_theme_motifs,"story_map_node_characters":map_characters,"timeline_tracks":timeline_tracks,"timeline_events":timeline_events,"timeline_event_characters":timeline_event_characters,"script_meta":script_meta,"images":images,"locations":locations,"location_characters":location_characters,"location_events":location_events,"location_scenes":location_scenes,"location_images":location_images,"versions":versions,"guided_runs":guided_runs,"guided_answers":guided_answers,"guided_applications":guided_applications,"guided_application_history":guided_application_history},ensure_ascii=False,indent=2),encoding="utf-8")
    def import_project(self,path:Path):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get('project'), dict):
            raise ValueError('Projet StoryForge invalide')
        if data.get('format', 'storyforge-project-v1') != 'storyforge-project-v1':
            raise ValueError('Format de projet non pris en charge')
        if not isinstance(data['project'].get('title'), str):
            raise ValueError('Titre de projet invalide')
        for key, value in data.items():
            if key in {'format', 'project'}:
                continue
            if key in {'script_meta', 'world_profile', 'theme_profile', 'hook_profile'}:
                if value is not None and not isinstance(value, dict):
                    raise ValueError(f'Objet invalide : {key}')
            elif not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
                raise ValueError(f'Collection invalide : {key}')
        with self.transaction():
            return self._import_project_data(data)

    def _import_project_data(self, data):
        p = data['project']
        fields=["created_at","title","stage","protagonist","desire","objective","opposition","stakes","change_note","ending","current_document","main_problem","next_decision","open_questions","project_type","story_format","target_duration","start_mode","project_status","archived","updated_at"]
        defaults={
            "created_at": NOW(), "stage": "Idée", "project_type": "film", "story_format": "free",
            "target_duration": 0, "start_mode": "free", "project_status": "ongoing",
            "archived": 0, "updated_at": NOW(),
        }
        vals=[p.get(k,defaults.get(k,"")) for k in fields]
        cur=self.run(f"INSERT INTO projects({','.join(fields)}) VALUES({','.join('?'*len(fields))})",vals); pid=cur.lastrowid
        imported_docs = {}
        for d in data.get("docs",[]):
            self.run("INSERT OR REPLACE INTO project_docs(project_id,doc_type,title,content,updated_at) VALUES(?,?,?,?,?)",(pid,d.get("doc_type"),d.get("title",""),d.get("content",""),NOW()))
            imported = self.one(
                "SELECT id FROM project_docs WHERE project_id=? AND doc_type=?",
                (pid, d.get("doc_type")),
            )
            if imported:
                imported_docs[d.get("id")] = int(imported["id"])
        for q in data.get("questions",[]):
            self.run("INSERT OR REPLACE INTO project_questions(project_id,question_key,answer,updated_at) VALUES(?,?,?,?)",(pid,q.get("question_key"),q.get("answer",""),NOW()))
        for answer in data.get("story_map",[]):
            self.save_story_map_answer(pid, answer.get("step_key"), answer.get("answer", ""))
        for answer in data.get("synopsis_answers",[]):
            self.save_synopsis_answer(pid, answer.get("step_key"), answer.get("answer", ""))
        imported_nodes = {}
        for node in data.get("story_map_nodes", []):
            imported_nodes[node.get("id")] = self.create_story_map_node(
                pid,
                node.get("title", "Carte"),
                node.get("content", ""),
                node.get("kind", "idea"),
                node.get("x", 80),
                node.get("y", 80),
                node.get("source_step_key", ""),
            )
        for link in data.get("story_map_links", []):
            source_id = imported_nodes.get(link.get("source_id"))
            target_id = imported_nodes.get(link.get("target_id"))
            if source_id and target_id:
                self.create_story_map_link(pid, source_id, target_id)
        imported_sequences = {}
        for block in data.get("sequence_blocks", []):
            source_node_id = imported_nodes.get(block.get("source_node_id"), 0)
            imported_sequences[block.get("id")] = self.create_sequence_block(
                pid,
                block.get("position", 0),
                block.get("title", "Séquence sans titre"),
                block.get("purpose", ""),
                block.get("events", ""),
                block.get("consequence", ""),
                source_node_id,
            )
        imported_scenes = {}
        pending_scene_drivers = {}
        for scene in data.get("scene_rows", []):
            imported_scenes[scene.get("id")] = self.run(
                """INSERT INTO scene_rows(
                project_id,position,title,duration,objective,opposition,change_note,status,moment_label,
                character_objective,conflict_note,information_revealed,entry_state,exit_state,notes,
                source_sequence_id,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    pid,
                    scene.get("position", 0),
                    scene.get("title", ""),
                    scene.get("duration", 0),
                    scene.get("objective", ""),
                    scene.get("opposition", ""),
                    scene.get("change_note", ""),
                    scene.get("status", "idea"),
                    scene.get("moment_label", ""),
                    scene.get("character_objective", ""),
                    scene.get("conflict_note", ""),
                    scene.get("information_revealed", ""),
                    scene.get("entry_state", ""),
                    scene.get("exit_state", ""),
                    scene.get("notes", ""),
                    imported_sequences.get(scene.get("source_sequence_id"), 0),
                    NOW(),
                    NOW(),
                ),
            ).lastrowid
            pending_scene_drivers[scene.get("id")] = scene.get("driver_character_id")
        imported_outline = {}
        for item in data.get("outline_items", []):
            imported_outline[item.get("id")] = self.create_outline_item(
                pid,
                item.get("position", 0),
                item.get("item_type", "beat"),
                item.get("title", ""),
                item.get("summary", ""),
                item.get("function_note", ""),
                item.get("consequence", ""),
                None,
                item.get("collapsed", 0),
                imported_sequences.get(item.get("source_sequence_id"), 0),
                imported_scenes.get(item.get("source_scene_id"), 0),
                imported_nodes.get(item.get("source_node_id"), 0),
            )
        for item in data.get("outline_items", []):
            imported_id = imported_outline.get(item.get("id"))
            imported_parent = imported_outline.get(item.get("parent_id"))
            if imported_id and imported_parent:
                self.run(
                    "UPDATE outline_items SET parent_id=?,updated_at=? WHERE id=?",
                    (imported_parent, NOW(), imported_id),
                )
        imported_characters = {}
        for character in data.get("characters", []):
            try:
                portrait_data = bytes.fromhex(character.get("portrait_data", ""))
            except (TypeError, ValueError):
                portrait_data = b""
            imported_characters[character.get("id")] = self.run(
                """INSERT INTO characters(
                project_id,name,role,gender,story_function,desire,conflict,arc,notes,
                age,occupation,description,appearance,personality,objective,need,fear,weakness,wound,
                values_note,beliefs,contradictions,secrets,backstory,start_situation,end_situation,
                speaking_style,portrait_name,portrait_mime,portrait_data,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    pid,
                    character.get("name", ""),
                    character.get("role", ""),
                    character.get("gender", "unspecified"),
                    character.get("story_function", ""),
                    character.get("desire", ""),
                    character.get("conflict", ""),
                    character.get("arc", ""),
                    character.get("notes", ""),
                    character.get("age", ""),
                    character.get("occupation", ""),
                    character.get("description", ""),
                    character.get("appearance", ""),
                    character.get("personality", ""),
                    character.get("objective", ""),
                    character.get("need", ""),
                    character.get("fear", ""),
                    character.get("weakness", ""),
                    character.get("wound", ""),
                    character.get("values_note", ""),
                    character.get("beliefs", ""),
                    character.get("contradictions", ""),
                    character.get("secrets", ""),
                    character.get("backstory", ""),
                    character.get("start_situation", ""),
                    character.get("end_situation", ""),
                    character.get("speaking_style", ""),
                    character.get("portrait_name", ""),
                    character.get("portrait_mime", ""),
                    portrait_data or None,
                    NOW(),
                    NOW(),
                ),
            ).lastrowid
        world_profile = data.get("world_profile") or {}
        if world_profile:
            self.run(
                """INSERT OR REPLACE INTO world_profiles(
                project_id,epoch,places,society,culture,worldview,originality,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?)""",
                (
                    pid, world_profile.get("epoch", ""), world_profile.get("places", ""),
                    world_profile.get("society", ""), world_profile.get("culture", ""),
                    world_profile.get("worldview", ""), world_profile.get("originality", ""),
                    NOW(), NOW(),
                ),
            )
        imported_world_rules = {}
        for rule in data.get("world_rules", []):
            imported_world_rules[rule.get("id")] = self.run(
                """INSERT INTO world_rules(
                project_id,category,title,rule_text,scope,limitation,cost,exceptions,consequence,status,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    pid, rule.get("category", "Autre"), rule.get("title", ""),
                    rule.get("rule_text", ""), rule.get("scope", ""), rule.get("limitation", ""),
                    rule.get("cost", ""), rule.get("exceptions", ""), rule.get("consequence", ""),
                    rule.get("status", "draft"), NOW(), NOW(),
                ),
            ).lastrowid
        for term in data.get("world_terms", []):
            self.run(
                """INSERT INTO world_terms(
                project_id,category,term,definition,usage,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?)""",
                (
                    pid, term.get("category", "Autre"), term.get("term", ""),
                    term.get("definition", ""), term.get("usage", ""), NOW(), NOW(),
                ),
            )
        theme_profile = data.get("theme_profile") or {}
        if theme_profile:
            self.run(
                """INSERT OR REPLACE INTO theme_profiles(
                project_id,theme_word,central_question,personal_interest,avoid_message,
                opening_view,decisions_note,consequences_note,conflicts_note,ending_response,
                notes,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    pid,
                    theme_profile.get("theme_word", ""),
                    theme_profile.get("central_question", ""),
                    theme_profile.get("personal_interest", ""),
                    theme_profile.get("avoid_message", ""),
                    theme_profile.get("opening_view", ""),
                    theme_profile.get("decisions_note", ""),
                    theme_profile.get("consequences_note", ""),
                    theme_profile.get("conflicts_note", ""),
                    theme_profile.get("ending_response", ""),
                    theme_profile.get("notes", ""),
                    NOW(),
                    NOW(),
                ),
            )
        imported_theme_positions = {}
        for item in data.get("theme_positions", []):
            imported_theme_positions[item.get("id")] = self.run(
                """INSERT INTO theme_positions(
                project_id,position,position_type,label,stance,nuance,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?)""",
                (
                    pid,
                    item.get("position", 0),
                    item.get("position_type", "nuance"),
                    item.get("label", ""),
                    item.get("stance", ""),
                    item.get("nuance", ""),
                    NOW(),
                    NOW(),
                ),
            ).lastrowid
        for link in data.get("theme_position_characters", []):
            position_id = imported_theme_positions.get(link.get("position_id"))
            character_id = imported_characters.get(link.get("character_id"))
            if position_id and character_id:
                self.run(
                    "INSERT OR IGNORE INTO theme_position_characters(position_id,character_id) VALUES(?,?)",
                    (position_id, character_id),
                )
        imported_theme_motifs = {}
        for motif in data.get("theme_motifs", []):
            imported_theme_motifs[motif.get("id")] = self.run(
                """INSERT INTO theme_motifs(
                project_id,position,name,motif_type,meaning,appearances,evolution,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?)""",
                (
                    pid,
                    motif.get("position", 0),
                    motif.get("name", ""),
                    motif.get("motif_type", "Objet"),
                    motif.get("meaning", ""),
                    motif.get("appearances", ""),
                    motif.get("evolution", ""),
                    NOW(),
                    NOW(),
                ),
            ).lastrowid
        conflict_fields = (
            "position", "title", "importance", "nature",
            "side_a_label", "side_a_goal", "side_a_strategy", "side_a_advantage",
            "side_a_vulnerability", "side_a_loss", "side_b_label", "side_b_goal",
            "side_b_strategy", "side_b_advantage", "side_b_vulnerability", "side_b_loss",
            "incompatibility", "stakes", "trigger_note", "first_actions", "escalation",
            "closing_options", "difficult_choice", "decisive_confrontation", "outcome",
            "winner", "loser", "cost", "change_note", "notes",
        )
        conflict_defaults = {"position": 0, "importance": "secondary", "nature": "external"}
        imported_conflicts = {}
        for conflict in data.get("conflicts", []):
            imported_conflicts[conflict.get("id")] = self.run(
                f"INSERT INTO conflicts(project_id,{','.join(conflict_fields)},created_at,updated_at) "
                f"VALUES({','.join('?' * (len(conflict_fields) + 3))})",
                [pid]
                + [conflict.get(field, conflict_defaults.get(field, "")) for field in conflict_fields]
                + [NOW(), NOW()],
            ).lastrowid
        arc_fields = (
            "arc_type", "initial_belief", "main_trial", "pressures",
            "breaking_point", "decisive_choice", "cost", "visible_proof", "notes",
        )
        imported_character_arcs = {}
        for arc in data.get("character_arcs", []):
            character_id = imported_characters.get(arc.get("character_id"))
            if not character_id:
                continue
            imported_character_arcs[arc.get("id")] = self.run(
                f"INSERT INTO character_arcs(project_id,character_id,{','.join(arc_fields)},created_at,updated_at) "
                f"VALUES({','.join('?' * (len(arc_fields) + 4))})",
                [pid, character_id]
                + [arc.get(field, "") for field in arc_fields]
                + [NOW(), NOW()],
            ).lastrowid
        hook_profile = data.get("hook_profile") or {}
        if hook_profile:
            self.run(
                """INSERT OR REPLACE INTO hook_profiles(
                project_id,hook_question,unusual_situation,audience_question,withheld_answer,
                created_at,updated_at) VALUES(?,?,?,?,?,?,?)""",
                (
                    pid,
                    hook_profile.get("hook_question", ""),
                    hook_profile.get("unusual_situation", ""),
                    hook_profile.get("audience_question", ""),
                    hook_profile.get("withheld_answer", ""),
                    NOW(),
                    NOW(),
                ),
            )
        promise_fields = (
            "position", "promise_type", "title", "description",
            "planted_note", "development_note", "payoff_note", "status",
        )
        promise_defaults = {"position": 0, "promise_type": "Concept", "status": "À placer"}
        imported_story_promises = {}
        for promise in data.get("story_promises", []):
            imported_story_promises[promise.get("id")] = self.run(
                f"INSERT INTO story_promises(project_id,{','.join(promise_fields)},created_at,updated_at) "
                f"VALUES({','.join('?' * (len(promise_fields) + 3))})",
                [pid]
                + [promise.get(field, promise_defaults.get(field, "")) for field in promise_fields]
                + [NOW(), NOW()],
            ).lastrowid
        moment_fields = (
            "position", "moment_type", "title", "description",
            "narrative_function", "placement_note", "status",
        )
        moment_defaults = {"position": 0, "moment_type": "Moment fort", "status": "Idée"}
        imported_story_moments = {}
        for moment in data.get("story_moments", []):
            imported_story_moments[moment.get("id")] = self.run(
                f"INSERT INTO story_moments(project_id,{','.join(moment_fields)},created_at,updated_at) "
                f"VALUES({','.join('?' * (len(moment_fields) + 3))})",
                [pid]
                + [moment.get(field, moment_defaults.get(field, "")) for field in moment_fields]
                + [NOW(), NOW()],
            ).lastrowid
        imported_relationship_maps = {}
        for relationship_map in data.get("relationship_maps", []):
            imported_relationship_maps[relationship_map.get("id")] = self.run(
                """INSERT INTO relationship_maps(project_id,name,map_type,created_at,updated_at)
                VALUES(?,?,?,?,?)""",
                (
                    pid,
                    relationship_map.get("name", "Relations générales"),
                    relationship_map.get("map_type", "general"),
                    NOW(),
                    NOW(),
                ),
            ).lastrowid
        if imported_relationship_maps:
            default_relationship_map_id = next(iter(imported_relationship_maps.values()))
        else:
            default_relationship_map_id = int(self.ensure_relationship_map(pid)["id"])
        for node in data.get("relationship_map_nodes", []):
            map_id = imported_relationship_maps.get(node.get("map_id"))
            character_id = imported_characters.get(node.get("character_id"))
            if map_id and character_id:
                self.run(
                    """INSERT OR REPLACE INTO relationship_map_nodes(map_id,character_id,x,y)
                    VALUES(?,?,?,?)""",
                    (map_id, character_id, node.get("x", 100), node.get("y", 100)),
                )
        imported_character_groups = {}
        for group in data.get("character_groups", []):
            imported_character_groups[group.get("id")] = self.run(
                """INSERT INTO character_groups(
                project_id,name,group_type,description,color,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?)""",
                (
                    pid,
                    group.get("name", ""),
                    group.get("group_type", "Groupe"),
                    group.get("description", ""),
                    group.get("color", ""),
                    NOW(),
                    NOW(),
                ),
            ).lastrowid
        for member in data.get("character_group_members", []):
            group_id = imported_character_groups.get(member.get("group_id"))
            character_id = imported_characters.get(member.get("character_id"))
            if group_id and character_id:
                self.run(
                    """INSERT OR IGNORE INTO character_group_members(group_id,character_id,role_in_group)
                    VALUES(?,?,?)""",
                    (group_id, character_id, member.get("role_in_group", "")),
                )
        for reference in data.get("character_references", []):
            character_id = imported_characters.get(reference.get("character_id"))
            try:
                image_data = bytes.fromhex(reference.get("image_data", ""))
            except (TypeError, ValueError):
                image_data = b""
            if character_id and image_data:
                self.run(
                    """INSERT INTO character_references(
                    project_id,character_id,title,category,notes,file_name,mime_type,image_data,created_at,updated_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (
                        pid,
                        character_id,
                        reference.get("title", ""),
                        reference.get("category", "Référence"),
                        reference.get("notes", ""),
                        reference.get("file_name", ""),
                        reference.get("mime_type", "image/png"),
                        image_data,
                        NOW(),
                        NOW(),
                    ),
                )
        for field in data.get("character_custom_fields", []):
            character_id = imported_characters.get(field.get("character_id"))
            if character_id:
                self.run(
                    """INSERT INTO character_custom_fields(character_id,label,value,position)
                    VALUES(?,?,?,?)""",
                    (
                        character_id,
                        field.get("label", ""),
                        field.get("value", ""),
                        field.get("position", 0),
                    ),
                )
        for relationship in data.get("character_relationships", []):
            character_a = imported_characters.get(relationship.get("character_a_id"))
            character_b = imported_characters.get(relationship.get("character_b_id"))
            if character_a and character_b:
                relationship_map_id = imported_relationship_maps.get(
                    relationship.get("map_id"), default_relationship_map_id
                )
                self.run(
                    """INSERT INTO character_relationships(
                    project_id,map_id,character_a_id,character_b_id,relationship_type,
                    description,tension,secret,evolution,color,created_at,updated_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        pid, relationship_map_id, character_a, character_b,
                        relationship.get("relationship_type", "Autre"),
                        relationship.get("description", ""), relationship.get("tension", ""),
                        relationship.get("secret", ""), relationship.get("evolution", ""),
                        relationship.get("color", ""),
                        NOW(), NOW(),
                    ),
                )
        for presence in data.get("scene_characters", []):
            scene_id = imported_scenes.get(presence.get("scene_id"))
            character_id = imported_characters.get(presence.get("character_id"))
            if scene_id and character_id:
                self.run(
                    "INSERT OR IGNORE INTO scene_characters(scene_id,character_id) VALUES(?,?)",
                    (scene_id, character_id),
                )
        for original_scene_id, original_character_id in pending_scene_drivers.items():
            scene_id = imported_scenes.get(original_scene_id)
            character_id = imported_characters.get(original_character_id)
            if scene_id and character_id:
                self.run(
                    "UPDATE scene_rows SET driver_character_id=? WHERE id=?",
                    (character_id, scene_id),
                )
        for presence in data.get("story_map_node_characters", []):
            node_id = imported_nodes.get(presence.get("node_id"))
            character_id = imported_characters.get(presence.get("character_id"))
            if node_id and character_id:
                self.run(
                    "INSERT OR IGNORE INTO story_map_node_characters(node_id,character_id) VALUES(?,?)",
                    (node_id, character_id),
                )
        imported_timeline_tracks = {}
        for track in data.get("timeline_tracks", []):
            imported_timeline_tracks[track.get("id")] = self.run(
                """INSERT INTO timeline_tracks(project_id,name,color,position,created_at,updated_at)
                VALUES(?,?,?,?,?,?)""",
                (
                    pid,
                    track.get("name", "Intrigue principale"),
                    track.get("color", "#3D8EF7"),
                    track.get("position", 0),
                    NOW(),
                    NOW(),
                ),
            ).lastrowid
        imported_timeline_events = {}
        for event in data.get("timeline_events", []):
            track_id = imported_timeline_tracks.get(event.get("track_id"))
            if not track_id:
                legacy_track = self.ensure_timeline_track(
                    pid,
                    event.get("category", "Intrigue principale") or "Intrigue principale",
                )
                track_id = int(legacy_track["id"])
            imported_timeline_events[event.get("id")] = self.run(
                """INSERT INTO timeline_events(
                project_id,track_id,title,time_hours,display_label,category,description,place,consequence,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    pid,
                    track_id,
                    event.get("title", ""),
                    event.get("time_hours", 0),
                    event.get("display_label", ""),
                    event.get("category", "Intrigue principale"),
                    event.get("description", ""),
                    event.get("place", ""),
                    event.get("consequence", ""),
                    NOW(),
                    NOW(),
                ),
            ).lastrowid
        for presence in data.get("timeline_event_characters", []):
            event_id = imported_timeline_events.get(presence.get("event_id"))
            character_id = imported_characters.get(presence.get("character_id"))
            if event_id and character_id:
                self.run(
                    "INSERT OR IGNORE INTO timeline_event_characters(event_id,character_id) VALUES(?,?)",
                    (event_id, character_id),
                )
        meta = data.get("script_meta") or {}
        if meta:
            self.run(
                """INSERT OR REPLACE INTO script_meta(
                project_id,title,author,contact,draft_date,based_on,copyright_notice,
                include_title_page,document_json,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (
                    pid, meta.get("title", p.get("title", "")), meta.get("author", ""),
                    meta.get("contact", ""), meta.get("draft_date", ""),
                    meta.get("based_on", ""), meta.get("copyright_notice", ""),
                    int(meta.get("include_title_page", 1)), meta.get("document_json", ""), NOW(),
                ),
            )
        imported_images = {}
        for image in data.get("images", []):
            try:
                image_data = bytes.fromhex(image.get("image_data", ""))
            except ValueError:
                image_data = b""
            if image_data:
                imported_images[image.get("id")] = self.run(
                    """INSERT INTO image_library(
                    project_id,title,category,notes,file_name,mime_type,image_data,created_at,updated_at
                    ) VALUES(?,?,?,?,?,?,?,?,?)""",
                    (
                        pid,
                        image.get("title", ""),
                        image.get("category", "reference"),
                        image.get("notes", ""),
                        image.get("file_name", ""),
                        image.get("mime_type", "image/png"),
                        image_data,
                        NOW(),
                        NOW(),
                    ),
                ).lastrowid
        imported_locations = {}
        for location in data.get("locations", []):
            imported_locations[location.get("id")] = self.run(
                """INSERT INTO locations(
                project_id,position,name,category,region,epoch,tags,description,narrative_function,
                atmosphere,constraints_note,evolution,notes,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    pid,
                    location.get("position", 0),
                    location.get("name", ""),
                    location.get("category", "Autre"),
                    location.get("region", ""),
                    location.get("epoch", ""),
                    location.get("tags", ""),
                    location.get("description", ""),
                    location.get("narrative_function", ""),
                    location.get("atmosphere", ""),
                    location.get("constraints_note", ""),
                    location.get("evolution", ""),
                    location.get("notes", ""),
                    NOW(),
                    NOW(),
                ),
            ).lastrowid
        for link in data.get("location_characters", []):
            location_id = imported_locations.get(link.get("location_id"))
            character_id = imported_characters.get(link.get("character_id"))
            if location_id and character_id:
                self.run(
                    "INSERT OR IGNORE INTO location_characters(location_id,character_id) VALUES(?,?)",
                    (location_id, character_id),
                )
        for link in data.get("location_events", []):
            location_id = imported_locations.get(link.get("location_id"))
            event_id = imported_timeline_events.get(link.get("event_id"))
            if location_id and event_id:
                self.run(
                    "INSERT OR IGNORE INTO location_events(location_id,event_id) VALUES(?,?)",
                    (location_id, event_id),
                )
        for link in data.get("location_scenes", []):
            location_id = imported_locations.get(link.get("location_id"))
            scene_id = imported_scenes.get(link.get("scene_id"))
            if location_id and scene_id:
                self.run(
                    "INSERT OR IGNORE INTO location_scenes(location_id,scene_id) VALUES(?,?)",
                    (location_id, scene_id),
                )
        for link in data.get("location_images", []):
            location_id = imported_locations.get(link.get("location_id"))
            image_id = imported_images.get(link.get("image_id"))
            if location_id and image_id:
                self.run(
                    """INSERT OR IGNORE INTO location_images(location_id,image_id,position,is_primary)
                    VALUES(?,?,?,?)""",
                    (
                        location_id,
                        image_id,
                        link.get("position", 0),
                        1 if link.get("is_primary") else 0,
                    ),
                )
        for table, column, imported_targets in (
            ("scene_events", "event_id", imported_timeline_events),
            ("scene_story_nodes", "node_id", imported_nodes),
            ("scene_theme_positions", "position_id", imported_theme_positions),
            ("scene_theme_motifs", "motif_id", imported_theme_motifs),
        ):
            for link in data.get(table, []):
                scene_id = imported_scenes.get(link.get("scene_id"))
                target_id = imported_targets.get(link.get(column))
                if scene_id and target_id:
                    self.run(
                        f"INSERT OR IGNORE INTO {table}(scene_id,{column}) VALUES(?,?)",
                        (scene_id, target_id),
                    )
        theme_motif_link_specs = (
            ("theme_motif_locations", "location_id", imported_locations),
            ("theme_motif_events", "event_id", imported_timeline_events),
            ("theme_motif_images", "image_id", imported_images),
        )
        for table, column, imported_targets in theme_motif_link_specs:
            for link in data.get(table, []):
                motif_id = imported_theme_motifs.get(link.get("motif_id"))
                target_id = imported_targets.get(link.get(column))
                if motif_id and target_id:
                    self.run(
                        f"INSERT OR IGNORE INTO {table}(motif_id,{column}) VALUES(?,?)",
                        (motif_id, target_id),
                    )
        conflict_link_specs = (
            ("conflict_scenes", "scene_id", imported_scenes),
            ("conflict_story_nodes", "node_id", imported_nodes),
            ("conflict_events", "event_id", imported_timeline_events),
            ("conflict_theme_positions", "position_id", imported_theme_positions),
        )
        for table, column, imported_targets in conflict_link_specs:
            for link in data.get(table, []):
                conflict_id = imported_conflicts.get(link.get("conflict_id"))
                target_id = imported_targets.get(link.get(column))
                if conflict_id and target_id:
                    self.run(
                        f"INSERT OR IGNORE INTO {table}(conflict_id,{column}) VALUES(?,?)",
                        (conflict_id, target_id),
                    )
        for table, column, imported_targets in (
            ("conflict_characters", "character_id", imported_characters),
            ("conflict_groups", "group_id", imported_character_groups),
        ):
            for link in data.get(table, []):
                conflict_id = imported_conflicts.get(link.get("conflict_id"))
                target_id = imported_targets.get(link.get(column))
                if conflict_id and target_id:
                    self.run(
                        f"INSERT OR IGNORE INTO {table}(conflict_id,{column},side) VALUES(?,?,?)",
                        (conflict_id, target_id, link.get("side", "affected")),
                    )
        for table, column, imported_targets in (
            ("character_arc_scenes", "scene_id", imported_scenes),
            ("character_arc_story_nodes", "node_id", imported_nodes),
            ("character_arc_events", "event_id", imported_timeline_events),
            ("character_arc_conflicts", "conflict_id", imported_conflicts),
        ):
            for link in data.get(table, []):
                arc_id = imported_character_arcs.get(link.get("arc_id"))
                target_id = imported_targets.get(link.get(column))
                if arc_id and target_id:
                    self.run(
                        f"INSERT OR IGNORE INTO {table}(arc_id,{column}) VALUES(?,?)",
                        (arc_id, target_id),
                    )
        for table, column, imported_targets in (
            ("story_promise_story_nodes", "node_id", imported_nodes),
            ("story_promise_scenes", "scene_id", imported_scenes),
        ):
            for link in data.get(table, []):
                promise_id = imported_story_promises.get(link.get("promise_id"))
                target_id = imported_targets.get(link.get(column))
                if promise_id and target_id:
                    self.run(
                        f"INSERT OR IGNORE INTO {table}(promise_id,{column}) VALUES(?,?)",
                        (promise_id, target_id),
                    )
        for table, column, imported_targets in (
            ("story_moment_story_nodes", "node_id", imported_nodes),
            ("story_moment_sequences", "sequence_id", imported_sequences),
            ("story_moment_scenes", "scene_id", imported_scenes),
            ("story_moment_events", "event_id", imported_timeline_events),
            ("story_moment_conflicts", "conflict_id", imported_conflicts),
        ):
            for link in data.get(table, []):
                moment_id = imported_story_moments.get(link.get("moment_id"))
                target_id = imported_targets.get(link.get(column))
                if moment_id and target_id:
                    self.run(
                        f"INSERT OR IGNORE INTO {table}(moment_id,{column}) VALUES(?,?)",
                        (moment_id, target_id),
                    )
        for link in data.get("world_rule_characters", []):
            rule_id = imported_world_rules.get(link.get("rule_id"))
            character_id = imported_characters.get(link.get("character_id"))
            if rule_id and character_id:
                self.run("INSERT OR IGNORE INTO world_rule_characters(rule_id,character_id) VALUES(?,?)", (rule_id, character_id))
        for link in data.get("world_rule_groups", []):
            rule_id = imported_world_rules.get(link.get("rule_id"))
            group_id = imported_character_groups.get(link.get("group_id"))
            if rule_id and group_id:
                self.run("INSERT OR IGNORE INTO world_rule_groups(rule_id,group_id) VALUES(?,?)", (rule_id, group_id))
        for link in data.get("world_rule_events", []):
            rule_id = imported_world_rules.get(link.get("rule_id"))
            event_id = imported_timeline_events.get(link.get("event_id"))
            if rule_id and event_id:
                self.run("INSERT OR IGNORE INTO world_rule_events(rule_id,event_id) VALUES(?,?)", (rule_id, event_id))
        for link in data.get("world_rule_images", []):
            rule_id = imported_world_rules.get(link.get("rule_id"))
            image_id = imported_images.get(link.get("image_id"))
            if rule_id and image_id:
                self.run("INSERT OR IGNORE INTO world_rule_images(rule_id,image_id) VALUES(?,?)", (rule_id, image_id))
        imported_form_templates = {}
        for template in data.get("form_templates", []):
            imported_form_templates[template.get("id")] = self.run(
                """INSERT INTO form_templates(name,target_type,description,created_at,updated_at)
                VALUES(?,?,?,?,?)""",
                (
                    template.get("name", "Modèle importé"),
                    template.get("target_type", "character"),
                    template.get("description", ""),
                    NOW(),
                    NOW(),
                ),
            ).lastrowid
        imported_form_sections = {}
        for section in data.get("form_template_sections", []):
            template_id = imported_form_templates.get(section.get("template_id"))
            if template_id:
                imported_form_sections[section.get("id")] = self.run(
                    """INSERT INTO form_template_sections(template_id,title,position)
                    VALUES(?,?,?)""",
                    (
                        template_id,
                        section.get("title", "Section"),
                        section.get("position", 0),
                    ),
                ).lastrowid
        imported_form_fields = {}
        source_form_fields = {
            field.get("id"): field for field in data.get("form_template_fields", [])
        }
        for field in data.get("form_template_fields", []):
            template_id = imported_form_templates.get(field.get("template_id"))
            section_id = imported_form_sections.get(field.get("section_id"))
            if template_id and section_id:
                imported_form_fields[field.get("id")] = self.run(
                    """INSERT INTO form_template_fields(
                    template_id,section_id,label,field_type,options_json,help_text,
                    default_value,required,position) VALUES(?,?,?,?,?,?,?,?,?)""",
                    (
                        template_id,
                        section_id,
                        field.get("label", "Nouveau champ"),
                        field.get("field_type", "text_short"),
                        field.get("options_json", "[]"),
                        field.get("help_text", ""),
                        field.get("default_value", ""),
                        field.get("required", 0),
                        field.get("position", 0),
                    ),
                ).lastrowid
        for assignment in data.get("project_form_templates", []):
            template_id = imported_form_templates.get(assignment.get("template_id"))
            if template_id:
                self.run(
                    """INSERT OR REPLACE INTO project_form_templates(
                    project_id,target_type,template_id) VALUES(?,?,?)""",
                    (pid, assignment.get("target_type", "character"), template_id),
                )
        entity_maps = {
            "character": imported_characters,
            "location": imported_locations,
            "scene": imported_scenes,
            "event": imported_timeline_events,
            "faction": imported_character_groups,
            "document": imported_docs,
        }
        linked_value_maps = {
            "image": imported_images,
            "link_character": imported_characters,
            "link_scene": imported_scenes,
            "link_location": imported_locations,
        }
        for value in data.get("form_field_values", []):
            old_field_id = value.get("field_id")
            field_id = imported_form_fields.get(old_field_id)
            target_type = value.get("target_type", "character")
            if not field_id:
                continue
            if target_type in {"world", "theme"}:
                entity_id = pid
            else:
                entity_id = entity_maps.get(target_type, {}).get(
                    value.get("entity_id"), value.get("entity_id", 0)
                )
            value_text = value.get("value_text", "")
            field_type = source_form_fields.get(old_field_id, {}).get("field_type", "")
            value_map = linked_value_maps.get(field_type)
            if value_map and str(value_text).isdigit():
                value_text = str(value_map.get(int(value_text), ""))
            self.run(
                """INSERT OR REPLACE INTO form_field_values(
                project_id,target_type,entity_id,field_id,value_text,updated_at)
                VALUES(?,?,?,?,?,?)""",
                (pid, target_type, int(entity_id or 0), field_id, value_text, NOW()),
            )
        imported_tags = {}
        for tag in data.get("tags", []):
            self.run(
                """INSERT INTO tags(project_id,name,color,created_at,updated_at)
                VALUES(?,?,?,?,?) ON CONFLICT(project_id,name)
                DO UPDATE SET color=excluded.color,updated_at=excluded.updated_at""",
                (
                    pid,
                    tag.get("name", "Tag"),
                    tag.get("color", "#D84A32"),
                    NOW(),
                    NOW(),
                ),
            )
            row = self.one(
                "SELECT id FROM tags WHERE project_id=? AND name=? COLLATE NOCASE",
                (pid, tag.get("name", "Tag")),
            )
            if row:
                imported_tags[tag.get("id")] = int(row["id"])
        tag_entity_maps = {
            "character": imported_characters,
            "location": imported_locations,
            "scene": imported_scenes,
            "event": imported_timeline_events,
            "story_node": imported_nodes,
            "sequence": imported_sequences,
            "image": imported_images,
            "conflict": imported_conflicts,
            "faction": imported_character_groups,
            "document": imported_docs,
        }
        for link in data.get("entity_tags", []):
            tag_id = imported_tags.get(link.get("tag_id"))
            target_type = link.get("target_type", "")
            if target_type in {"world", "theme", "project"}:
                entity_id = pid
            else:
                entity_id = tag_entity_maps.get(target_type, {}).get(link.get("entity_id"))
            if tag_id and entity_id:
                self.run(
                    """INSERT OR IGNORE INTO entity_tags(tag_id,target_type,entity_id)
                    VALUES(?,?,?)""",
                    (tag_id, target_type, entity_id),
                )
        for version in data.get('versions', []):
            self.snapshot(pid, version['doc_type'], version.get('content', ''),
                          version.get('label'), version.get('snapshot_json', ''))
        imported_runs = {}
        for run in data.get("guided_runs", []):
            imported_run_id = self.create_guided_run(
                run.get("guide_key", "seed"),
                run.get("title", "Guide importé"),
                project_id=pid,
                assistance_level=run.get("assistance_level", "discovery"),
            )
            imported_runs[run.get("id")] = imported_run_id
            self.update_guided_run(
                imported_run_id,
                current_step=run.get("current_step", 0),
                status=run.get("status", "ongoing"),
                applied_at=run.get("applied_at", ""),
                applied_target_id=imported_scenes.get(run.get("applied_target_id"), 0),
            )
        for answer in data.get("guided_answers", []):
            imported_run_id = imported_runs.get(answer.get("run_id"))
            if imported_run_id:
                self.save_guided_answer(
                    imported_run_id,
                    answer.get("step_key", ""),
                    answer.get("step_index", 0),
                    answer.get("answer", ""),
                    answer.get("status", "draft"),
                )
        application_target_maps = {
            "character": imported_characters,
            "scene": imported_scenes,
            "conflict": imported_conflicts,
            "story_node": imported_nodes,
            "promise": imported_story_promises,
            "outline_item": imported_outline,
        }
        for application in data.get("guided_applications", []):
            imported_run_id = imported_runs.get(application.get("run_id"))
            if not imported_run_id:
                continue
            target_type = application.get("target_type", "")
            old_target_id = application.get("target_id", 0)
            target_id = application_target_maps.get(target_type, {}).get(old_target_id, 0)
            self.save_guided_application(
                imported_run_id,
                application.get("step_key", ""),
                pid,
                target_type,
                target_id,
                application.get("target_field", ""),
                application.get("status", "en pratique"),
                application.get("evidence", ""),
            )
        for event in data.get("guided_application_history", []):
            imported_run_id = imported_runs.get(event.get("run_id"))
            if not imported_run_id:
                continue
            target_type = event.get("target_type", "")
            old_target_id = event.get("target_id", 0)
            target_id = application_target_maps.get(target_type, {}).get(old_target_id, 0)
            self.record_guided_application_event(
                imported_run_id,
                event.get("step_key", ""),
                pid,
                target_type,
                target_id,
                event.get("target_field", ""),
                event.get("event_kind", "legacy"),
                event.get("status", "en pratique"),
                event.get("evidence", ""),
                event.get("occurred_at", ""),
            )
        imported_statuses = data.get("development_status", [])
        for state in imported_statuses:
            self.run(
                "INSERT OR REPLACE INTO development_status(project_id,doc_type,status,updated_at) VALUES(?,?,?,?)",
                (pid, state.get("doc_type", ""), state.get("status", "draft"), NOW()),
            )
        if not imported_statuses:
            for document in data.get("docs", []):
                if document.get("doc_type") != "story_map" and document.get("content", "").strip():
                    self.run(
                        "INSERT OR IGNORE INTO development_status(project_id,doc_type,status,updated_at) VALUES(?,?,?,?)",
                        (pid, document.get("doc_type", ""), "complete", NOW()),
                    )
            if data.get("story_map_nodes") or len(data.get("story_map", [])) >= 9:
                self.run(
                    "INSERT OR IGNORE INTO development_status(project_id,doc_type,status,updated_at) VALUES(?,?,?,?)",
                    (pid, "story_map", "complete", NOW()),
                )
            if data.get("sequence_blocks"):
                self.run(
                    "INSERT OR IGNORE INTO development_status(project_id,doc_type,status,updated_at) VALUES(?,?,?,?)",
                    (pid, "outline", "complete", NOW()),
                )
            if data.get("scene_rows"):
                self.run(
                    "INSERT OR IGNORE INTO development_status(project_id,doc_type,status,updated_at) VALUES(?,?,?,?)",
                    (pid, "scenes", "complete", NOW()),
                )
        return pid
