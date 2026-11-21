"""Static scenario checks and collectors of text keys / citation ids."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator
from typing import Any

from app.game_engine.engine import RESULTS
from app.schemas.scenario import OUTCOME_BEST, Condition, Effect, Scenario

NARRATOR = "narrator"


def iter_text_keys(data: Any) -> Iterator[str]:
    """Yield every text key in a dumped model: values of `*_key` and items of `*_keys`."""
    if isinstance(data, dict):
        for k, v in data.items():
            if k.endswith("_key") and isinstance(v, str):
                yield v
            elif k.endswith("_keys") and isinstance(v, list):
                yield from (x for x in v if isinstance(x, str))
            elif k.endswith("_keys") and isinstance(v, dict):
                yield from (x for x in v.values() if isinstance(x, str))
            else:
                yield from iter_text_keys(v)
    elif isinstance(data, list):
        for item in data:
            yield from iter_text_keys(item)


def _mentioned_citations(data: Any) -> Iterator[str]:
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "citation_id" and isinstance(v, str):
                yield v
            elif k.endswith("citation_ids") and isinstance(v, list):
                yield from (x for x in v if isinstance(x, str))
            elif k != "citations":
                yield from _mentioned_citations(v)
    elif isinstance(data, list):
        for item in data:
            yield from _mentioned_citations(item)


def _dump(scenario: Scenario) -> dict:
    return scenario.model_dump(mode="json", by_alias=True)


def collect_text_keys(scenario: Scenario) -> set[str]:
    """All text keys used by the scenario."""
    return set(iter_text_keys(_dump(scenario)))


def collect_citation_ids(scenario: Scenario) -> set[str]:
    """Declared `citations` plus every citation id mentioned anywhere in the scenario."""
    return set(scenario.citations) | set(_mentioned_citations(_dump(scenario)))


# --------------------------------------------------------------------------- walkers


def _walk_condition(c: Condition) -> Iterator[Condition]:
    yield c
    name, val = c.active()
    if name == "not_":
        yield from _walk_condition(val)
    elif name in ("all_", "any_"):
        for sub in val:
            yield from _walk_condition(sub)


def _conditions(sc: Scenario) -> Iterator[tuple[str, Condition]]:
    for st in sc.stages:
        for t in st.transitions:
            yield f"stage {st.id} transition to {t.to}", t.when
        for a in st.actions:
            yield f"action {a.id} requires", a.requires
    for d in sc.decisions:
        for o in d.options:
            if o.when is not None:
                yield f"decision {d.decision_id} option {o.id} when", o.when
    for i, r in enumerate(sc.evaluation_rules):
        yield f"evaluation_rules[{i}]", r.when
    for i, r in enumerate(sc.mistake_rules):
        yield f"mistake_rules[{i}]", r.when


def _effect_lists(sc: Scenario) -> Iterator[tuple[str, list[Effect]]]:
    for st in sc.stages:
        yield f"stage {st.id} on_enter", st.on_enter
        for a in st.actions:
            yield f"action {a.id} effects", a.effects
    for d in sc.decisions:
        for opt, effs in d.consequences.items():
            yield f"decision {d.decision_id} consequences[{opt}]", effs


def _dups(label: str, ids: list[str]) -> list[str]:
    return [f"duplicate {label} id '{i}'" for i, n in Counter(ids).items() if n > 1]


def _check_graph(sc: Scenario, stage_ids: set[str]) -> list[str]:
    errs: list[str] = []
    decisions = {d.decision_id: d for d in sc.decisions}
    edges: dict[str, set[str]] = {}
    for st in sc.stages:
        out = {t.to for t in st.transitions}
        lists = [st.on_enter] + [a.effects for a in st.actions]
        for a in st.actions:
            dp = decisions.get(a.decision_id or "")
            if dp:
                lists += list(dp.consequences.values())
        for effs in lists:
            out |= {e.goto for e in effs if e.goto is not None}
        edges.setdefault(st.id, set()).update(out & stage_ids)

    first = sc.stages[0].id
    seen, todo = {first}, [first]
    while todo:
        for nxt in edges.get(todo.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    errs += [f"stage '{s}' is unreachable from '{first}'" for s in sorted(stage_ids - seen)]

    if RESULTS in stage_ids:
        rev: dict[str, set[str]] = {}
        for src, dsts in edges.items():
            for d in dsts:
                rev.setdefault(d, set()).add(src)
        can, todo = {RESULTS}, [RESULTS]
        while todo:
            for prev in rev.get(todo.pop(), ()):
                if prev not in can:
                    can.add(prev)
                    todo.append(prev)
        errs += [f"stage '{s}' cannot reach {RESULTS}" for s in sorted(stage_ids - can)]
    return errs


def validate_scenario(sc: Scenario) -> list[str]:
    """Static checks. Returns human-readable errors; empty list means OK."""
    errs: list[str] = []
    stage_ids = {s.id for s in sc.stages}
    actions = [a for s in sc.stages for a in s.actions]
    char_ids = {c.id for c in sc.characters}
    speakers = char_ids | {NARRATOR}
    ev_ids = {e.id for e in sc.evidence}
    fact_ids = {f.id for f in sc.facts}
    dec_ids = {d.decision_id for d in sc.decisions}
    cats = set(sc.mistake_categories)
    cites = set(sc.citations)

    # unique ids
    errs += _dups("stage", [s.id for s in sc.stages])
    errs += _dups("action", [a.id for a in actions])
    errs += _dups("character", [c.id for c in sc.characters])
    errs += _dups("evidence", [e.id for e in sc.evidence])
    errs += _dups("fact", [f.id for f in sc.facts])
    errs += _dups("decision", [d.decision_id for d in sc.decisions])
    errs += _dups("npc question", [q.question_id for q in sc.npc_questions])
    for d in sc.decisions:
        errs += _dups(f"option of decision '{d.decision_id}'", [o.id for o in d.options])

    # structure
    if sc.stages[0].id == RESULTS:
        errs.append(f"first stage must not be {RESULTS}")
    if RESULTS not in stage_ids:
        errs.append(f"stage {RESULTS} is missing")
    else:
        res = next(s for s in sc.stages if s.id == RESULTS)
        if res.actions or res.transitions:
            errs.append(f"stage {RESULTS} must have no actions and no transitions")
    if not sc.evaluation_rules:
        errs.append("evaluation_rules is empty")
    else:
        last = sc.evaluation_rules[-1].when
        if last.active() != ("always", True):
            errs.append('the last evaluation rule must be {"always": true}')

    # references
    if sc.intro.player_role.character_id not in char_ids:
        errs.append(f"intro.player_role: unknown character '{sc.intro.player_role.character_id}'")
    facts_by_id = {f.id: f for f in sc.facts}
    for q in sc.npc_questions:
        if q.character_id not in char_ids:
            errs.append(f"npc_question '{q.question_id}': unknown character '{q.character_id}'")
        for s_id in q.stages:
            if s_id not in stage_ids:
                errs.append(f"npc_question '{q.question_id}': unknown stage '{s_id}'")
            elif s_id == RESULTS:
                errs.append(f"npc_question '{q.question_id}': stage {RESULTS} is not allowed")
        for f_id in q.fact_ids:
            fact = facts_by_id.get(f_id)
            if fact is None:
                errs.append(f"npc_question '{q.question_id}': unknown fact '{f_id}'")
            elif q.character_id not in fact.known_by:
                errs.append(
                    f"npc_question '{q.question_id}': character '{q.character_id}' does not know fact '{f_id}'"
                )
    for e in sc.evidence:
        for f in e.facts:
            if f not in fact_ids:
                errs.append(f"evidence '{e.id}': unknown fact '{f}'")
    for st in sc.stages:
        for t in st.transitions:
            if t.to not in stage_ids:
                errs.append(f"stage '{st.id}': transition to unknown stage '{t.to}'")
        for a in st.actions:
            if a.target_character and a.target_character not in speakers:
                errs.append(f"action '{a.id}': unknown target_character '{a.target_character}'")
            if a.evidence_id and a.evidence_id not in ev_ids:
                errs.append(f"action '{a.id}': unknown evidence '{a.evidence_id}'")
            if a.decision_id:
                if a.decision_id not in dec_ids:
                    errs.append(f"action '{a.id}': unknown decision '{a.decision_id}'")
                else:
                    dp = next(d for d in sc.decisions if d.decision_id == a.decision_id)
                    if dp.stage != st.id:
                        errs.append(
                            f"action '{a.id}' is on stage '{st.id}' but decision "
                            f"'{dp.decision_id}' is on stage '{dp.stage}'"
                        )
    for d in sc.decisions:
        opts = {o.id for o in d.options}
        if d.stage not in stage_ids:
            errs.append(f"decision '{d.decision_id}': unknown stage '{d.stage}'")
        if d.best == OUTCOME_BEST:
            outcomes = {r.outcome for r in sc.evaluation_rules}
            for o in sorted(opts - outcomes):
                errs.append(f"decision '{d.decision_id}': option '{o}' is not an outcome id (best is {OUTCOME_BEST})")
            if d.kind != "prediction":
                errs.append(f"decision '{d.decision_id}': best {OUTCOME_BEST} requires kind 'prediction'")
        elif d.best not in opts:
            errs.append(f"decision '{d.decision_id}': best '{d.best}' is not an option")
        if d.outcome_score and d.best != OUTCOME_BEST:
            errs.append(f"decision '{d.decision_id}': outcome_score needs best {OUTCOME_BEST}")
        for key in list(d.consequences) + list(d.score) + list(d.score_reason_keys):
            if key not in opts:
                errs.append(f"decision '{d.decision_id}': consequences/score key '{key}' is not an option")

    for where, effs in _effect_lists(sc):
        for i, e in enumerate(effs):
            name, val = e.active()
            if name == "goto":
                if val not in stage_ids:
                    errs.append(f"{where}: goto unknown stage '{val}'")
                if i != len(effs) - 1:
                    errs.append(f"{where}: goto must be the last effect")
            elif name == "say" and val.speaker not in speakers:
                errs.append(f"{where}: unknown speaker '{val.speaker}'")
            elif name == "react" and val.character not in char_ids:
                errs.append(f"{where}: unknown character '{val.character}'")
            elif name == "add_evidence" and val not in ev_ids:
                errs.append(f"{where}: add_evidence unknown evidence '{val}'")
            elif name == "mistake" and val.category not in cats:
                errs.append(f"{where}: unknown mistake category '{val.category}'")

    for where, root in _conditions(sc):
        for c in _walk_condition(root):
            name, val = c.active()
            if name == "chose":
                dp = next((d for d in sc.decisions if d.decision_id == val.decision_id), None)
                if dp is None:
                    errs.append(f"{where}: chose unknown decision '{val.decision_id}'")
                elif val.option not in {o.id for o in dp.options}:
                    errs.append(f"{where}: chose unknown option '{val.option}' of '{val.decision_id}'")
    for i, r in enumerate(sc.mistake_rules):
        if r.mistake.category not in cats:
            errs.append(f"mistake_rules[{i}]: unknown category '{r.mistake.category}'")
    for cat in sc.recommendations:
        if cat not in cats:
            errs.append(f"recommendations: unknown category '{cat}'")

    # graph
    errs += _check_graph(sc, stage_ids)

    # citations
    for c in sorted(set(_mentioned_citations(_dump(sc))) - cites):
        errs.append(f"citation '{c}' is used but not listed in scenario.citations")
    return errs
