from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def uninstall_application(home: Path | None = None) -> list[Path]:
    user_home = Path.home() if home is None else Path(home)
    target_dir = user_home / ".local" / "lib" / "storyforge"
    paths = [
        user_home / ".local" / "bin" / "storyforge",
        user_home / ".local" / "share" / "applications" / "storyforge.desktop",
        user_home / ".local" / "share" / "icons" / "hicolor" / "scalable" / "apps" / "storyforge.svg",
        target_dir / "StoryForge",
    ]
    removed: list[Path] = []
    for path in paths:
        if path.is_symlink() or path.is_file():
            path.unlink()
            removed.append(path)
    if target_dir.is_dir() and not any(target_dir.iterdir()):
        target_dir.rmdir()
    applications_dir = user_home / ".local" / "share" / "applications"
    if shutil.which("update-desktop-database"):
        subprocess.run(
            ["update-desktop-database", str(applications_dir)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return removed


if __name__ == "__main__":
    removed_paths = uninstall_application()
    print(f"StoryForge désinstallé ({len(removed_paths)} élément(s)).")
    print("Les histoires et sauvegardes ont été conservées.")
