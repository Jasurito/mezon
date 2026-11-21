"""Every line of a scenario that a character (or the narrator) speaks and that is known before the game starts."""

from __future__ import annotations

from dataclasses import dataclass

from app.game_engine.validate import _effect_lists
from app.schemas.scenario import Scenario


@dataclass(frozen=True)
class Line:
    speaker: str
    text_key: str


def spoken_lines(scenario: Scenario) -> list[Line]:
    """``say`` effects (stages, actions, decision consequences) and scripted NPC answers, without duplicates.

    AI-written NPC answers and Mentor answers are not known in advance and stay text only.
    """
    seen: dict[tuple[str, str], Line] = {}
    for _, effects in _effect_lists(scenario):
        for e in effects:
            if e.say is not None:
                seen.setdefault((e.say.speaker, e.say.text_key), Line(e.say.speaker, e.say.text_key))
    for q in scenario.npc_questions:
        seen.setdefault((q.character_id, q.answer_key), Line(q.character_id, q.answer_key))
    return list(seen.values())
