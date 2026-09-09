from pathlib import Path

from app import GUIDE_LEVEL_DETAILS, GUIDE_LEVELS, GUIDE_ORDER, GUIDE_SESSIONS
from learning_content import load_session


def test_session_content_follows_the_universal_questions_one_at_a_time() -> None:
    path = Path(__file__).parents[1] / "content" / "sessions" / "session_01.json"
    session = load_session(path)

    assert session.key == "session01"
    assert len(session.steps) == 14
    assert [step.key for step in session.steps] == [
        "idea",
        "interest",
        "protagonist",
        "desire",
        "objective",
        "opposition",
        "stakes",
        "action",
        "consequence",
        "progression",
        "choice",
        "change",
        "ending",
        "seed",
    ]
    for step in session.steps:
        assert step.question
        assert step.why
        assert step.example
        assert step.placeholder
        assert step.tips


def test_all_guides_support_the_three_help_levels_with_complete_content() -> None:
    assert tuple(GUIDE_SESSIONS) == GUIDE_ORDER
    assert tuple(GUIDE_LEVELS) == ("discovery", "guided", "autonomous")
    assert set(GUIDE_LEVEL_DETAILS) == set(GUIDE_LEVELS)

    for session in GUIDE_SESSIONS.values():
        assert session.steps
        assert session.deliverable
        for step in session.steps:
            assert step.question
            assert step.why
            assert step.example
            assert step.placeholder
            assert step.tips
