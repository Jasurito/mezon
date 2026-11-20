from app.game_engine import evaluate
from tests.engine.conftest import BEST, LOSS, PARTIAL, play


def test_best_path_gives_max_score(scenario):
    state, _, _ = play(scenario, BEST)
    assert state.finished and state.stage == "RESULTS"
    assert state.score == scenario.max_score == 100
    assert state.outcome == "claim_granted"
    out = evaluate(scenario, state)
    assert out.correct_decision_rate == 1.0 and out.mistakes == ()
    assert [d.chosen for d in out.decisions] == ["receipt_and_chat", "request_expertise", "refund"]


def test_partial_path(scenario):
    state, _, _ = play(scenario, PARTIAL)
    assert state.outcome == "claim_partially_granted"
    assert state.score == 40
    out = evaluate(scenario, state)
    assert [d.chosen for d in out.decisions] == ["receipt_only", "none", "refund"]
    assert round(out.correct_decision_rate, 2) == 0.33
    assert [m.title_key for m in out.mistakes] == ["mistake.no_expertise.title"]
    assert out.citation_ids == tuple(sorted(set(out.citation_ids)))
    assert [r.topic_key for r in out.recommendations] == ["rec.procedure"]


def test_loss_path(scenario):
    state, _, per_step = play(scenario, LOSS)
    assert state.outcome == "claim_denied"
    assert state.score == 4  # 3 reviews (6) - 2 irrelevant motion + 0 reduce_price
    out = evaluate(scenario, state)
    cats = {m.category for m in out.mistakes}
    assert cats == {"procedure", "evidence", "substantive"}
    assert len({m.title_key for m in out.mistakes}) == len(out.mistakes)
    types = {e.type for e in per_step[-1]}
    assert {"say", "stage_changed", "score"} <= types


def test_events_use_keys_not_text(scenario):
    _, events, _ = play(scenario, BEST)
    for e in events:
        if e.type == "say":
            assert e.text_key.startswith(("line.",))
