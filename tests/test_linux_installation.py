import importlib.util
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INSTALLER = _load("storyforge_linux_installer", ROOT / "packaging" / "linux" / "install_application.py")
UNINSTALLER = _load("storyforge_linux_uninstaller", ROOT / "packaging" / "linux" / "uninstall_application.py")


def test_linux_install_and_uninstall_preserve_user_data(tmp_path: Path) -> None:
    source_root = ROOT
    fake_executable = tmp_path / "StoryForge"
    fake_executable.write_bytes(b"native executable")
    legacy_database = tmp_path / "source" / "storyforge.db"
    legacy_database.parent.mkdir()
    connection = sqlite3.connect(legacy_database)
    connection.execute("CREATE TABLE projects(title TEXT)")
    connection.execute("INSERT INTO projects VALUES('Histoire')")
    connection.commit()
    connection.close()

    installed = INSTALLER.install_application(
        source_root,
        fake_executable,
        tmp_path / "home",
        legacy_database.parent,
    )
    assert installed["executable"].read_bytes() == b"native executable"
    assert installed["executable"].stat().st_mode & 0o111
    assert installed["command"].is_symlink()
    assert str(installed["executable"]) in installed["desktop"].read_text(encoding="utf-8")
    assert installed["icon"].read_text(encoding="utf-8").startswith("<svg")
    assert installed["database"].is_file()
    assert legacy_database.is_file()

    removed = UNINSTALLER.uninstall_application(tmp_path / "home")
    assert installed["executable"] in removed
    assert installed["database"].is_file()
