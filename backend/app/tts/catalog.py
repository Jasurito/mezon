"""Runtime side: audio manifests from object storage -> ``audio_url`` of a spoken line.

At startup ``attach_audio`` reads ``scenarios/<id>/<lang>/manifest.json`` for every scenario over plain HTTP
(AUDIO_MANIFEST_BASE_URL) and keeps it on the LoadedScenario. ``audio_for`` returns a line's URL only when the
recording matches the current text and voice (same hash): an edited text without a rebuild plays no audio rather
than the old recording. Storage down or AUDIO_PUBLIC_BASE_URL empty = the game runs text only.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from app.config import Settings
from app.scenarios.loader import LoadedScenario
from app.tts.voices import SOURCE_LOCALE, Lang, lang_of, line_hash, voice_for

log = logging.getLogger("adolat.tts")

LANGS: tuple[Lang, ...] = ("ru", "uz")


@dataclass(frozen=True)
class AudioRef:
    url: str
    duration_ms: int


def manifest_path(scenario_id: str, lang: str) -> str:
    return f"scenarios/{scenario_id}/{lang}/manifest.json"


def line_path(scenario_id: str, lang: str, speaker: str, text_key: str) -> str:
    return f"scenarios/{scenario_id}/{lang}/{speaker}/{text_key}.mp3"


def attach_audio(
    registry: dict[str, LoadedScenario], settings: Settings, transport: httpx.BaseTransport | None = None
) -> int:
    """Load the manifests into ``loaded.audio``; returns the number of lines with audio."""
    for loaded in registry.values():
        loaded.audio = {}
    if not settings.AUDIO_PUBLIC_BASE_URL or not settings.AUDIO_MANIFEST_BASE_URL:
        return 0
    base = settings.AUDIO_MANIFEST_BASE_URL.rstrip("/")
    public = settings.AUDIO_PUBLIC_BASE_URL.rstrip("/")
    total = 0
    with httpx.Client(timeout=settings.AUDIO_MANIFEST_TIMEOUT, transport=transport) as client:
        for sid, loaded in registry.items():
            for lang in LANGS:
                try:
                    resp = client.get(f"{base}/{manifest_path(sid, lang)}")
                except httpx.HTTPError as exc:
                    log.warning("audio storage unavailable (%s): the game runs without speech", exc.__class__.__name__)
                    return total
                if resp.status_code != 200:
                    continue  # nothing built for this scenario / language yet
                try:
                    lines = {
                        k: {**v, "url": f"{public}/{v['path']}?v={v['hash']}"} for k, v in resp.json()["lines"].items()
                    }
                except (ValueError, KeyError, TypeError, AttributeError):
                    log.warning("broken audio manifest %s", manifest_path(sid, lang))
                    continue
                loaded.audio[lang] = lines
                total += len(lines)
    log.info("audio: %d lines in %d scenarios", total, sum(1 for s in registry.values() if s.audio))
    return total


def audio_for(loaded: LoadedScenario, speaker: str, text_key: str, locale: str) -> AudioRef | None:
    lang = lang_of(locale)
    entry = loaded.audio.get(lang, {}).get(f"{speaker}/{text_key}")
    if not entry:
        return None
    text = loaded.texts.get(SOURCE_LOCALE[lang], {}).get(text_key)
    if not text or entry.get("hash") != line_hash(voice_for(loaded, speaker, lang), text):
        return None
    return AudioRef(entry["url"], int(entry.get("duration_ms", 0)))


def audio_lines(loaded: LoadedScenario) -> int:
    return sum(len(v) for v in loaded.audio.values())
