from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _copy(source: Path, destination: Path, mode: int | None = None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if mode is not None:
        destination.chmod(mode)


def build_release(
    source_root: Path,
    executable: Path,
    output_dir: Path,
    version: str,
    architecture: str,
) -> tuple[Path, Path]:
    """Build a self-contained, checksummed Linux release archive."""

    root = Path(source_root).resolve()
    executable = Path(executable).resolve()
    output_dir = Path(output_dir).resolve()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"Version invalide : {version}")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", architecture):
        raise ValueError(f"Architecture invalide : {architecture}")
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise FileNotFoundError(f"Exécutable introuvable ou non exécutable : {executable}")
    reported = subprocess.run(
        [str(executable), "--version"],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout.strip()
    if reported != f"StoryForge {version}":
        raise ValueError(f"Version de l’exécutable inattendue : {reported!r}")

    output_dir.mkdir(parents=True, exist_ok=True)
    bundle_name = f"StoryForge-{version}-linux-{architecture}"
    archive = output_dir / f"{bundle_name}.tar.gz"
    archive_checksum = archive.with_suffix(archive.suffix + ".sha256")

    with tempfile.TemporaryDirectory(prefix="storyforge-release-") as temporary:
        bundle = Path(temporary) / bundle_name
        _copy(executable, bundle / "StoryForge", 0o755)
        for relative in (
            "storyforge/__init__.py",
            "storyforge/runtime_paths.py",
            "storyforge/version.py",
            "storyforge/resources/storyforge.svg",
            "packaging/linux/install_application.py",
            "packaging/linux/storyforge.desktop.in",
            "packaging/linux/uninstall_application.py",
        ):
            _copy(root / relative, bundle / relative)

        install_script = """#!/usr/bin/env bash
set -euo pipefail
bundle_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v sha256sum >/dev/null; then
  echo "sha256sum est requis pour vérifier le paquet." >&2
  exit 3
fi
(cd "$bundle_root" && sha256sum -c SHA256SUMS)
if pgrep -u "$(id -u)" -f '/StoryForge( |$)' >/dev/null; then
  echo "Ferme StoryForge avant de lancer la mise à jour." >&2
  exit 2
fi
python3 "$bundle_root/packaging/linux/install_application.py" \\
  --source-root "$bundle_root" \\
  --executable "$bundle_root/StoryForge"
"""
        uninstall_script = """#!/usr/bin/env bash
set -euo pipefail
bundle_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 "$bundle_root/packaging/linux/uninstall_application.py"
"""
        (bundle / "install.sh").write_text(install_script, encoding="utf-8")
        (bundle / "install.sh").chmod(0o755)
        (bundle / "uninstall.sh").write_text(uninstall_script, encoding="utf-8")
        (bundle / "uninstall.sh").chmod(0o755)

        readme = (root / "packaging" / "linux" / "RELEASE_README.txt.in").read_text(encoding="utf-8")
        (bundle / "LISEZ-MOI.txt").write_text(readme.replace("@VERSION@", version), encoding="utf-8")

        payloads = sorted(path for path in bundle.rglob("*") if path.is_file())
        checksum_lines = [f"{_sha256(path)}  {path.relative_to(bundle).as_posix()}" for path in payloads]
        (bundle / "SHA256SUMS").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

        temporary_archive = archive.with_name(f".{archive.name}.building-{os.getpid()}")
        with tarfile.open(temporary_archive, "w:gz") as target:
            target.add(bundle, arcname=bundle_name, recursive=True)
        temporary_archive.replace(archive)

    checksum_text = f"{_sha256(archive)}  {archive.name}\n"
    temporary_checksum = archive_checksum.with_name(f".{archive_checksum.name}.building-{os.getpid()}")
    temporary_checksum.write_text(checksum_text, encoding="utf-8")
    temporary_checksum.replace(archive_checksum)
    return archive, archive_checksum


def main() -> int:
    parser = argparse.ArgumentParser(description="Créer une archive Linux installable de StoryForge.")
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--architecture", required=True)
    arguments = parser.parse_args()
    archive, checksum = build_release(
        arguments.source_root,
        arguments.executable,
        arguments.output_dir,
        arguments.version,
        arguments.architecture,
    )
    print(f"Archive : {archive}")
    print(f"Checksum : {checksum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
