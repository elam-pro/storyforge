"""Deployment entry point for StoryForge."""

import sys

from storyforge.version import APP_VERSION


def main() -> int:
    if "--version" in sys.argv[1:]:
        print(f"StoryForge {APP_VERSION}")
        return 0

    from storyforge.app import main as run_application

    return run_application()


if __name__ == "__main__":
    raise SystemExit(main())
