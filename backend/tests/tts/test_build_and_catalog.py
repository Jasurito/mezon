"""Build into a folder, serve it like the bucket, and check what the API gets."""

import json

import httpx
import pytest

from app.config import Settings
from app.game_engine.state import SayEvent as EngineSay
from app.services.presenter import present_events
from app.tts.build import BuildError, build_scenario
from app.tts.catalog import attach_audio, audio_for, manifest_path
from app.tts.lines import spoken_lines

from .conftest import fake_encode

BASE = "http://storage.test/mezon-audio"
PUBLIC = "https://mezon.test/audio"


def _serve(out_dir):
    """httpx transport that serves the build folder like the bucket does."""

    def handler(request: httpx.Request) -> httpx.Response:
        rel = request.url.path.removeprefix("/mezon-audio/")
        f = out_dir / rel
        return httpx.Response(200, content=f.read_bytes()) if f.is_file() else httpx.Response(404)

    return httpx.MockTransport(handler)


def _attach(loaded, out_dir):
    settings = Settings(AUDIO_PUBLIC_BASE_URL=PUBLIC, AUDIO_MANIFEST_BASE_URL=BASE)
    return attach_audio({loaded.scenario.scenario_id: loaded}, settings, transport=_serve(out_dir))


def test_build_layout_and_manifest(loaded, synth, tmp_path):
    report = build_scenario(loaded, tmp_path, synth, fake_encode)
    sid = loaded.scenario.scenario_id
    n = len(spoken_lines(loaded.scenario))
    assert report.written == 2 * n  # ru + uz
    m = json.loads((tmp_path / manifest_path(sid, "uz")).read_text())
    entry = m["lines"]["judge/line.case_review"]
    assert entry["path"] == f"scenarios/{sid}/uz/judge/line.case_review.mp3"
    assert entry["voice"] == "uz-uzb_0" and entry["duration_ms"] == 100
    assert (tmp_path / entry["path"]).read_bytes().startswith(b"MP3")
    # uzb_0 reads only Cyrillic: no Latin letters reach it
    assert all(not any("a" <= c <= "z" for c in t.lower()) for s, t in synth.calls if s == "uzb_0")


def test_rebuild_only_changed_lines(loaded, synth, tmp_path):
    build_scenario(loaded, tmp_path, synth, fake_encode)
    synth.calls.clear()
    report = build_scenario(loaded, tmp_path, synth, fake_encode)
    assert report.written == 0 and synth.calls == []

    loaded.texts["ru"]["line.case_review"] = "Новый текст судьи."
    report = build_scenario(loaded, tmp_path, synth, fake_encode)
    assert report.written == 1 and synth.calls == [("eugene", "Новый текст судьи.")]


def test_unknown_name_stops_the_build(loaded, synth, tmp_path):
    loaded.texts["ru"]["char.plaintiff.name"] = "Зумрад Х."
    loaded.texts["uz-Latn"]["char.plaintiff.name"] = "Zumrad X."
    with pytest.raises(BuildError, match="plaintiff"):
        build_scenario(loaded, tmp_path, synth, fake_encode)
    loaded.scenario.characters[2].voice = "female"  # plaintiff
    build_scenario(loaded, tmp_path, synth, fake_encode)


def test_catalog_urls_and_stale_text(loaded, synth, tmp_path):
    build_scenario(loaded, tmp_path, synth, fake_encode)
    assert _attach(loaded, tmp_path) == 2 * len(spoken_lines(loaded.scenario))

    ru = audio_for(loaded, "judge", "line.case_review", "ru")
    sid = loaded.scenario.scenario_id
    assert ru is not None and ru.url.startswith(f"{PUBLIC}/scenarios/{sid}/ru/judge/line.case_review.mp3?v=")
    # uz-Latn and uz-Cyrl sessions hear the same recording
    assert audio_for(loaded, "judge", "line.case_review", "uz-Cyrl") == audio_for(
        loaded, "judge", "line.case_review", "uz-Latn"
    )
    # text edited after the build: no audio instead of the old recording
    loaded.texts["ru"]["line.case_review"] = "Изменённый текст."
    assert audio_for(loaded, "judge", "line.case_review", "ru") is None


def test_storage_down_means_text_only(loaded):
    def boom(request):
        raise httpx.ConnectError("down")

    settings = Settings(AUDIO_PUBLIC_BASE_URL=PUBLIC, AUDIO_MANIFEST_BASE_URL=BASE)
    assert attach_audio({"x": loaded}, settings, transport=httpx.MockTransport(boom)) == 0
    assert audio_for(loaded, "judge", "line.case_review", "ru") is None


def test_audio_off_without_public_url(loaded, synth, tmp_path):
    build_scenario(loaded, tmp_path, synth, fake_encode)
    settings = Settings(AUDIO_PUBLIC_BASE_URL=None, AUDIO_MANIFEST_BASE_URL=BASE)
    assert attach_audio({"x": loaded}, settings, transport=_serve(tmp_path)) == 0


def test_presenter_adds_audio_to_say_events(loaded, synth, tmp_path):
    build_scenario(loaded, tmp_path, synth, fake_encode)
    _attach(loaded, tmp_path)
    events = present_events(loaded, [EngineSay(speaker="judge", text_key="line.case_review")], "ru")
    assert events[0].audio_url and events[0].audio_duration_ms == 100
    # a line that was never built: text only
    events = present_events(loaded, [EngineSay(speaker="judge", text_key="no.such.key")], "ru")
    assert events[0].audio_url is None
