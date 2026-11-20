import random

import pytest

from app.game_engine import apply, available_actions, initial_state

MAX_STEPS = 200


@pytest.mark.parametrize("chunk", range(5))
def test_random_walks_reach_results(scenario, chunk):
    for seed in range(chunk * 100, chunk * 100 + 100):
        rng = random.Random(seed)
        state, _ = initial_state(scenario)
        steps = 0
        while not state.finished:
            actions = available_actions(scenario, state)
            assert actions, f"seed {seed}: dead end on {state.stage}"
            a = rng.choice(actions)
            params = {"option": rng.choice(a.options).id} if a.kind == "decision" else None
            state, _ = apply(scenario, state, a.id, params)
            steps += 1
            assert steps <= MAX_STEPS, f"seed {seed}: no RESULTS within {MAX_STEPS} steps"
        assert state.stage == "RESULTS" and state.outcome
        assert 0 <= state.step <= MAX_STEPS
