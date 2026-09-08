#!/usr/bin/env bash
set -euo pipefail
context_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
context_python="$context_root/.venv-mcp/bin/python"
if [[ ! -x "$context_python" ]]; then
    echo "MCP optional environment missing. See docs/MCP.md." >&2
    exit 1
fi
cd -- "$context_root"
exec "$context_python" -B -m storyforge_context.server --root "$context_root"
