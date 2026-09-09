import os
import shutil
import subprocess
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from storyforge.report_export import export_report_pdf


def test_paginated_report_preserves_unicode_and_every_paragraph(tmp_path):
    if not shutil.which("pdftotext"):
        pytest.skip("Poppler text extractor is not installed")
    qt = QApplication.instance() or QApplication([])
    destination = tmp_path / "characters.pdf"
    paragraphs = [f"REPÈRE-{i:03d} — Mina protège sa sœur au musée." for i in range(120)]
    export_report_pdf(destination, "# Personnages\n\n" + "\n\n".join(paragraphs), "Les Veilleurs")
    text = subprocess.check_output(["pdftotext", str(destination), "-"], text=True)
    for paragraph in paragraphs:
        assert text.count(paragraph) == 1
    assert "1 / " in text
    assert text.count("\f") > 1
    assert destination.read_bytes().startswith(b"%PDF")
