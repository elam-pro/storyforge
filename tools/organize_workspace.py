from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1]
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from storyforge.runtime_paths import (
    RuntimePaths,
    migrate_legacy_database,
    prepare_runtime_directories,
    resolve_runtime_paths,
)


@dataclass
class OrganizationReport:
    migrated_database: bool = False
    moved: list[tuple[Path, Path]] = field(default_factory=list)
    removed_caches: list[Path] = field(default_factory=list)


def _digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def _available_destination(destination: Path) -> Path:
    if not destination.exists():
        return destination
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # noqa: DTZ005
    return destination.with_name(f"{destination.stem}_{stamp}{destination.suffix}")


def _move_verified(source: Path, destination: Path) -> Path:
    destination = _available_destination(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.moving-{os.getpid()}")
    shutil.copy2(source, temporary)
    if source.stat().st_size != temporary.stat().st_size or _digest(source) != _digest(temporary):
        temporary.unlink(missing_ok=True)
        raise OSError(f"Échec de vérification pendant le déplacement de {source}")
    temporary.replace(destination)
    source.unlink()
    return destination


def organize_workspace(
    source_root: Path,
    paths: RuntimePaths,
    *,
    remove_caches: bool = True,
) -> OrganizationReport:
    """Relocate legacy runtime files after verified copies; keep development envs."""

    root = Path(source_root).resolve()
    report = OrganizationReport()
    prepare_runtime_directories(paths)
    legacy_database = root / "storyforge.db"
    if legacy_database.exists():
        if paths.database.exists():
            raise FileExistsError(
                "La nouvelle base existe déjà. Le déplacement de l’ancienne base est refusé "
                "pour éviter un écrasement ambigu."
            )
        report.migrated_database = migrate_legacy_database(root, paths)
        if not report.migrated_database:
            raise OSError("La base historique n’a pas pu être copiée.")
        archived = paths.backups / "legacy_repository_storyforge.db"
        report.moved.append((legacy_database, _move_verified(legacy_database, archived)))

    legacy_backups = root / "backups"
    if legacy_backups.is_dir():
        for source in sorted(legacy_backups.iterdir()):
            if source.is_file():
                destination = _move_verified(source, paths.backups / source.name)
                report.moved.append((source, destination))
        if not any(legacy_backups.iterdir()):
            legacy_backups.rmdir()

    legacy_output = root / "output"
    if legacy_output.is_dir():
        for source in sorted(path for path in legacy_output.rglob("*") if path.is_file()):
            relative = source.relative_to(legacy_output)
            destination = _move_verified(source, paths.exports / "Anciens exports" / relative)
            report.moved.append((source, destination))
        for directory in sorted(
            (path for path in legacy_output.rglob("*") if path.is_dir()),
            key=lambda path: len(path.parts),
            reverse=True,
        ):
            if not any(directory.iterdir()):
                directory.rmdir()
        if not any(legacy_output.iterdir()):
            legacy_output.rmdir()

    manual = root / "Mon manuel d’écriture & storytelling.pdf"
    if manual.is_file():
        destination = _move_verified(manual, paths.exports / "Manuels" / manual.name)
        report.moved.append((manual, destination))

    if remove_caches:
        cache_paths = [
            root / ".pytest_cache",
            root / ".ruff_cache",
            root / "__pycache__",
            root / "build",
            root / "tmp",
            root / "storyforge" / "__pycache__",
            root / "storyforge_context" / "__pycache__",
            root / "tests" / "__pycache__",
            root / "tools" / "__pycache__",
            root / "packaging" / "linux" / "__pycache__",
        ]
        for cache_path in cache_paths:
            if cache_path.is_dir():
                shutil.rmtree(cache_path)
                report.removed_caches.append(cache_path)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Ranger les anciennes données hors du dépôt StoryForge.")
    parser.add_argument("--source-root", type=Path, default=SOURCE_ROOT)
    parser.add_argument("--apply", action="store_true", help="Effectuer les déplacements vérifiés.")
    arguments = parser.parse_args()
    paths = resolve_runtime_paths()
    if not arguments.apply:
        print(f"Base cible : {paths.database}")
        print(f"Sauvegardes : {paths.backups}")
        print(f"Exports : {paths.exports}")
        print("Relancer avec --apply après avoir fermé StoryForge.")
        return 0
    report = organize_workspace(arguments.source_root, paths)
    print(f"Base migrée : {'oui' if report.migrated_database else 'déjà absente du dépôt'}")
    print(f"Fichiers déplacés et vérifiés : {len(report.moved)}")
    print(f"Caches supprimés : {len(report.removed_caches)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
