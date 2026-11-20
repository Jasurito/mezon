"""FakeLLM для NPC: модель вывода классификатора создаётся динамически, поэтому подбираем её по базе."""

from __future__ import annotations

from app.ai.llm import FakeLLM
from app.schemas.npc import NpcClassification


class NpcFakeLLM(FakeLLM):
    """``classify``: question_id, None (сбой) или исключение. ``reply``: NpcReply, None или исключение."""

    def __init__(self, classify=None, reply=None) -> None:
        from app.schemas.npc import NpcReply

        super().__init__({NpcReply: reply})
        self.classify = classify

    def structured(self, **kw):
        out = kw["output_model"]
        if isinstance(out, type) and issubclass(out, NpcClassification):
            self.calls.append(kw)
            if isinstance(self.classify, BaseException):
                raise self.classify
            return None if self.classify is None else out(question_id=self.classify)
        return super().structured(**kw)

    def classify_calls(self):
        return [c for c in self.calls if issubclass(c["output_model"], NpcClassification)]
