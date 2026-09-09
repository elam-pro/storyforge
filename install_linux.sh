#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
app_version="$(awk -F'"' '/^APP_VERSION = / { print $2; exit }' app.py)"
: "${app_version:=locale}"
if [ ! -d .venv ]; then python3 -m venv .venv; fi
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
printf '\nStoryForge %s pour Linux est prêt.\n' "$app_version"
