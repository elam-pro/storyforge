"""Structured screenplay data used by StoryForge's existing script editor.

The editor widget is intentionally still a Qt widget, but it is no longer the
canonical storage format for a screenplay.  This small, dependency-free model
keeps element types and persistent block identifiers beside the text and can
project the document to the legacy plain-text field used by older StoryForge
projects and exports.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence
from uuid import uuid4


class BlockType(str, Enum):
    """Supported screenplay paragraph kinds.

    The first six values are the types exposed by the current StoryForge UI.
    The additional values reserve stable names for later screenplay slices so
    that adding them does not require changing the persistence contract.
    """

    SCENE = "scene"
    ACTION = "action"
    CHARACTER = "character"
    DIALOGUE = "dialogue"
    PARENTHETICAL = "parenthetical"
    TRANSITION = "transition"
    SHOT = "shot"
    GENERAL = "general"
    LYRICS = "lyrics"
    ACT_BREAK = "act_break"
    PAGE_BREAK = "page_break"
    SECTION = "section"

    @classmethod
    def from_value(cls, value: Any, default: "BlockType" = ACTION) -> "BlockType":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            candidate = value.strip().casefold().replace("-", "_").replace(" ", "_")
            aliases = {
                "scene_heading": cls.SCENE,
                "sceneheading": cls.SCENE,
                "parenthesis": cls.PARENTHETICAL,
                "general_text": cls.GENERAL,
                "actbreak": cls.ACT_BREAK,
                "pagebreak": cls.PAGE_BREAK,
            }
            if candidate in aliases:
                return aliases[candidate]
            try:
                return cls(candidate)
            except ValueError:
                pass
        return default


ELEMENT_NAMES: dict[BlockType, str] = {
    BlockType.SCENE: "Scene Heading",
    BlockType.ACTION: "Action",
    BlockType.CHARACTER: "Character",
    BlockType.DIALOGUE: "Dialogue",
    BlockType.PARENTHETICAL: "Parenthetical",
    BlockType.TRANSITION: "Transition",
    BlockType.SHOT: "Shot",
    BlockType.GENERAL: "Action",
    BlockType.LYRICS: "Lyrics",
    BlockType.ACT_BREAK: "Act Break",
    BlockType.PAGE_BREAK: "Page Break",
    BlockType.SECTION: "Section",
}

SCENE_PREFIXES = ("INT.", "EXT.", "INT./EXT.", "EXT./INT.", "I/E.")
TRANSITION_EXACT = {"CUT TO:", "FADE IN:", "FADE OUT.", "FONDU :"}
_CONTINUED_RE = re.compile(r"\s*\(CONT['’]?D\)\s*$", re.IGNORECASE)


def _new_id() -> str:
    return uuid4().hex


def _normalise_text(value: Any) -> str:
    return str(value if value is not None else "").replace("\r", "")


def _normalise_for_type(value: str, block_type: BlockType) -> str:
    value = _normalise_text(value)
    if block_type is BlockType.SCENE:
        return value.strip().upper()
    if block_type is BlockType.CHARACTER:
        return value.strip().upper()
    if block_type is BlockType.TRANSITION:
        return value.strip().upper()
    if block_type is BlockType.PARENTHETICAL:
        value = value.strip()
        if value and not value.startswith("("):
            value = f"({value.strip('()')})"
        return value
    return value


def infer_block_type(
    line: str,
    previous_type: BlockType | None = None,
    previous_blank: bool = True,
) -> BlockType:
    """Infer a type from the explicit markers used by older StoryForge data."""

    raw = _normalise_text(line)
    stripped = raw.strip()
    if not stripped:
        return BlockType.ACTION
    upper = stripped.upper()
    if upper.startswith(SCENE_PREFIXES):
        return BlockType.SCENE
    if stripped.startswith("@"):
        return BlockType.CHARACTER
    if stripped.startswith("!"):
        return BlockType.ACTION
    if stripped.startswith("(") and stripped.endswith(")"):
        return BlockType.PARENTHETICAL
    if upper.endswith((" TO:", " À :", " A :")) or upper in TRANSITION_EXACT:
        return BlockType.TRANSITION
    if (
        previous_type in {BlockType.CHARACTER, BlockType.DIALOGUE, BlockType.PARENTHETICAL}
        and not previous_blank
    ):
        return BlockType.DIALOGUE
    if previous_blank and stripped == upper and len(stripped) <= 42:
        return BlockType.CHARACTER
    return BlockType.ACTION


@dataclass
class ScreenplayBlock:
    """One persistent screenplay paragraph."""

    type: BlockType = BlockType.ACTION
    text: str = ""
    id: str = field(default_factory=_new_id)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.type = BlockType.from_value(self.type)
        self.text = _normalise_for_type(self.text, self.type)
        self.id = str(self.id or _new_id())
        if not isinstance(self.metadata, dict):
            self.metadata = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "text": self.text,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ScreenplayBlock":
        return cls(
            id=str(value.get("id") or _new_id()),
            type=BlockType.from_value(value.get("type")),
            text=_normalise_text(value.get("text", "")),
            metadata=dict(value.get("metadata") or {}),
        )


class ScreenplayDocument:
    """Model-first screenplay document with a stable JSON representation."""

    SCHEMA_VERSION = 1

    def __init__(
        self,
        *,
        document_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        blocks: Iterable[ScreenplayBlock] | None = None,
    ) -> None:
        self.document_id = str(document_id or _new_id())
        self.metadata: dict[str, Any] = dict(metadata or {})
        self.blocks: list[ScreenplayBlock] = list(blocks or [])
        if not self.blocks:
            self.blocks = [ScreenplayBlock(type=BlockType.SCENE)]

    @classmethod
    def new(cls, project_id: int | str | None = None) -> "ScreenplayDocument":
        metadata = {"project_id": str(project_id)} if project_id is not None else {}
        return cls(metadata=metadata)

    @classmethod
    def from_json(cls, payload: str | Mapping[str, Any] | None) -> "ScreenplayDocument | None":
        if not payload:
            return None
        if isinstance(payload, str):
            try:
                value = json.loads(payload)
            except (json.JSONDecodeError, TypeError):
                return None
        else:
            value = payload
        if not isinstance(value, Mapping) or not isinstance(value.get("blocks"), list):
            return None
        version = value.get("schema_version", 1)
        if type(version) is not int or version != cls.SCHEMA_VERSION:
            return None
        if not isinstance(value.get("metadata", {}), dict):
            return None
        if "document_id" in value and not isinstance(value["document_id"], str):
            return None
        ids = set()
        for item in value["blocks"]:
            if not isinstance(item, Mapping):
                return None
            if item.get("type") not in {kind.value for kind in BlockType}:
                return None
            if not isinstance(item.get("text", ""), str) or not isinstance(item.get("metadata", {}), dict):
                return None
            if "id" in item:
                if not isinstance(item["id"], str) or not item["id"] or item["id"] in ids:
                    return None
                ids.add(item["id"])
        blocks = [
            ScreenplayBlock.from_dict(item)
            for item in value["blocks"]
            if isinstance(item, Mapping)
        ]
        return cls(
            document_id=str(value.get("document_id") or _new_id()),
            metadata=value.get("metadata") if isinstance(value.get("metadata"), Mapping) else {},
            blocks=blocks,
        )

    @classmethod
    def from_legacy_text(cls, text: str, *, project_id: int | str | None = None) -> "ScreenplayDocument":
        normalised_text = _normalise_text(text)
        if not normalised_text:
            metadata = {"project_id": str(project_id)} if project_id is not None else {}
            return cls(metadata=metadata, blocks=[ScreenplayBlock(type=BlockType.SCENE)])
        previous_type: BlockType | None = None
        previous_blank = True
        blocks: list[ScreenplayBlock] = []
        for raw_line in normalised_text.split("\n"):
            stripped = raw_line.strip()
            if not stripped:
                blocks.append(ScreenplayBlock(type=BlockType.ACTION, text=""))
                previous_blank = True
                continue
            block_type = infer_block_type(raw_line, previous_type, previous_blank)
            value = stripped
            if value.startswith(("@", "!")):
                value = value[1:].lstrip()
            blocks.append(ScreenplayBlock(type=block_type, text=value))
            previous_type = block_type
            previous_blank = False
        metadata = {"project_id": str(project_id)} if project_id is not None else {}
        return cls(metadata=metadata, blocks=blocks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "document_id": self.document_id,
            "metadata": self.metadata,
            "blocks": [block.to_dict() for block in self.blocks],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, separators=(",", ":"))

    def to_plain_text(self) -> str:
        return "\n".join(block.text for block in self.blocks)

    def block(self, index: int) -> ScreenplayBlock | None:
        if 0 <= index < len(self.blocks):
            return self.blocks[index]
        return None

    def set_block_type(self, index: int, block_type: BlockType | str) -> bool:
        """Change one paragraph kind without changing its persistent ID."""

        current = self.block(index)
        if current is None:
            return False
        target = BlockType.from_value(block_type)
        replacement = ScreenplayBlock(
            id=current.id,
            type=target,
            text=current.text,
            metadata=current.metadata,
        )
        changed = replacement.to_dict() != current.to_dict()
        self.blocks[index] = replacement
        return changed

    def elements(self) -> list[tuple[str, str]]:
        """Return non-empty blocks in the public FDX/export vocabulary."""

        result: list[tuple[str, str]] = []
        for block in self.blocks:
            if not block.text.strip():
                continue
            result.append((ELEMENT_NAMES.get(block.type, "Action"), block.text))
        return result

    def sync_from_editor(
        self,
        block_values: Sequence[tuple[str, BlockType | str | None]],
    ) -> bool:
        """Synchronise a Qt text projection while preserving block IDs.

        Text edits happen in the existing Qt widget for now.  The widget is a
        projection: this method updates the structured model and keeps IDs for
        unchanged, edited, or locally replaced blocks.  A later editor can use
        the same model without changing persistence.
        """

        new_blocks: list[tuple[BlockType, str]] = []
        previous_type: BlockType | None = None
        previous_blank = True
        for raw_value, hinted_type in block_values:
            raw_value = _normalise_text(raw_value)
            block_type = BlockType.from_value(hinted_type, default=BlockType.ACTION)
            if hinted_type is None:
                block_type = infer_block_type(raw_value, previous_type, previous_blank)
            value = raw_value
            if value.strip().startswith(("@", "!")):
                value = value.strip()[1:].lstrip()
            value = _normalise_for_type(value, block_type)
            new_blocks.append((block_type, value))
            if value.strip():
                previous_type = block_type
                previous_blank = False
            else:
                previous_blank = True

        if not new_blocks:
            new_blocks = [(BlockType.SCENE, "")]

        old_keys = [(block.type.value, block.text) for block in self.blocks]
        new_keys = [(block_type.value, value) for block_type, value in new_blocks]
        matches: list[ScreenplayBlock | None] = [None] * len(new_blocks)
        matcher = SequenceMatcher(a=old_keys, b=new_keys, autojunk=False)
        for tag, old_start, old_end, new_start, new_end in matcher.get_opcodes():
            if tag == "delete":
                continue
            count = min(old_end - old_start, new_end - new_start)
            for offset in range(count):
                matches[new_start + offset] = self.blocks[old_start + offset]

        rebuilt: list[ScreenplayBlock] = []
        for index, ((block_type, value), previous) in enumerate(zip(new_blocks, matches)):
            if previous is None:
                rebuilt.append(ScreenplayBlock(type=block_type, text=value))
            else:
                rebuilt.append(
                    ScreenplayBlock(
                        id=previous.id,
                        type=block_type,
                        text=value,
                        metadata=previous.metadata,
                    )
                )

        changed = [block.to_dict() for block in self.blocks] != [
            block.to_dict() for block in rebuilt
        ]
        self.blocks = rebuilt
        return changed

    def rename_character(self, old_name: str, new_name: str) -> int:
        """Rename matching character cues as one model operation."""

        old = _CONTINUED_RE.sub("", _normalise_text(old_name).strip()).strip().casefold()
        new = _normalise_text(new_name).strip().upper()
        if not old or not new:
            return 0
        changed = 0
        for block in self.blocks:
            if block.type is not BlockType.CHARACTER:
                continue
            current = block.text.strip()
            suffix = " (CONT'D)" if _CONTINUED_RE.search(current) else ""
            identity = _CONTINUED_RE.sub("", current).strip().casefold()
            if identity == old:
                block.text = f"{new}{suffix}"
                changed += 1
        return changed

    def scene_headings(self) -> list[ScreenplayBlock]:
        return [block for block in self.blocks if block.type is BlockType.SCENE and block.text.strip()]

    def character_names(self) -> list[str]:
        names: list[str] = []
        seen: set[str] = set()
        for block in self.blocks:
            if block.type is not BlockType.CHARACTER:
                continue
            name = _CONTINUED_RE.sub("", block.text).strip()
            key = name.casefold()
            if name and key not in seen:
                seen.add(key)
                names.append(name)
        return names

    @property
    def word_count(self) -> int:
        return len(self.to_plain_text().split())
