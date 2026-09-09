from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from storyforge.runtime_paths import migrate_legacy_database, resolve_runtime_paths


def _atomic_copy(source: Path, destination: Path, mode: int | None = None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.installing-{os.getpid()}")
    shutil.copy2(source, temporary)
    if mode is not None:
        temporary.chmod(mode)
    temporary.replace(destination)


def install_application(
    source_root: Path,
    executable: Path,
    home: Path | None = None,
    legacy_root: Path | None = None,
) -> dict[str, Path]:
    source_root = Path(source_root).resolve()
    executable = Path(executable).resolve()
    user_home = Path.home() if home is None else Path(home)
    if not executable.is_file():
        raise FileNotFoundError(f"Exécutable introuvable : {executable}")

    target_dir = user_home / ".local" / "lib" / "storyforge"
    target_executable = target_dir / "StoryForge"
    command_path = user_home / ".local" / "bin" / "storyforge"
    applications_dir = user_home / ".local" / "share" / "applications"
    desktop_path = applications_dir / "storyforge.desktop"
    icon_path = user_home / ".local" / "share" / "icons" / "hicolor" / "scalable" / "apps" / "storyforge.svg"

    _atomic_copy(executable, target_executable, 0o755)
    _atomic_copy(source_root / "storyforge" / "resources" / "storyforge.svg", icon_path, 0o644)

    command_path.parent.mkdir(parents=True, exist_ok=True)
    if command_path.exists() and not command_path.is_symlink():
        raise FileExistsError(f"Le chemin existe déjà et n’est pas un lien StoryForge : {command_path}")
    command_path.unlink(missing_ok=True)
    command_path.symlink_to(target_executable)

    template = (source_root / "packaging" / "linux" / "storyforge.desktop.in").read_text(encoding="utf-8")
    desktop_text = template.replace("@EXECUTABLE@", str(target_executable))
    applications_dir.mkdir(parents=True, exist_ok=True)
    temporary_desktop = desktop_path.with_name(f".{desktop_path.name}.installing-{os.getpid()}")
    temporary_desktop.write_text(desktop_text, encoding="utf-8")
    temporary_desktop.chmod(0o644)
    temporary_desktop.replace(desktop_path)

    paths = resolve_runtime_paths(environ={} if home is not None else None, home=user_home)
    migrate_legacy_database(source_root if legacy_root is None else legacy_root, paths)

    for command in (
        ["update-desktop-database", str(applications_dir)],
        ["gtk-update-icon-cache", "-f", "-t", str(icon_path.parents[2])],
    ):
        if shutil.which(command[0]):
            subprocess.run(command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return {
        "executable": target_executable,
        "command": command_path,
        "desktop": desktop_path,
        "icon": icon_path,
        "database": paths.database,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Installer StoryForge dans la session Linux courante.")
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--executable", type=Path, required=True)
    arguments = parser.parse_args()
    installed = install_application(arguments.source_root, arguments.executable)
    print(f"StoryForge installé : {installed['executable']}")
    print(f"Commande : {installed['command']}")
    print(f"Données : {installed['database'].parent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
