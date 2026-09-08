import json
import subprocess
import pytest
from screenplay_model import ScreenplayDocument
from screenplay_adapter import load_document
from screenplay_commands import cycle, after_return, margins
from script_export import export_script_pdf, export_fdx, import_fdx_document


@pytest.mark.parametrize('change', ['future', 'duplicate', 'metadata', 'text', 'kind', 'block'])
def test_reject_invalid_structure_without_legacy_overwrite(change):
    data = ScreenplayDocument.new().to_dict()
    if change == 'future': data['schema_version'] = 99
    elif change == 'duplicate': data['blocks'] *= 2
    elif change == 'metadata': data['blocks'][0]['metadata'] = ['invalid']
    elif change == 'text': data['blocks'][0]['text'] = 12
    elif change == 'kind': data['blocks'][0]['type'] = 'unknown'
    else: data['blocks'].append(None)
    assert ScreenplayDocument.from_json(data) is None
    with pytest.raises(ValueError):
        load_document(json.dumps(data), 'Version texte conservée', 1)


def test_command_rules_and_geometry():
    assert cycle('scene', True) == 'scene'
    assert cycle('character', True) == 'action'
    assert cycle('transition') == 'transition'
    assert after_return('action') == 'character'
    assert after_return('character') == 'dialogue'
    assert margins('dialogue', 1036) == (210, 210, 0, 5)


def test_fdx_explicit_types_and_unicode(tmp_path):
    elements = [('Action', 'MINA'), ('Character', 'MINA'), ('Dialogue', 'Đặng — Привет'), ('Action', '')]
    path = tmp_path / 'typed.fdx'
    export_fdx(path, 'Test', '', elements=elements)
    model = import_fdx_document(path, 1)
    assert [(b.type.value, b.text) for b in model.blocks] == [('action', 'MINA'), ('character', 'MINA'), ('dialogue', 'Đặng — Привет'), ('action', '')]


def test_unicode_pdf_embeds_readable_text(tmp_path):
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    path = tmp_path / 'unicode.pdf'
    export_script_pdf(path, 'Đặng', '', author='Łukasz', elements=[('Scene Heading', 'INT. MUSÉE - JOUR'), ('Character', 'MINA'), ('Dialogue', 'Привет Łódź Đặng')])
    result = subprocess.run(['pdftotext', '-layout', str(path), '-'], check=True, capture_output=True, text=True).stdout
    for value in ('Łukasz', 'Привет', 'Łódź', 'Đặng'):
        assert value in result
