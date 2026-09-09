import json
import sqlite3

import pytest

from db import Database, NOW
from screenplay_model import ScreenplayDocument


@pytest.fixture
def db(tmp_path):
    database = Database(tmp_path / 'test.db')
    yield database
    database.conn.close()


def project(db):
    return db.run('INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)', (NOW(), 'Test', 'Idée')).lastrowid


def test_import_failure_rolls_back_all_writes(db, tmp_path, monkeypatch):
    pid = project(db)
    path = tmp_path / 'project.json'
    db.export_project(pid, path)
    data = json.loads(path.read_text())
    data['guided_runs'] = [{'guide_key': 'seed', 'title': 'Test'}]
    path.write_text(json.dumps(data))
    def fail(*args, **kwargs):
        raise RuntimeError('late failure')
    monkeypatch.setattr(db, 'create_guided_run', fail)
    with pytest.raises(RuntimeError):
        db.import_project(path)
    assert db.one('SELECT COUNT(*) FROM projects')[0] == 1
    assert not db.conn.in_transaction


def test_unknown_import_format_rejected(db, tmp_path):
    path = tmp_path / 'bad.json'
    path.write_text(json.dumps({'format': 'future', 'project': {'title': 'Test'}}))
    with pytest.raises(ValueError):
        db.import_project(path)
    assert db.one('SELECT COUNT(*) FROM projects')[0] == 0


def test_save_failure_preserves_text_structure_and_title(db):
    pid = project(db)
    old = ScreenplayDocument.from_legacy_text('INT. HALL - JOUR', project_id=pid)
    db.save_screenplay(pid, old.to_json(), title_meta={'author': 'Mina'})
    db.conn.execute("CREATE TEMP TRIGGER fail_meta BEFORE UPDATE ON script_meta BEGIN SELECT RAISE(ABORT, 'failure'); END")
    new = ScreenplayDocument.from_legacy_text('EXT. RUE - NUIT', project_id=pid)
    with pytest.raises(sqlite3.IntegrityError):
        db.save_screenplay(pid, new.to_json())
    assert db.one('SELECT content FROM project_docs WHERE project_id=?', (pid,))[0] == old.to_plain_text()
    assert db.one('SELECT document_json FROM script_meta WHERE project_id=?', (pid,))[0] == old.to_json()


def test_structured_version_restore_and_archive(db, tmp_path):
    pid = project(db)
    old = ScreenplayDocument.from_legacy_text('INT. HALL - JOUR\n\nMINA\nBonjour.', project_id=pid)
    db.save_screenplay(pid, old.to_json(), title_meta={'author': 'Mina', 'title': 'Original'})
    version = db.snapshot_screenplay(pid)
    new = ScreenplayDocument.from_legacy_text('EXT. RUE - NUIT', project_id=pid)
    db.save_screenplay(pid, new.to_json(), title_meta={'author': 'Sarah'})
    db.restore_screenplay_version(pid, version)
    assert db.one('SELECT document_json FROM script_meta WHERE project_id=?', (pid,))[0] == old.to_json()
    assert db.one('SELECT author FROM script_meta WHERE project_id=?', (pid,))[0] == 'Mina'
    assert db.one('SELECT COUNT(*) FROM doc_versions WHERE project_id=?', (pid,))[0] == 2
    path = tmp_path / 'export.json'
    db.export_project(pid, path)
    imported = db.import_project(path)
    imported_version = db.one('SELECT id FROM doc_versions WHERE project_id=? ORDER BY id', (imported,))[0]
    db.restore_screenplay_version(imported, imported_version)
    assert db.one('SELECT document_json FROM script_meta WHERE project_id=?', (imported,))[0] == old.to_json()
    with pytest.raises(ValueError):
        db.restore_screenplay_version(imported, version)


def test_nested_transaction_rollback(db):
    with pytest.raises(RuntimeError):
        with db.transaction():
            project(db)
            with db.transaction():
                project(db)
            raise RuntimeError()
    assert db.one('SELECT COUNT(*) FROM projects')[0] == 0


def test_failed_restore_preserves_current_document_and_version_count(db):
    pid = project(db)
    old = ScreenplayDocument.from_legacy_text('INT. HALL - JOUR', project_id=pid)
    db.save_screenplay(pid, old.to_json())
    version = db.snapshot_screenplay(pid)
    current = ScreenplayDocument.from_legacy_text('EXT. RUE - NUIT', project_id=pid)
    db.save_screenplay(pid, current.to_json())
    db.conn.execute("CREATE TEMP TRIGGER fail_restore BEFORE UPDATE ON script_meta BEGIN SELECT RAISE(ABORT, 'failure'); END")
    with pytest.raises(sqlite3.IntegrityError):
        db.restore_screenplay_version(pid, version)
    assert db.one('SELECT COUNT(*) FROM doc_versions')[0] == 1
    assert db.one('SELECT content FROM project_docs')[0] == current.to_plain_text()


def test_legacy_version_and_additive_migration(tmp_path):
    path = tmp_path / 'legacy.db'
    conn = sqlite3.connect(path)
    conn.execute('CREATE TABLE doc_versions(id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, doc_type TEXT NOT NULL, label TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL)')
    conn.commit()
    conn.close()
    db = Database(path)
    backups = list((tmp_path / 'backups').glob('*before_structured_versions*.db'))
    assert len(backups) == 1
    original = sqlite3.connect(backups[0])
    assert 'snapshot_json' not in {row[1] for row in original.execute('PRAGMA table_info(doc_versions)')}
    original.close()
    pid = project(db)
    version = db.snapshot(pid, 'script', 'INT. HALL - JOUR')
    db.restore_screenplay_version(pid, version)
    assert db.one('SELECT content FROM project_docs')[0] == 'INT. HALL - JOUR'
    assert db.one('SELECT snapshot_json FROM doc_versions WHERE id=?', (version,))[0] == ''
    db.conn.close()


def test_connected_learning_history_migration_is_backed_up_and_restorable(tmp_path):
    path = tmp_path / 'learning.db'
    db = Database(path)
    pid = project(db)
    run_id = db.create_guided_run('seed', 'Guide', project_id=pid)
    db.save_guided_application(
        run_id, 'idea', pid, 'project', 0, 'premise', 'en pratique', 'Une piste'
    )
    db.run('DROP TABLE guided_application_history')
    db.conn.close()

    migrated = Database(path)
    backups = list((tmp_path / 'backups').glob('*before_connected_learning_history*.db'))
    assert len(backups) == 1
    original = sqlite3.connect(backups[0])
    assert 'guided_application_history' not in {
        row[0] for row in original.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    original.close()
    history = migrated.guided_application_history(run_id, 'idea')
    assert len(history) == 1
    assert history[0]['event_kind'] == 'legacy'
    assert history[0]['evidence'] == 'Une piste'
    migrated.conn.close()


def test_geography_migration_is_backed_up_and_restorable(tmp_path):
    path = tmp_path / 'world.db'
    db = Database(path)
    project(db)
    db.run('DROP TABLE geography_markers')
    db.run('DROP TABLE geography_maps')
    db.conn.close()

    migrated = Database(path)
    backups = list((tmp_path / 'backups').glob('*before_geography_maps*.db'))
    assert len(backups) == 1
    original = sqlite3.connect(backups[0])
    old_tables = {
        row[0] for row in original.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    assert 'geography_maps' not in old_tables
    assert 'geography_markers' not in old_tables
    original.close()
    new_tables = {
        row[0] for row in migrated.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    assert {'geography_maps', 'geography_markers'} <= new_tables
    migrated.conn.close()
