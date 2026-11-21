"""Представление состояния движка для API: перевод и сборка ответов. Чистые функции, без БД."""

from __future__ import annotations

import uuid

from app.game_engine import AvailableAction, EngineState, Event, Outcome, available_actions
from app.game_engine.engine import FORECAST_REASON_KEY
from app.i18n import message, translate
from app.i18n.messages import MESSAGES
from app.scenarios.loader import LoadedScenario
from app.schemas import api
from app.schemas.legal import CitationView, Locale
from app.schemas.scenario import SKILLS
from app.tts.catalog import audio_for


def stage_index(loaded: LoadedScenario, stage_id: str) -> int:
    """Номер этапа в scenario.stages, с 1."""
    for i, st in enumerate(loaded.scenario.stages, start=1):
        if st.id == stage_id:
            return i
    raise KeyError(stage_id)


def present_events(
    loaded: LoadedScenario, events: list[Event], locale: Locale
) -> list[api.SayEvent | api.ReactEvent | api.StageChangedEvent | api.EvidenceAddedEvent | api.ScoreEvent | api.LegalNoteEvent | api.MistakeEvent]:
    """События с переведёнными текстами; mistake скрыты, если reveal_mistakes = false."""
    out: list = []
    for e in events:
        if e.type == "say":
            audio = audio_for(loaded, e.speaker, e.text_key, locale)
            out.append(
                api.SayEvent(
                    speaker=e.speaker,
                    text=translate(loaded, e.text_key, locale),
                    emotion=e.emotion,
                    audio_url=audio.url if audio else None,
                    audio_duration_ms=audio.duration_ms if audio else None,
                )
            )
        elif e.type == "react":
            out.append(api.ReactEvent(character=e.character, reaction=e.reaction))
        elif e.type == "stage_changed":
            out.append(api.StageChangedEvent(stage=e.stage, title=translate(loaded, e.title_key, locale)))
        elif e.type == "evidence_added":
            out.append(api.EvidenceAddedEvent(evidence_id=e.evidence_id))
        elif e.type == "score":
            reason = None
            if e.reason_key:
                reason = message(e.reason_key, locale) if e.reason_key in MESSAGES else translate(loaded, e.reason_key, locale)
            out.append(api.ScoreEvent(delta=e.delta, total=e.total, reason=reason))
        elif e.type == "legal_note":
            out.append(
                api.LegalNoteEvent(citation_id=e.citation_id, text=translate(loaded, e.text_key, locale))
            )
        elif e.type == "mistake":
            if loaded.scenario.reveal_mistakes:
                out.append(api.MistakeEvent(category=e.category, text=translate(loaded, e.title_key, locale)))
    return out


def present_actions(
    loaded: LoadedScenario, actions: list[AvailableAction], locale: Locale
) -> list[api.ActionView]:
    return [
        api.ActionView(
            action_id=a.id,
            kind=a.kind,
            label=translate(loaded, a.label_key, locale),
            target_character=a.target_character,
            evidence_id=a.evidence_id,
            options=(
                [api.OptionView(id=o.id, label=translate(loaded, o.label_key, locale)) for o in a.options]
                if a.options is not None
                else None
            ),
            hint_citation_ids=list(a.hint_citation_ids),
        )
        for a in actions
    ]


def present_evidence(loaded: LoadedScenario, state: EngineState, locale: Locale) -> list[api.EvidenceView]:
    """Улики дела видны со второго этапа; добавленные эффектами идут следом в порядке добавления."""
    sc = loaded.scenario
    by_id = {e.id: e for e in sc.evidence}
    ids: list[str] = []
    if stage_index(loaded, state.stage) >= 2:
        ids += [e.id for e in sc.evidence if e.in_case_file]
    ids += [i for i in state.evidence if i not in ids]
    flags = set(state.flags)
    return [
        api.EvidenceView(
            id=i,
            title=translate(loaded, by_id[i].title_key, locale),
            type=by_id[i].type,
            reviewed=f"{i}_reviewed" in flags,
            presented=f"{i}_presented" in flags,
        )
        for i in ids
    ]


def build_evidence_document(
    loaded: LoadedScenario, state: EngineState, evidence_id: str, locale: Locale
) -> api.EvidenceDocument | None:
    """Текст улики из материалов дела; None, если в этой сессии её ещё нет (тот же список, что GameState.evidence)."""
    if evidence_id not in {e.id for e in present_evidence(loaded, state, locale)}:
        return None
    sc = loaded.scenario
    ev = next(e for e in sc.evidence if e.id == evidence_id)
    if ev.text_key:
        lines = [ln.strip() for ln in translate(loaded, ev.text_key, locale).split("\n") if ln.strip()]
    else:
        facts = {f.id: f for f in sc.facts}
        lines = [translate(loaded, facts[f].text_key, locale) for f in ev.facts if f in facts]
    return api.EvidenceDocument(id=ev.id, title=translate(loaded, ev.title_key, locale), type=ev.type, lines=lines)


def build_game_state(
    loaded: LoadedScenario,
    state: EngineState,
    events: list[Event],
    session_id: uuid.UUID,
    locale: Locale,
    actions: list[AvailableAction] | None = None,
) -> api.GameState:
    """Собрать GameState. ``actions`` по умолчанию считаются движком."""
    sc = loaded.scenario
    if actions is None:
        actions = available_actions(sc, state)
    stage = next(s for s in sc.stages if s.id == state.stage)
    return api.GameState(
        session_id=session_id,
        scenario_id=sc.scenario_id,
        locale=locale,
        stage=state.stage,
        stage_title=translate(loaded, stage.title_key, locale),
        stage_index=stage_index(loaded, state.stage),
        stage_count=len(sc.stages),
        score=state.score,
        max_score=sc.max_score,
        evidence=present_evidence(loaded, state, locale),
        available_actions=present_actions(loaded, actions, locale),
        events=present_events(loaded, events, locale),
        finished=state.finished,
        legal_date=sc.legal_date,
        stage_goal=translate(loaded, stage.goal_key, locale) if stage.goal_key else None,
    )


def build_scenario_card(loaded: LoadedScenario, locale: Locale) -> api.ScenarioCard:
    sc = loaded.scenario
    card = sc.card
    return api.ScenarioCard(
        scenario_id=sc.scenario_id,
        title=translate(loaded, card.title_key, locale),
        category=translate(loaded, card.category_key, locale),
        difficulty=card.difficulty,
        minutes=card.minutes,
        topics=[translate(loaded, k, locale) for k in card.topic_keys],
        cover=card.cover,
        fictional_notice=translate(loaded, sc.fictional_notice_key, locale),
        available=card.available,
        kind=card.kind,
    )


def build_scenario_detail(
    loaded: LoadedScenario, legal_acts: list, locale: Locale
) -> api.ScenarioDetail:
    sc = loaded.scenario
    t = lambda k: translate(loaded, k, locale)  # noqa: E731
    return api.ScenarioDetail(
        scenario_id=sc.scenario_id,
        title=t(sc.card.title_key),
        fictional_notice=t(sc.fictional_notice_key),
        legal_date=sc.legal_date,
        story=t(sc.intro.story_key),
        player_role=api.PlayerRoleView(
            character_id=sc.intro.player_role.character_id, title=t(sc.intro.player_role.title_key)
        ),
        characters=[
            api.CharacterView(id=c.id, name=t(c.name_key), role=t(c.role_key), sprite=c.sprite)
            for c in sc.characters
        ],
        claims=[api.ClaimView(side=c.side, text=t(c.text_key)) for c in sc.intro.claims],
        documents=[api.DocumentView(id=e.id, title=t(e.title_key)) for e in sc.evidence if e.in_case_file],
        legal_acts=legal_acts,
        kind=sc.card.kind,
        scoring=api.ScenarioScoring(
            max_score=sc.max_score,
            skills=[
                api.ScoringSkill(
                    skill=s,
                    label=message(f"skill.{s}", locale),
                    description=message(f"skill.{s}.desc", locale),
                )
                for s in SKILLS
            ],
            outcomes=[
                api.ScoringOutcome(result_kind=k, label=message(f"result.kind.{k}", locale))
                for k in dict.fromkeys(r.result_kind or "loss" for r in sc.evaluation_rules)
            ],
        ),
    )


def build_result(
    loaded: LoadedScenario,
    outcome: Outcome,
    session_id: uuid.UUID,
    locale: Locale,
    citations: list[CitationView],
    time_spent_sec: int,
) -> api.SessionResult:
    sc = loaded.scenario
    t = lambda k: translate(loaded, k, locale)  # noqa: E731
    dps = {d.decision_id: d for d in sc.decisions}

    def option_label(decision_id: str, option_id: str | None) -> str:
        if option_id is None:
            return message("result.no_choice", locale)
        for o in dps[decision_id].options:
            if o.id == option_id:
                return t(o.label_key)
        return option_id

    def mistake_view(m) -> api.MistakeView:
        return api.MistakeView(
            category=m.category,
            title=t(m.title_key),
            explanation=t(m.explanation_key),
            correct_action=t(m.correct_action_key) if m.correct_action_key else None,
            citation_ids=list(m.citation_ids),
        )

    skills = []
    for s in SKILLS:
        total = sum(1 for d in outcome.decisions if d.skill == s)
        correct = sum(1 for d in outcome.decisions if d.skill == s and d.correct)
        skills.append(
            api.SkillScore(
                skill=s,
                label=message(f"skill.{s}", locale),
                correct=correct,
                total=total,
                percent=round(100 * correct / total) if total else None,
                mistakes=sum(1 for m in outcome.mistakes if m.category == s),
            )
        )

    return api.SessionResult(
        session_id=session_id,
        scenario_id=sc.scenario_id,
        outcome=outcome.outcome,
        result_kind=outcome.result_kind,
        result_label=message(f"result.kind.{outcome.result_kind}", locale),
        outcome_title=t(outcome.title_key),
        ruling_text=t(outcome.ruling_key),
        score=outcome.score,
        max_score=outcome.max_score,
        correct_decision_rate=round(outcome.correct_decision_rate, 2),
        time_spent_sec=time_spent_sec,
        decisions=[
            api.DecisionView(
                decision_id=d.decision_id,
                stage=d.stage,
                chosen=d.chosen,
                chosen_label=option_label(d.decision_id, d.chosen),
                best=d.best,
                best_label=option_label(d.decision_id, d.best),
                correct=d.correct,
                explanation=t(d.explanation_key),
                citation_ids=list(d.citation_ids),
                kind=d.kind,
                counterfactual=(
                    t(d.counterfactual_key) if d.counterfactual_key and not d.correct else None
                ),
            )
            for d in outcome.decisions
        ],
        mistakes=[mistake_view(m) for m in outcome.mistakes],
        citations=citations,
        recommendations=[
            api.RecommendationView(topic=t(r.topic_key), citation_ids=list(r.citation_ids), scenario_id=r.scenario_id)
            for r in outcome.recommendations
        ],
        skills=skills,
        main_mistake=mistake_view(outcome.mistakes[0]) if outcome.mistakes else None,
        disclaimer=message("result.disclaimer", locale),
    )
