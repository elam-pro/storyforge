import sqlite3
from pathlib import Path

from storyforge.runtime_paths import resolve_runtime_paths
from tools.organize_workspace import organize_workspace


def test_workspace_organization_moves_verified_runtime_files(tmp_path: Path) -> None:
    source = tmp_path / "repository"
    source.mkdir()
    database = source / "storyforge.db"
    connection = sqlite3.connect(database)
    connection.execute("CREATE TABLE projects(title TEXT)")
    connection.execute("INSERT INTO projects VALUES('Projet sûr')")
    connection.commit()
    connection.close()
    (source / "backups").mkdir()
    (source / "backups" / "old.db").write_bytes(b"old backup")
    (source / "output" / "pdf").mkdir(parents=True)
    (source / "output" / "pdf" / "report.pdf").write_bytes(b"%PDF-test")
    (source / "tmp").mkdir()
    (source / "tmp" / "cache.bin").write_bytes(b"cache")
    (source / "build").mkdir()
    (source / "build" / "generated.bin").write_bytes(b"generated")

    paths = resolve_runtime_paths({}, tmp_path / "home")
    report = organize_workspace(source, paths)

    assert report.migrated_database
    assert not database.exists()
    assert not (source / "backups").exists()
    assert not (source / "output").exists()
    assert not (source / "tmp").exists()
    assert not (source / "build").exists()
    assert (paths.backups / "legacy_repository_storyforge.db").is_file()
    assert (paths.backups / "old.db").read_bytes() == b"old backup"
    assert (paths.exports / "Anciens exports" / "pdf" / "report.pdf").is_file()
    restored = sqlite3.connect(paths.database)
    assert restored.execute("SELECT title FROM projects").fetchone()[0] == "Projet sûr"
    restored.close()


def test_workspace_organization_refuses_ambiguous_database(tmp_path: Path) -> None:
    source = tmp_path / "repository"
    source.mkdir()
    (source / "storyforge.db").write_bytes(b"legacy")
    paths = resolve_runtime_paths({}, tmp_path / "home")
    paths.database.parent.mkdir(parents=True)
    paths.database.write_bytes(b"existing")
    try:
        organize_workspace(source, paths, remove_caches=False)
    except FileExistsError:
        pass
    else:
        raise AssertionError("An ambiguous database must never be moved")
    assert (source / "storyforge.db").read_bytes() == b"legacy"
    assert paths.database.read_bytes() == b"existing"
