"""Структурированный контекст игровой сессии для наставника (не свободный текст)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.game_engine import evaluate
from app.i18n.translate import translate
from app.models.legal import Citation, LegalDocument
from app.scenarios.registry import Registry
from app.schemas.legal import Locale
from app.services import game


@dataclass
class SessionContext:
    session_id: uuid.UUID
    user_id: uuid.UUID
    legal_date: date
    document_keys: list[str]  # whitelist документов
    citation_ids: list[str]  # кандидаты поиска: ошибки, затем решения, затем остальные ссылки сценария
    text: str  # структурированное описание для промпта
    mistakes: list[dict] = field(default_factory=list)


def load_session_context(
    db: Session, registry: Registry, session_id: uuid.UUID, language: Locale
) -> SessionContext:
    """Raises NotFoundError (нет сессии или сценария) / SessionOutdatedError (журнал не проигрывается)."""
    r = game.load_replayed(db, registry, session_id)
    session = r.session
    sc = r.loaded.scenario
    tr = lambda key: translate(r.loaded, key, language)  # noqa: E731

    lines = [
        f"scenario_id: {sc.scenario_id}",
        f"scenario_title: {tr(sc.card.title_key)}",
        f"legal_date: {sc.legal_date.isoformat()}",
        f"status: {'finished' if r.state.finished else 'in_progress'}",
    ]
    cites: list[str] = []
    mistakes_payload: list[dict] = []
    if r.state.finished:
        outcome = evaluate(sc, r.state)
        lines.append(f"outcome: {outcome.outcome} ({tr(outcome.title_key)})")
        lines.append(f"score: {outcome.score}/{outcome.max_score}")
        lines.append("player_choices:")
        for d in outcome.decisions:
            verdict = "correct" if d.correct else "incorrect"
            lines.append(
                f"- decision {d.decision_id}: chose {d.chosen or 'nothing'}, best {d.best}, {verdict}; "
                f"citations: {', '.join(d.citation_ids) or 'none'}"
            )
        lines.append("mistakes:")
        for m in outcome.mistakes:
            lines.append(
                f"- {tr(m.title_key)} [{m.category}]; citations: {', '.join(m.citation_ids) or 'none'}"
            )
            mistakes_payload.append({"category": m.category, "citation_ids": list(m.citation_ids)})
            cites.extend(m.citation_ids)
        if not outcome.mistakes:
            lines.append("- none")
        cites.extend(c for d in outcome.decisions if not d.correct for c in d.citation_ids)
        cites.extend(outcome.citation_ids)
    else:
        lines.append(f"stage: {r.state.stage}")
        lines.append(f"score_so_far: {r.state.score}")
        lines.append("player_choices: " + (", ".join(f"{k}={v}" for k, v in r.state.choices.items()) or "none"))
        lines.append("mistakes_so_far: " + (", ".join(m.category for m in r.state.mistakes) or "none"))
        for m in r.state.mistakes:
            cites.extend(m.citation_ids)
    cites.extend(sc.citations)
    citation_ids = list(dict.fromkeys(cites))

    keys = list(sc.intro.legal_acts)
    if citation_ids:
        keys.extend(
            db.scalars(
                select(LegalDocument.document_key)
                .join(Citation, Citation.document_id == LegalDocument.id)
                .where(Citation.citation_id.in_(citation_ids))
            )
        )
    return SessionContext(
        session_id=session.id,
        user_id=session.user_id,
        legal_date=sc.legal_date,
        document_keys=list(dict.fromkeys(keys)),
        citation_ids=citation_ids,
        text="\n".join(lines),
        mistakes=mistakes_payload,
    )
