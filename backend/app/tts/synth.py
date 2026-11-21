"""Silero synthesis (build tool only: needs the ``[tts]`` extra). Weights are downloaded once into TTS_MODELS_DIR,
pinned by sha256, and never committed (each model is 35-150 MB)."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Protocol

from app.tts.voices import Voice

SAMPLE_RATE = 24000

MODELS: dict[str, tuple[str, str]] = {
    "v5_6_ru": ("https://models.silero.ai/models/tts/ru/v5_6_ru.pt",
                "04cc9b1d08ce38bcaa9d02c488d80d3e6806d17f7eaa7c95982f36a3cbf50b2e"),
    "v5_turkic": ("https://models.silero.ai/models/tts/ru/v5_turkic.pt",
                  "891b83d0e0952a72595df3719b76deff9461df2528a8bd226b14ba9da070315a"),
    "v4_uz": ("https://models.silero.ai/models/tts/uz/v4_uz.pt",
              "46c7977beccf2f3c9f730de281f8efefe60ee8f293a2047e89aebe567b3ed4d7"),
}

MAX_CHUNK = 700  # characters per model call; longer texts are split at sentence ends
PAUSE_S = 0.25  # silence between chunks


class Synth(Protocol):
    def synthesize(self, text: str, voice: Voice) -> bytes:
        """Mono 16-bit PCM (little endian) at SAMPLE_RATE."""


def split_text(text: str, limit: int = MAX_CHUNK) -> list[str]:
    parts: list[str] = []
    cur = ""
    for sentence in re.split(r"(?<=[.!?…])\s+", text):
        if cur and len(cur) + 1 + len(sentence) > limit:
            parts.append(cur)
            cur = sentence
        else:
            cur = f"{cur} {sentence}".strip()
    if cur:
        parts.append(cur)
    # a single sentence longer than the limit is cut at commas / spaces
    out: list[str] = []
    for p in parts:
        while len(p) > limit:
            cut = max(p.rfind(",", 0, limit), p.rfind(" ", 0, limit))
            cut = cut if cut > 0 else limit
            out.append(p[:cut + 1].strip())
            p = p[cut + 1:].strip()
        out.append(p)
    return [p for p in out if p]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def ensure_model(models_dir: Path, name: str) -> Path:
    import httpx

    url, sha = MODELS[name]
    path = models_dir / f"{name}.pt"
    if path.exists() and _sha256(path) == sha:
        return path
    models_dir.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".part")
    print(f"downloading {name} from {url}")
    with httpx.stream("GET", url, follow_redirects=True, timeout=60) as r:
        r.raise_for_status()
        with tmp.open("wb") as f:
            for chunk in r.iter_bytes(1 << 20):
                f.write(chunk)
    if _sha256(tmp) != sha:
        tmp.unlink()
        raise RuntimeError(f"{name}: checksum mismatch, refusing to use {url}")
    tmp.replace(path)
    return path


class SileroSynth:
    def __init__(self, models_dir: Path, threads: int = 1) -> None:
        import torch

        torch.set_num_threads(threads)
        self._torch = torch
        self._dir = models_dir
        self._models: dict = {}

    def _model(self, name: str):
        if name not in self._models:
            path = ensure_model(self._dir, name)
            model = self._torch.package.PackageImporter(str(path)).load_pickle("tts_models", "model")
            model.to(self._torch.device("cpu"))
            self._models[name] = model
        return self._models[name]

    def synthesize(self, text: str, voice: Voice) -> bytes:
        import numpy as np

        model = self._model(voice.model)
        pause = np.zeros(int(PAUSE_S * SAMPLE_RATE), dtype=np.float32)
        pieces: list = []
        for chunk in split_text(text):
            audio = model.apply_tts(text=chunk, speaker=voice.speaker, sample_rate=SAMPLE_RATE).numpy()
            pieces += [audio, pause] if pieces else [audio]
        audio = np.concatenate(pieces) if pieces else np.zeros(0, dtype=np.float32)
        # same loudness for every voice: RMS to -20 dBFS, peaks kept under -1 dBFS
        rms = float(np.sqrt(np.mean(audio**2))) if audio.size else 0.0
        if rms > 0:
            audio = audio * (0.1 / rms)
            peak = float(np.max(np.abs(audio)))
            if peak > 0.89:
                audio = audio * (0.89 / peak)
        return (np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes()


def encode_mp3(pcm: bytes, sample_rate: int = SAMPLE_RATE) -> bytes:
    """Mono MP3, 48 kbit/s (about 6 KB per second of speech)."""
    import lameenc

    enc = lameenc.Encoder()
    enc.set_bit_rate(48)
    enc.set_in_sample_rate(sample_rate)
    enc.set_channels(1)
    enc.set_quality(2)
    return bytes(enc.encode(pcm) + enc.flush())
