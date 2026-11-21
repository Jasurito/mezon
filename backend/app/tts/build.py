"""Scenario texts -> MP3 files + manifests in a local folder laid out exactly like the bucket:

    <out>/scenarios/<scenario_id>/<lang>/manifest.json
    <out>/scenarios/<scenario_id>/<lang>/<speaker>/<text_key>.mp3

A line whose hash (voice + text) is unchanged and whose file exists is not synthesized again.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from app.scenarios.loader import LoadedScenario
from app.tts.catalog import LANGS, line_path, manifest_path
from app.tts.lines import spoken_lines
from app.tts.synth import SAMPLE_RATE, Synth
from app.tts.text import prepare
from app.tts.voices import SOURCE_LOCALE, Lang, infer_speaker, line_hash, voice_for


class BuildError(Exception):
    pass


@dataclass
class BuildReport:
    written: int = 0
    unchanged: int = 0
    removed: int = 0
    missing_text: list[str] = field(default_factory=list)  # "<scenario>/<lang>/<speaker>/<key>"
    with_digits: list[tuple[str, str, str]] = field(default_factory=list)  # (where, original, spoken)


def unknown_names(loaded: LoadedScenario) -> list[str]:
    """Speakers whose name looks like a person's but is not in app/tts/names.py and has no ``voice``."""
    speakers = {line.speaker for line in spoken_lines(loaded.scenario)}
    return sorted(s for s in speakers if infer_speaker(loaded, s).reason == "unknown_name")


def _load_manifest(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("lines", {})
    except (FileNotFoundError, ValueError):
        return {}


def build_scenario(
    loaded: LoadedScenario,
    out_dir: Path,
    synth: Synth,
    encode: Callable[[bytes, int], bytes],
    langs: tuple[Lang, ...] = LANGS,
    force: bool = False,
    report: BuildReport | None = None,
    progress: Callable[[str], None] = lambda _: None,
) -> BuildReport:
    report = report or BuildReport()
    sid = loaded.scenario.scenario_id
    if unknown := unknown_names(loaded):
        raise BuildError(
            f"{sid}: cannot tell the gender of {', '.join(unknown)} from the name. Add the first name to "
            f"app/tts/names.py or set \"voice\": \"male\"|\"female\" on the character in scenario.json."
        )
    lines = spoken_lines(loaded.scenario)
    for lang in langs:
        texts = loaded.texts.get(SOURCE_LOCALE[lang], {})
        mfile = out_dir / manifest_path(sid, lang)
        old = _load_manifest(mfile)
        entries: dict[str, dict] = {}
        for line in lines:
            key = f"{line.speaker}/{line.text_key}"
            text = texts.get(line.text_key)
            if not text:
                report.missing_text.append(f"{sid}/{lang}/{key}")
                continue
            voice = voice_for(loaded, line.speaker, lang)
            h = line_hash(voice, text)
            rel = line_path(sid, lang, line.speaker, line.text_key)
            mp3 = out_dir / rel
            prev = old.get(key)
            if not force and prev and prev.get("hash") == h and mp3.exists():
                entries[key] = prev
                report.unchanged += 1
                continue
            spoken = prepare(text, lang, voice)
            if re.search(r"\d", text):
                report.with_digits.append((f"{sid}/{lang}/{key}", text, spoken))
            progress(f"{sid}/{lang}/{key} [{voice.speaker}]")
            pcm = synth.synthesize(spoken, voice)
            data = encode(pcm, SAMPLE_RATE)
            mp3.parent.mkdir(parents=True, exist_ok=True)
            mp3.write_bytes(data)
            entries[key] = {
                "speaker": line.speaker,
                "text_key": line.text_key,
                "voice": voice.id,
                "path": rel,
                "hash": h,
                "duration_ms": round(len(pcm) / 2 / SAMPLE_RATE * 1000),
                "bytes": len(data),
            }
            report.written += 1

        # files of lines that no longer exist
        keep = {out_dir / e["path"] for e in entries.values()}
        lang_dir = mfile.parent
        if lang_dir.is_dir():
            for f in lang_dir.rglob("*.mp3"):
                if f not in keep:
                    f.unlink()
                    report.removed += 1
        mfile.parent.mkdir(parents=True, exist_ok=True)
        manifest = {
            "scenario_id": sid,
            "lang": lang,
            "built_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "lines": dict(sorted(entries.items())),
        }
        mfile.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
