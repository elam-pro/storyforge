import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

import storyforge.app as app_module
from storyforge.app import StoryForgeWindow
from storyforge.ai_service import ProfessorAI
from storyforge.db import Database, NOW


def test_manual_output_is_next_to_test_database(tmp_path, monkeypatch):
    qt = QApplication.instance() or QApplication([])
    fake_source = tmp_path / 'source'
    fake_source.mkdir()
    sentinel = fake_source / 'Mon manuel d’écriture & storytelling.pdf'
    sentinel.write_bytes(b'keep existing export')
    window = StoryForgeWindow(tmp_path / 'data.db')
    monkeypatch.setattr(app_module, 'BASE_DIR', fake_source)
    try:
        window._write_cumulative_manual()
        output = window._manual_output_path()
        assert output == tmp_path / 'output' / 'manuals' / sentinel.name
        assert output.read_bytes().startswith(b'%PDF-')
        assert sentinel.read_bytes() == b'keep existing export'
    finally:
        window.close()
        qt.processEvents()


def test_manual_export_failure_is_reported(tmp_path, monkeypatch):
    qt = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / 'data.db')
    warnings = []
    def fail(*args):
        raise OSError('disk unavailable')
    monkeypatch.setattr(app_module, 'export_manual_pdf', fail)
    monkeypatch.setattr(QMessageBox, 'warning', lambda *args: warnings.append(args))
    try:
        window._write_cumulative_manual()
        assert len(warnings) == 1
        assert 'disk unavailable' in warnings[0][-1]
    finally:
        window.close()
        qt.processEvents()


def test_legacy_ai_data_survives_without_obsolete_ui(tmp_path):
    qt = QApplication.instance() or QApplication([])
    path = tmp_path / 'legacy.db'
    db = Database(path)
    db.run('INSERT INTO ai_messages(created_at,role,content) VALUES(?,?,?)', (NOW(), 'user', 'Historical message'))
    db.run('INSERT INTO ai_notes(created_at,content) VALUES(?,?)', (NOW(), 'Historical note'))
    db.set_setting('ai_mode', 'legacy')
    db.conn.close()
    window = StoryForgeWindow(path)
    try:
        assert not hasattr(window, '_ai_worker')
        assert not hasattr(window, 'show_ai')
        assert 'ai' not in window.nav_buttons
        assert window.db.one('SELECT content FROM ai_messages')[0] == 'Historical message'
        assert window.db.one('SELECT content FROM ai_notes')[0] == 'Historical note'
        assert window.db.setting('ai_mode') == 'legacy'
        with pytest.raises(RuntimeError, match='retiré'):
            ProfessorAI('', '').ask('', '')
    finally:
        window.close()
        qt.processEvents()
