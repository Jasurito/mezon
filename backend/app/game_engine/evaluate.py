"""Outcome computation for the results screen."""

from __future__ import annotations

from app.game_engine.conditions import eval_condition
from app.game_engine.errors import ScenarioError
from app.game_engine.state import DecisionResult, EngineState, Outcome
from app.schemas.scenario import Mistake, Recommendation, Scenario


def _chosen(scenario: Scenario, decision, state: EngineState) -> str | None:
    """Explicit choice, else the first option whose `when` holds, else None."""
    if decision.decision_id in state.choices:
        return state.choices[decision.decision_id]
    for opt in decision.options:
        if opt.when is not None and eval_condition(opt.when, state):
            return opt.id
    return None


def evaluate(scenario: Scenario, state: EngineState) -> Outcome:
    """Compute the outcome from the (usually final) state. Pure."""
    rule = next((r for r in scenario.evaluation_rules if eval_condition(r.when, state)), None)
    if rule is None:
        raise ScenarioError("no evaluation rule matched")

    decisions: list[DecisionResult] = []
    for d in scenario.decisions:
        chosen = _chosen(scenario, d, state)
        decisions.append(
            DecisionResult(
                decision_id=d.decision_id,
                stage=d.stage,
                chosen=chosen,
                best=d.best,
                correct=chosen == d.best,
                explanation_key=d.explanation_key,
                citation_ids=tuple(d.citation_ids),
            )
        )

    mistakes: list[Mistake] = []
    seen: set[str] = set()
    triggered = list(state.mistakes) + [
        r.mistake for r in scenario.mistake_rules if eval_condition(r.when, state)
    ]
    for m in triggered:
        if m.title_key not in seen:
            seen.add(m.title_key)
            mistakes.append(m)

    cites = {c for d in decisions for c in d.citation_ids} | {
        c for m in mistakes for c in m.citation_ids
    }
    recs: list[Recommendation] = []
    for cat in dict.fromkeys(m.category for m in mistakes):
        if cat in scenario.recommendations:
            recs.append(scenario.recommendations[cat])

    rate = sum(d.correct for d in decisions) / len(decisions) if decisions else 0.0
    return Outcome(
        outcome=rule.outcome,
        title_key=rule.title_key,
        ruling_key=rule.ruling_key,
        score=state.score,
        max_score=scenario.max_score,
        decisions=tuple(decisions),
        correct_decision_rate=rate,
        mistakes=tuple(mistakes),
        citation_ids=tuple(sorted(cites)),
        recommendations=tuple(recs),
    )
