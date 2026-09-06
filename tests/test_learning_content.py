from pathlib import Path

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
