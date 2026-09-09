import subprocess
import sys
from pathlib import Path

from storyforge.version import APP_VERSION


ROOT = Path(__file__).resolve().parents[1]


def test_module_entry_point_reports_version_without_starting_ui(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "storyforge", "--version"],
        cwd=ROOT,
        env={"HOME": str(tmp_path)},
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == f"StoryForge {APP_VERSION}"
    assert not (tmp_path / ".local" / "share" / "storyforge").exists()
