"""Boundary between a Qt text document and the screenplay model.

No window, persistence or exports here. Explicit Qt paragraph states take
precedence; untyped legacy paragraphs retain the editor's inference rules.
"""
from .screenplay_model import BlockType, ScreenplayDocument, SCENE_PREFIXES, TRANSITION_EXACT


QT_BLOCK_TYPES = dict(zip(range(1001, 1007), (
    BlockType.SCENE, BlockType.ACTION, BlockType.CHARACTER,
    BlockType.DIALOGUE, BlockType.PARENTHETICAL, BlockType.TRANSITION)))


def _infer(text, state, previous_type, previous_text, empty_type):
    if state in QT_BLOCK_TYPES:
        return QT_BLOCK_TYPES[state]
    line = text.strip()
    if not line:
        return BlockType.from_value(empty_type)
    upper = line.upper()
    if upper in {'I', 'IN', 'INT', 'E', 'EX', 'EXT', 'I/E'} or upper.startswith(SCENE_PREFIXES):
        return BlockType.SCENE
    if line.startswith('@'):
        return BlockType.CHARACTER
    if line.startswith('!'):
        return BlockType.ACTION
    if line.startswith('(') and line.endswith(')'):
        return BlockType.PARENTHETICAL
    if upper.endswith((' TO:', ' À :', ' A :')) or upper in TRANSITION_EXACT:
        return BlockType.TRANSITION
    if previous_type in {BlockType.CHARACTER, BlockType.DIALOGUE, BlockType.PARENTHETICAL} and previous_text.strip():
        return BlockType.DIALOGUE
    return BlockType.CHARACTER if line == upper and len(line) <= 42 else BlockType.ACTION


def block_values(qt_document, empty_type='action'):
    """Read all paragraphs in one pass (no recursion for long dialogues)."""
    values = []
    previous_type, previous_text = None, ''
    block = qt_document.firstBlock()
    while block.isValid():
        text = block.text()
        kind = _infer(text, block.userState(), previous_type, previous_text, empty_type)
        values.append((text, kind))
        previous_type, previous_text = kind, text
        block = block.next()
    return values


def block_type(block, empty_type='action'):
    if block.userState() in QT_BLOCK_TYPES:
        return QT_BLOCK_TYPES[block.userState()]
    preceding = []
    current = block
    while current.isValid():
        preceding.append((current.text(), current.userState()))
        if current.userState() in QT_BLOCK_TYPES:
            break
        current = current.previous()
    kind, previous_text = None, ''
    for text, state in reversed(preceding):
        kind = _infer(text, state, kind, previous_text, empty_type)
        previous_text = text
    return kind or BlockType.from_value(empty_type)


def load_document(stored_json, legacy_text, project_id):
    """Preserve the existing migration policy; do not discard edited legacy text."""
    document = ScreenplayDocument.from_json(stored_json)
    if stored_json and document is None:
        raise ValueError("Format de scénario invalide ou version non prise en charge. Données conservées.")
    legacy = str(legacy_text or '')
    if document is None or (legacy.strip() and document.to_plain_text().strip() != legacy.strip()):
        document = ScreenplayDocument.from_legacy_text(legacy, project_id=project_id)
    document.metadata.setdefault('project_id', str(project_id))
    return document
