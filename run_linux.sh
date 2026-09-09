#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$repo_root"
if [[ ! -x .venv/bin/python ]]; then
  echo "Préparation de l’environnement de développement StoryForge..."
  "$repo_root/scripts/bootstrap_dev.sh"
fi
exec "$repo_root/.venv/bin/python" -m storyforge
