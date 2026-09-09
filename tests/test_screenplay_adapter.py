import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QApplication

from storyforge.screenplay_adapter import block_type, block_values, load_document
from storyforge.screenplay_model import BlockType, ScreenplayBlock, ScreenplayDocument


def test_explicit_types_override_ambiguous_text_and_keep_model_ids():
    qt = QApplication.instance() or QApplication([])
    document = QTextDocument()
    document.setPlainText('MINA\nMINA\n')
    document.firstBlock().setUserState(1002)
    document.firstBlock().next().setUserState(1004)
    values = block_values(document, 'scene')
    assert [kind for text, kind in values] == [BlockType.ACTION, BlockType.DIALOGUE, BlockType.SCENE]
    model = ScreenplayDocument(blocks=[ScreenplayBlock(type=kind, text=text) for text, kind in values])
    ids = [block.id for block in model.blocks]
    assert not model.sync_from_editor(values)
    assert [block.id for block in model.blocks] == ids
    assert model.elements() == [('Action', 'MINA'), ('Dialogue', 'MINA')]


def test_long_untyped_dialogue_has_no_recursion_and_matches_single_lookup():
    qt = QApplication.instance() or QApplication([])
    document = QTextDocument()
    document.setPlainText('@MINA\n' + '\n'.join(['Une réplique.'] * 2000))
    values = block_values(document)
    assert len(values) == 2001
    assert values[0][1] == BlockType.CHARACTER
    assert all(kind == BlockType.DIALOGUE for text, kind in values[1:])
    assert block_type(document.lastBlock()) == BlockType.DIALOGUE


def test_partial_prefixes_and_blank_break_preserve_editor_rules():
    qt = QApplication.instance() or QApplication([])
    document = QTextDocument()
    document.setPlainText('IN\n@MINA\nBonjour\n\nElle part.\nCUT TO:')
    expected = [BlockType.SCENE, BlockType.CHARACTER, BlockType.DIALOGUE,
                BlockType.ACTION, BlockType.ACTION, BlockType.TRANSITION]
    assert [kind for text, kind in block_values(document)] == expected
    block = document.firstBlock()
    for kind in expected:
        assert block_type(block) == kind
        block = block.next()


def test_load_preserves_structure_and_legacy_conflict_policy():
    original = ScreenplayDocument(blocks=[ScreenplayBlock(type=BlockType.ACTION, text='MINA')])
    restored = load_document(original.to_json(), 'MINA', 42)
    assert restored.document_id == original.document_id
    assert restored.blocks[0].id == original.blocks[0].id
    assert restored.blocks[0].type == BlockType.ACTION
    assert restored.metadata['project_id'] == '42'
    assert load_document(original.to_json(), '', 42).to_plain_text() == 'MINA'
    assert load_document(original.to_json(), 'Texte modifié', 42).to_plain_text() == 'Texte modifié'
    assert load_document('', 'INT. HALL - JOUR', 42).blocks[0].type == BlockType.SCENE
