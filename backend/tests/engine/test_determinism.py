from app.game_engine import EngineState, apply, initial_state, replay
from tests.engine.conftest import BEST, play, to_log


def test_replay_100_times_identical(scenario):
    log = to_log(BEST)
    first = replay(scenario, log)
    for _ in range(100):
        assert replay(scenario, log) == first


def test_replay_equals_sequential_apply(scenario):
    state, _, per_step = play(scenario, BEST)
    r_state, r_events = replay(scenario, to_log(BEST))
    assert r_state == state
    assert r_events == per_step[-1]


def test_replay_empty_log_is_initial(scenario):
    assert replay(scenario, []) == initial_state(scenario)


def test_state_is_json_serializable(scenario):
    state, _, _ = play(scenario, BEST)
    assert EngineState.model_validate_json(state.model_dump_json()) == state
    # resuming from a serialized state gives the same result as continuing
    mid, _, _ = play(scenario, BEST[:10])
    restored = EngineState.model_validate_json(mid.model_dump_json())
    assert apply(scenario, restored, BEST[10][0], BEST[10][1]) == apply(scenario, mid, BEST[10][0], BEST[10][1])
