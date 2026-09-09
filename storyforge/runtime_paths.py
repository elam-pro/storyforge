from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


APP_DIR_NAME = "storyforge"


@dataclass(frozen=True)
class RuntimePaths:
    data: Path
    config: Path
    cache: Path
    exports: Path
    database: Path
    backups: Path


def _path_from_env(environ: Mapping[str, str], key: str, fallback: Path) -> Path:
    value = environ.get(key, "").strip()
    return Path(value).expanduser() if value else fallback


def resolve_runtime_paths(
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> RuntimePaths:
    """Resolve Linux user directories without creating or migrating anything."""

    values = os.environ if environ is None else environ
    user_home = Path.home() if home is None else Path(home)
    data_root = _path_from_env(values, "XDG_DATA_HOME", user_home / ".local" / "share")
    config_root = _path_from_env(values, "XDG_CONFIG_HOME", user_home / ".config")
    cache_root = _path_from_env(values, "XDG_CACHE_HOME", user_home / ".cache")
    data_dir = _path_from_env(values, "STORYFORGE_DATA_DIR", data_root / APP_DIR_NAME)
    export_dir = _path_from_env(
        values,
        "STORYFORGE_EXPORT_DIR",
        user_home / "Documents" / "StoryForge",
    )
    database = _path_from_env(
        values,
        "STORYFORGE_DB_PATH",
        data_dir / "storyforge.db",
    )
    return RuntimePaths(
        data=data_dir,
        config=config_root / APP_DIR_NAME,
        cache=cache_root / APP_DIR_NAME,
        exports=export_dir,
        database=database,
        backups=database.parent / "backups",
    )


def prepare_runtime_directories(paths: RuntimePaths) -> None:
    """Create only the directories owned by the installed application."""

    for directory in {
        paths.data,
        paths.config,
        paths.cache,
        paths.exports,
        paths.database.parent,
        paths.backups,
    }:
        directory.mkdir(parents=True, exist_ok=True)


def copy_sqlite_database(source: Path, destination: Path) -> bool:
    """Copy a SQLite database atomically, preserving the source as rollback."""

    source = Path(source)
    destination = Path(destination)
    if destination.exists() or not source.is_file() or source.resolve() == destination.resolve():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.migrating-{os.getpid()}")
    if temporary.exists():
        temporary.unlink()
    source_connection: sqlite3.Connection | None = None
    destination_connection: sqlite3.Connection | None = None
    try:
        source_connection = sqlite3.connect(source)
        destination_connection = sqlite3.connect(temporary)
        source_connection.backup(destination_connection)
        check = destination_connection.execute("PRAGMA integrity_check").fetchone()
        if not check or check[0] != "ok":
            raise sqlite3.DatabaseError("La copie SQLite n’a pas passé le contrôle d’intégrité.")
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    finally:
        if destination_connection is not None:
            destination_connection.close()
        if source_connection is not None:
            source_connection.close()
    temporary.replace(destination)
    return True


def migrate_legacy_database(legacy_root: Path, paths: RuntimePaths) -> bool:
    """Copy the former repository database once; never delete the original."""

    prepare_runtime_directories(paths)
    return copy_sqlite_database(Path(legacy_root) / "storyforge.db", paths.database)
