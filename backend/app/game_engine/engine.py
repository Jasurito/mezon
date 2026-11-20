"""Pure game engine: initial_state / available_actions / apply / replay."""

from __future__ import annotations

from app.game_engine.conditions import eval_condition
from app.game_engine.errors import IllegalAction, ScenarioError, SessionFinished
from app.game_engine.evaluate import evaluate
from app.game_engine.state import (
    AvailableAction,
    EngineState,
    Event,
    EvidenceAddedEvent,
    LegalNoteEvent,
    LoggedAction,
    MistakeEvent,
    OptionView,
    ReactEvent,
    SayEvent,
    ScoreEvent,
    StageChangedEvent,
)
from app.schemas.scenario import Action, Effect, Scenario, Stage

RESULTS = "RESULTS"
MAX_TRANSITIONS = 20


class _Work:
    """Mutable scratch state for a single apply() call."""

    def __init__(self, scenario: Scenario, s: EngineState | None) -> None:
        self.stages: dict[str, Stage] = {st.id: st for st in scenario.stages}
        self.flags: set[str] = set(s.flags) if s else set()
        self.score = s.score if s else 0
        self.evidence = list(s.evidence) if s else []
        self.choices = dict(s.choices) if s else {}
        self.mistakes = list(s.mistakes) if s else []
        self.stage = s.stage if s else scenario.stages[0].id
        self.finished = s.finished if s else False
        self.events: list[Event] = []
        self.jumps = 0


def _run_effects(w: _Work, effects: list[Effect]) -> None:
    for eff in effects:
        name, val = eff.active()
        if name == "set_":
            w.flags.add(val)
        elif name == "unset":
            w.flags.discard(val)
        elif name == "score":
            _add_score(w, val)
        elif name == "say":
            w.events.append(SayEvent(speaker=val.speaker, text_key=val.text_key, emotion=val.emotion))
        elif name == "react":
            w.events.append(ReactEvent(character=val.character, reaction=val.reaction))
        elif name == "add_evidence":
            if val not in w.evidence:
                w.evidence.append(val)
            w.events.append(EvidenceAddedEvent(evidence_id=val))
        elif name == "mistake":
            w.mistakes.append(val)
            w.events.append(MistakeEvent(category=val.category, title_key=val.title_key))
        elif name == "legal_note":
            w.events.append(LegalNoteEvent(citation_id=val.citation_id, text_key=val.text_key))
        elif name == "goto":
            _enter(w, val)


def _add_score(w: _Work, delta: int) -> None:
    w.score += delta
    w.events.append(ScoreEvent(delta=delta, total=w.score))


def _enter(w: _Work, to: str) -> None:
    """Move to a stage: emit stage_changed, run on_enter, finish on RESULTS."""
    w.jumps += 1
    if w.jumps > MAX_TRANSITIONS:
        raise ScenarioError(f"more than {MAX_TRANSITIONS} transitions in one step (loop?)")
    stage = w.stages.get(to)
    if stage is None:
        raise ScenarioError(f"unknown stage '{to}'")
    w.stage = to
    w.events.append(StageChangedEvent(stage=to, title_key=stage.title_key))
    if to == RESULTS:
        w.finished = True
        return
    _run_effects(w, stage.on_enter)


def _settle(w: _Work) -> None:
    """Follow transitions of the current stage until none fires."""
    while not w.finished:
        for t in w.stages[w.stage].transitions:
            if eval_condition(t.when, w):
                _enter(w, t.to)
                break
        else:
            return


def _freeze(scenario: Scenario, w: _Work, prev: EngineState | None, action_id: str | None) -> EngineState:
    performed = (prev.performed if prev else ()) + ((action_id,) if action_id else ())
    state = EngineState(
        stage=w.stage,
        flags=tuple(sorted(w.flags)),
        score=w.score,
        evidence=tuple(w.evidence),
        performed=performed,
        choices=dict(w.choices),
        mistakes=tuple(w.mistakes),
        finished=w.finished,
        outcome=None,
        step=(prev.step + 1) if prev else 0,
    )
    if state.finished:
        state = state.model_copy(update={"outcome": evaluate(scenario, state).outcome})
    return state


def initial_state(scenario: Scenario) -> tuple[EngineState, list[Event]]:
    """First stage of the scenario plus its on_enter effects."""
    w = _Work(scenario, None)
    first = w.stages[w.stage]
    w.events.append(StageChangedEvent(stage=first.id, title_key=first.title_key))
    _run_effects(w, first.on_enter)
    _settle(w)
    return _freeze(scenario, w, None, None), w.events


def _is_available(action: Action, state: EngineState) -> bool:
    return eval_condition(action.requires, state) and (
        action.repeatable or action.id not in state.performed
    )


def available_actions(scenario: Scenario, state: EngineState) -> list[AvailableAction]:
    """Actions the player can take now (empty when finished)."""
    if state.finished:
        return []
    stage = next(st for st in scenario.stages if st.id == state.stage)
    decisions = {d.decision_id: d for d in scenario.decisions}
    out: list[AvailableAction] = []
    for a in stage.actions:
        if not _is_available(a, state):
            continue
        options = None
        if a.kind == "decision":
            dp = decisions.get(a.decision_id or "")
            if dp is None:
                raise ScenarioError(f"unknown decision '{a.decision_id}'")
            options = tuple(OptionView(id=o.id, label_key=o.label_key) for o in dp.options)
        out.append(
            AvailableAction(
                id=a.id,
                kind=a.kind,
                label_key=a.label_key,
                target_character=a.target_character,
                evidence_id=a.evidence_id,
                decision_id=a.decision_id,
                hint_citation_ids=tuple(a.hint_citation_ids),
                options=options,
            )
        )
    return out


def apply(
    scenario: Scenario, state: EngineState, action_id: str, params: dict | None = None
) -> tuple[EngineState, list[Event]]:
    """Apply one action; returns the new state and the events it produced."""
    if state.finished:
        raise SessionFinished()
    stage = next((st for st in scenario.stages if st.id == state.stage), None)
    if stage is None:
        raise ScenarioError(f"unknown stage '{state.stage}'")
    action = next((a for a in stage.actions if a.id == action_id), None)
    if action is None or not _is_available(action, state):
        raise IllegalAction(action_id, state.stage)

    w = _Work(scenario, state)
    if action.kind == "decision":
        dp = next((d for d in scenario.decisions if d.decision_id == action.decision_id), None)
        if dp is None:
            raise ScenarioError(f"unknown decision '{action.decision_id}'")
        option = (params or {}).get("option")
        if option not in {o.id for o in dp.options}:
            raise IllegalAction(action_id, state.stage)
        w.choices[dp.decision_id] = option
        _run_effects(w, action.effects)
        _run_effects(w, dp.consequences.get(option, []))
        if option in dp.score:
            _add_score(w, dp.score[option])
    else:
        _run_effects(w, action.effects)
    _settle(w)
    return _freeze(scenario, w, state, action_id), w.events


def replay(scenario: Scenario, actions: list[LoggedAction]) -> tuple[EngineState, list[Event]]:
    """Fold the action log; returns the final state and the last step's events."""
    state, events = initial_state(scenario)
    for la in actions:
        state, events = apply(scenario, state, la.action_id, la.params)
    return state, events
