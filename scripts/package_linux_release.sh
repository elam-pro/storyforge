#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$repo_root"

if [[ ! -x "$repo_root/.venv/bin/python" ]]; then
  "$repo_root/scripts/bootstrap_dev.sh"
fi

version="$("$repo_root/.venv/bin/python" -c 'from storyforge.version import APP_VERSION; print(APP_VERSION)')"
architecture="${STORYFORGE_RELEASE_ARCH:-$(uname -m)}"
expected="StoryForge $version"
reported=""
if [[ -x "$repo_root/dist/StoryForge" ]]; then
  reported="$("$repo_root/dist/StoryForge" --version || true)"
fi
if [[ "$reported" != "$expected" ]]; then
  "$repo_root/scripts/build_linux.sh"
fi

"$repo_root/.venv/bin/python" "$repo_root/packaging/linux/build_release.py" \
  --source-root "$repo_root" \
  --executable "$repo_root/dist/StoryForge" \
  --output-dir "$repo_root/dist/releases" \
  --version "$version" \
  --architecture "$architecture"
