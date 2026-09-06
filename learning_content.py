from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LearningStep:
    key: str
    title: str
    concept_key: str
    concept_label: str
    question: str
    why: str
    example: str
    placeholder: str
    tips: tuple[str, ...]


@dataclass(frozen=True)
class LearningSession:
    key: str
    cycle: str
    title: str
    subtitle: str
    steps: tuple[LearningStep, ...]
    description: str = ""
    deliverable: str = ""
    requires_project: bool = False
    apply_label: str = ""


def load_session(path: Path) -> LearningSession:
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "key",
        "title",
        "concept_key",
        "concept_label",
        "question",
        "why",
        "example",
        "placeholder",
        "tips",
    }
    steps: list[LearningStep] = []
    for index, raw in enumerate(data.get("steps", []), 1):
        missing = required.difference(raw)
        if missing:
            raise ValueError(f"Étape {index}: champs manquants: {', '.join(sorted(missing))}")
        steps.append(
            LearningStep(
                key=str(raw["key"]),
                title=str(raw["title"]),
                concept_key=str(raw["concept_key"]),
                concept_label=str(raw["concept_label"]),
                question=str(raw["question"]),
                why=str(raw["why"]),
                example=str(raw["example"]),
                placeholder=str(raw["placeholder"]),
                tips=tuple(str(item) for item in raw["tips"]),
            )
        )
    if not steps:
        raise ValueError("Une session pédagogique doit contenir au moins une étape.")
    return LearningSession(
        key=str(data["key"]),
        cycle=str(data["cycle"]),
        title=str(data["title"]),
        subtitle=str(data["subtitle"]),
        steps=tuple(steps),
        description=str(data.get("description", data["subtitle"])),
        deliverable=str(data.get("deliverable", "")),
        requires_project=bool(data.get("requires_project", False)),
        apply_label=str(data.get("apply_label", "")),
    )
