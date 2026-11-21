from app.i18n.translit import lat_to_cyr_display
"""Презентер: чистые функции, без БД."""

import uuid

from app.game_engine import apply, initial_state
from app.i18n import translate
from app.scenarios import load_scenario_dir
from app.services.presenter import build_game_state
from tests.engine.conftest import BEST, FIXTURES, LOSS, play

SID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def _loaded():
    return load_scenario_dir(FIXTURES / "test_consumer")


def _state(path):
    loaded = _loaded()
    state, _, per_step = play(loaded.scenario, path)
    return loaded, state, per_step[-1]


def test_initial_state_stage_and_evidence():
    loaded = _loaded()
    st, events = initial_state(loaded.scenario)
    gs = build_game_state(loaded, st, events, SID, "ru")
    assert (gs.stage, gs.stage_index, gs.stage_count) == ("INTRO", 1, len(loaded.scenario.stages))
    assert gs.evidence == []  # материалы дела не видны на первом этапе
    assert gs.max_score == 100 and gs.finished is False
    assert gs.legal_date == loaded.scenario.legal_date
    assert gs.available_actions[0].action_id == "enter_courtroom"
    assert gs.stage_title and not gs.stage_title.startswith("stage.")


def test_evidence_visible_from_second_stage_with_flags():
    loaded = _loaded()
    st, events, = initial_state(loaded.scenario)
    st, events = apply(loaded.scenario, st, "enter_courtroom")
    st, events = apply(loaded.scenario, st, "review_receipt")
    gs = build_game_state(loaded, st, events, SID, "ru")
    assert gs.stage_index == 2
    case_file = [e.id for e in loaded.scenario.evidence if e.in_case_file]
    assert [e.id for e in gs.evidence][: len(case_file)] == case_file
    by_id = {e.id: e for e in gs.evidence}
    assert by_id["receipt"].reviewed is True and by_id["receipt"].presented is False
    assert by_id["contract"].reviewed is False


def test_presented_flag_and_added_evidence_order():
    loaded, state, events = _state(BEST)
    gs = build_game_state(loaded, state, events, SID, "ru")
    by_id = {e.id: e for e in gs.evidence}
    assert by_id["receipt"].presented and by_id["receipt"].reviewed
    # улики, добавленные эффектами, идут после материалов дела
    in_file = [e.id for e in loaded.scenario.evidence if e.in_case_file]
    assert [e.id for e in gs.evidence][: len(in_file)] == in_file
    assert list(state.evidence) == [i for i in (e.id for e in gs.evidence) if i in state.evidence]
    assert len({e.id for e in gs.evidence}) == len(gs.evidence)


def test_finished_state_has_no_actions():
    loaded, state, events = _state(BEST)
    gs = build_game_state(loaded, state, events, SID, "ru")
    assert gs.finished and gs.available_actions == []
    assert gs.stage_index == gs.stage_count == len(loaded.scenario.stages)
    assert gs.score == 100


def test_mistake_events_hidden_unless_revealed():
    loaded, state, _ = _state(LOSS)
    all_events = [e for step in play(loaded.scenario, LOSS)[2] for e in step]
    assert any(e.type == "mistake" for e in all_events)
    assert loaded.scenario.reveal_mistakes is False
    shown = [e for step in play(loaded.scenario, LOSS)[2]
             for e in build_game_state(loaded, state, step, SID, "ru").events]
    assert not any(e.type == "mistake" for e in shown)

    loaded.scenario.reveal_mistakes = True
    shown = [e for step in play(loaded.scenario, LOSS)[2]
             for e in build_game_state(loaded, state, step, SID, "ru").events]
    mistakes = [e for e in shown if e.type == "mistake"]
    assert mistakes and all(not m.text.startswith("mistake.") for m in mistakes)


def test_events_translated_and_typed():
    loaded, _, events = _state(BEST)
    gs = build_game_state(loaded, _state(BEST)[1], events, SID, "uz-Latn")
    types = {e.type for e in gs.events}
    assert "stage_changed" in types
    for e in gs.events:
        if e.type == "say":
            assert e.text != "" and not e.text.startswith("line.")
        if e.type == "stage_changed":
            assert not e.title.startswith("stage.")


def test_decision_options_translated():
    loaded, state, events = _state(BEST[:-1])
    gs = build_game_state(loaded, state, events, SID, "ru")
    dec = [a for a in gs.available_actions if a.kind == "decision"]
    assert len(dec) == 1
    ids = [o.id for o in dec[0].options]
    assert {"refund", "reduce_price"} <= set(ids)
    assert all(not o.label.startswith(("opt.", "dec.")) and o.label for o in dec[0].options)
    assert all(a.options is None for a in gs.available_actions if a.kind != "decision")


def test_translate_fallback_chain():
    loaded = _loaded()
    key = "act.enter_courtroom"
    ru = loaded.texts["ru"][key]
    lat = loaded.texts["uz-Latn"][key]
    # uz-Cyrl в фикстуре отсутствует: берётся uz-Latn в кириллической транслитерации, затем ru
    assert translate(loaded, key, "uz-Cyrl") == loaded.texts["uz-Cyrl"].get(key, lat_to_cyr_display(lat))
    loaded.texts["uz-Cyrl"].pop(key, None)
    assert translate(loaded, key, "uz-Cyrl") == lat_to_cyr_display(lat)
    loaded.texts["uz-Latn"].pop(key)
    assert translate(loaded, key, "uz-Cyrl") == ru
    assert translate(loaded, key, "uz-Latn") == ru
    loaded.texts["ru"].pop(key)
    assert translate(loaded, key, "ru") == key
