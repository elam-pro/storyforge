#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
app_version="$(awk -F'"' '/^APP_VERSION = / { print $2; exit }' app.py)"
: "${app_version:=locale}"
if [ ! -x .venv/bin/python ]; then
  echo "Première installation de StoryForge ${app_version} pour Linux..."
  python3 -m venv .venv
  . .venv/bin/activate
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
fi
exec .venv/bin/python app.py
