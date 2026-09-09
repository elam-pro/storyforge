#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$repo_root"
"$repo_root/scripts/build_linux.sh"
if pgrep -u "$(id -u)" -f 'python([^ ]*)? .*app\.py|/StoryForge( |$)' >/dev/null; then
  echo "Ferme StoryForge avant l’installation afin de migrer la base sans perdre de modification." >&2
  exit 2
fi
"$repo_root/.venv/bin/python" "$repo_root/packaging/linux/install_application.py" \
  --source-root "$repo_root" \
  --executable "$repo_root/dist/StoryForge"
printf '\nStoryForge est disponible dans le menu des applications et avec la commande storyforge.\n'
