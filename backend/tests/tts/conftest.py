"""Speech fixtures: the test_consumer scenario, a fake synthesizer and a fake MP3 encoder (no torch, no network)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.scenarios.loader import LoadedScenario, load_scenario_dir

SCENARIO_DIR = Path(__file__).parent.parent / "fixtures" / "scenarios" / "test_consumer"


@pytest.fixture
def loaded() -> LoadedScenario:
    return load_scenario_dir(SCENARIO_DIR)


class FakeSynth:
    """100 ms of silence per call; remembers what it was asked to say."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def synthesize(self, text, voice) -> bytes:
        self.calls.append((voice.speaker, text))
        return b"\x00\x00" * 2400  # 0.1 s at 24 kHz


def fake_encode(pcm: bytes, sample_rate: int) -> bytes:
    return b"MP3" + len(pcm).to_bytes(4, "big")


@pytest.fixture
def synth() -> FakeSynth:
    return FakeSynth()
