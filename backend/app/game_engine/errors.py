"""Engine exceptions."""

from __future__ import annotations


class IllegalAction(Exception):
    """The action is not available in the current state."""

    def __init__(self, action_id: str, stage: str) -> None:
        super().__init__(f"action '{action_id}' is not available on stage '{stage}'")
        self.action_id = action_id
        self.stage = stage


class SessionFinished(Exception):
    """The game is already finished; no more actions are accepted."""


class ScenarioError(Exception):
    """The scenario is internally inconsistent (should be caught by validate_scenario)."""
