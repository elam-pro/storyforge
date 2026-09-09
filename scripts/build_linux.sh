#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$repo_root"
"$repo_root/scripts/bootstrap_dev.sh"
"$repo_root/.venv/bin/python" -m pip install -r requirements-build.txt
"$repo_root/.venv/bin/pyinstaller" \
  --noconfirm \
  --clean \
  --onefile \
  --windowed \
  --name StoryForge \
  --icon "$repo_root/storyforge/resources/storyforge.svg" \
  --add-data "$repo_root/storyforge/content:storyforge/content" \
  --add-data "$repo_root/storyforge/resources:storyforge/resources" \
  --distpath "$repo_root/dist" \
  --workpath "$repo_root/build/pyinstaller" \
  --specpath "$repo_root/build/pyinstaller" \
  "$repo_root/main.py"
printf 'Exécutable créé : %s\n' "$repo_root/dist/StoryForge"
