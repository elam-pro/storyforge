import hashlib
import importlib.util
import subprocess
import tarfile
from pathlib import Path

from storyforge.version import APP_VERSION


ROOT = Path(__file__).resolve().parents[1]


def _load_builder():
    path = ROOT / "packaging" / "linux" / "build_release.py"
    spec = importlib.util.spec_from_file_location("storyforge_linux_release", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_release_archive_is_verified_and_installs_without_repository(tmp_path: Path) -> None:
    builder = _load_builder()
    executable = tmp_path / "StoryForge"
    executable.write_text(
        f"#!/usr/bin/env sh\necho 'StoryForge {APP_VERSION}'\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)

    archive, checksum_path = builder.build_release(
        ROOT,
        executable,
        tmp_path / "releases",
        APP_VERSION,
        "test-arch",
    )
    expected_checksum, expected_name = checksum_path.read_text(encoding="utf-8").split()
    assert expected_name == archive.name
    assert expected_checksum == _sha256(archive)

    extracted = tmp_path / "extracted"
    with tarfile.open(archive, "r:gz") as source:
        source.extractall(extracted, filter="data")
    bundle = extracted / f"StoryForge-{APP_VERSION}-linux-test-arch"
    for line in (bundle / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        checksum, relative = line.split("  ", 1)
        assert checksum == _sha256(bundle / relative)

    home = tmp_path / "home"
    subprocess.run(
        [str(bundle / "install.sh")],
        cwd=bundle,
        env={"HOME": str(home), "PATH": "/usr/bin:/bin"},
        check=True,
        capture_output=True,
        text=True,
    )
    installed = home / ".local" / "lib" / "storyforge" / "StoryForge"
    assert subprocess.run(
        [str(installed), "--version"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == f"StoryForge {APP_VERSION}"

    (bundle / "LISEZ-MOI.txt").write_text("paquet altéré", encoding="utf-8")
    rejected = subprocess.run(
        [str(bundle / "install.sh")],
        cwd=bundle,
        env={"HOME": str(home), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )
    assert rejected.returncode != 0
    assert "FAILED" in rejected.stdout
