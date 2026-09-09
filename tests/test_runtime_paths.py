import sqlite3
from pathlib import Path

from storyforge.runtime_paths import copy_sqlite_database, resolve_runtime_paths


def test_runtime_paths_follow_xdg_and_explicit_overrides(tmp_path: Path) -> None:
    home = tmp_path / "home"
    paths = resolve_runtime_paths(
        {
            "XDG_DATA_HOME": str(tmp_path / "data"),
            "XDG_CONFIG_HOME": str(tmp_path / "config"),
            "XDG_CACHE_HOME": str(tmp_path / "cache"),
            "STORYFORGE_EXPORT_DIR": str(tmp_path / "exports"),
        },
        home,
    )
    assert paths.database == tmp_path / "data" / "storyforge" / "storyforge.db"
    assert paths.backups == tmp_path / "data" / "storyforge" / "backups"
    assert paths.config == tmp_path / "config" / "storyforge"
    assert paths.cache == tmp_path / "cache" / "storyforge"
    assert paths.exports == tmp_path / "exports"

    overridden = resolve_runtime_paths(
        {"STORYFORGE_DB_PATH": str(tmp_path / "custom.db")},
        home,
    )
    assert overridden.database == tmp_path / "custom.db"
    assert overridden.backups == tmp_path / "backups"


def test_sqlite_copy_is_atomic_and_never_overwrites(tmp_path: Path) -> None:
    source = tmp_path / "legacy.db"
    connection = sqlite3.connect(source)
    connection.execute("CREATE TABLE stories(title TEXT)")
    connection.execute("INSERT INTO stories VALUES('Originale')")
    connection.commit()
    connection.close()

    destination = tmp_path / "data" / "storyforge.db"
    assert copy_sqlite_database(source, destination)
    assert source.exists()
    copied = sqlite3.connect(destination)
    assert copied.execute("SELECT title FROM stories").fetchone()[0] == "Originale"
    copied.close()

    connection = sqlite3.connect(source)
    connection.execute("INSERT INTO stories VALUES('Nouvelle')")
    connection.commit()
    connection.close()
    assert not copy_sqlite_database(source, destination)
    copied = sqlite3.connect(destination)
    assert copied.execute("SELECT COUNT(*) FROM stories").fetchone()[0] == 1
    copied.close()
