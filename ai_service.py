from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AIReply:
    text: str
    response_id: str | None = None


class ProfessorAI:
    """Compatibility shim for data created by StoryForge 0.5.0.

    The online professor is deliberately disabled in 0.5.1. Keeping this tiny
    class lets older databases open without installing an online SDK.
    """

    def __init__(self, _api_key: str, _model: str):
        pass

    def ask(self, _user_text: str, _context: str, _history: list[dict] = ()) -> AIReply:
        raise RuntimeError(
            "Le professeur IA en ligne a été retiré de StoryForge. "
            "Utilise le guide de feedback local dans Apprentissage."
        )
