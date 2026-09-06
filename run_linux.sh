#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "Première installation de StoryForge 0.26.0 pour Linux..."
  python3 -m venv .venv
  . .venv/bin/activate
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
fi
exec .venv/bin/python app.py
