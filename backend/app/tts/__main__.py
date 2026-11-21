"""Pre-generated speech: ``python -m app.tts <command>`` (docs/TTS.md). Needs the extra: pip install -e ".[tts]".

    voices       who speaks with which voice, and why (no ML needed)
    build        synthesize changed lines into TTS_OUT_DIR (default .tts-out)
    init-bucket  create the bucket and its public read policy (once per storage)
    upload       send changed files and the manifests to the bucket (--prune deletes removed lines)

Storage access (vm1: ssh -N -L 9000:127.0.0.1:9000 root@vm1.modeus.cc, keys from /etc/mezon/storage.env):
TTS_S3_ENDPOINT (default http://127.0.0.1:9000), TTS_S3_ACCESS_KEY, TTS_S3_SECRET_KEY, TTS_S3_BUCKET (mezon-audio).
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from pathlib import Path

from app.config import get_settings
from app.scenarios.registry import load_from_roots, scenario_roots
from app.tts.catalog import LANGS
from app.tts.lines import spoken_lines
from app.tts.voices import SOURCE_LOCALE, infer_speaker, voice_for


def _registry(args):
    settings = get_settings()
    if args.scenarios:
        settings = settings.model_copy(update={"SCENARIOS_DIR": args.scenarios})
    registry = load_from_roots(scenario_roots(settings))
    if args.scenario:
        missing = set(args.scenario) - set(registry)
        if missing:
            sys.exit(f"unknown scenario: {', '.join(sorted(missing))}")
        registry = {k: v for k, v in registry.items() if k in args.scenario}
    return registry


def cmd_voices(args) -> int:
    for sid, loaded in _registry(args).items():
        counts = Counter(line.speaker for line in spoken_lines(loaded.scenario))
        print(f"\n{sid}")
        for speaker, n in counts.most_common():
            sv = infer_speaker(loaded, speaker)
            name = next((loaded.texts["ru"].get(c.name_key, "") for c in loaded.scenario.characters if c.id == speaker), "")
            ru, uz = voice_for(loaded, speaker, "ru"), voice_for(loaded, speaker, "uz")
            flag = "  <-- add the name to app/tts/names.py or set voice" if sv.reason == "unknown_name" else ""
            print(f"  {speaker:16s} {name[:22]:22s} {sv.gender:6s} ({sv.reason:8s}) "
                  f"ru={ru.speaker:8s} uz={uz.speaker:8s} {n:3d} lines{flag}")
    return 0


def cmd_build(args) -> int:
    from app.tts.build import BuildError, BuildReport, build_scenario
    from app.tts.synth import SileroSynth, encode_mp3

    registry = _registry(args)
    synth = SileroSynth(Path(args.models), threads=args.threads)
    report = BuildReport()
    langs = (args.lang,) if args.lang else LANGS
    try:
        for loaded in registry.values():
            build_scenario(loaded, Path(args.out), synth, encode_mp3, langs, args.force, report,
                           progress=lambda s: print("  synth", s))
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"\nwritten {report.written}, unchanged {report.unchanged}, removed {report.removed} -> {args.out}")
    if report.missing_text:
        print(f"no text (skipped, check {'/'.join(SOURCE_LOCALE.values())} texts): {len(report.missing_text)}")
        for m in report.missing_text:
            print("  ", m)
    if report.with_digits:
        print("lines with numbers (listen to these, the words are generated):")
        for where, original, spoken in report.with_digits:
            print(f"  {where}\n     {original}\n  -> {spoken}")
    return 0


def _s3():
    from app.tts.storage import make_client

    key, secret = os.environ.get("TTS_S3_ACCESS_KEY"), os.environ.get("TTS_S3_SECRET_KEY")
    if not key or not secret:
        sys.exit("set TTS_S3_ACCESS_KEY and TTS_S3_SECRET_KEY (vm1: /etc/mezon/storage.env)")
    return make_client(os.environ.get("TTS_S3_ENDPOINT", "http://127.0.0.1:9000"), key, secret)


def cmd_init_bucket(args) -> int:
    from app.tts.storage import init_bucket

    init_bucket(_s3(), args.bucket)
    return 0


def cmd_upload(args) -> int:
    from app.tts.storage import upload

    stats = upload(_s3(), args.bucket, Path(args.out), prune=args.prune)
    print(", ".join(f"{k} {v}" for k, v in stats.items()))
    print("restart the backend so it reads the new manifests: ssh root@vm1.modeus.cc systemctl restart mezon-backend")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m app.tts", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    bucket = os.environ.get("TTS_S3_BUCKET", "mezon-audio")
    out = os.environ.get("TTS_OUT_DIR", ".tts-out")

    def scenarios(sp):
        sp.add_argument("--scenarios", help="scenario folders (default SCENARIOS_DIR), several joined with ':'")
        sp.add_argument("--scenario", action="append", help="only this scenario_id (repeatable)")

    sp = sub.add_parser("voices", help="who speaks with which voice")
    scenarios(sp)
    sp.set_defaults(fn=cmd_voices)

    sp = sub.add_parser("build", help="synthesize changed lines")
    scenarios(sp)
    sp.add_argument("--lang", choices=LANGS)
    sp.add_argument("--force", action="store_true", help="synthesize every line again")
    sp.add_argument("--out", default=out)
    sp.add_argument("--models", default=os.environ.get("TTS_MODELS_DIR", ".tts-models"))
    sp.add_argument("--threads", type=int, default=2)
    sp.set_defaults(fn=cmd_build)

    sp = sub.add_parser("init-bucket", help="create the bucket and its public read policy")
    sp.add_argument("--bucket", default=bucket)
    sp.set_defaults(fn=cmd_init_bucket)

    sp = sub.add_parser("upload", help="upload changed files and manifests")
    sp.add_argument("--bucket", default=bucket)
    sp.add_argument("--out", default=out)
    sp.add_argument("--prune", action="store_true", help="delete bucket files of lines that no longer exist")
    sp.set_defaults(fn=cmd_upload)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
