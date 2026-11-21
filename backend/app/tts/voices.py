"""Who speaks with which voice. Shared by the build tool and the runtime (pure Python, no ML imports).

A speaker's gender comes from, in order: ``voice`` on the character in scenario.json, the player's own character
(always male), a known first name (names.py), Russian role grammar ("Истица", "(сын)"), and finally the default
(male) for characters with only a job title ("Судья", "Эксперт"). The narrator uses ``narrator_voice``.
The same gender is used in both languages: male -> eugene / uzb_0, female -> xenia / dilnavoz.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Literal

from app.scenarios.loader import LoadedScenario
from app.tts.names import FEMALE_KIN, FEMALE_NAMES, FEMALE_ROLE_WORDS, MALE_KIN, MALE_NAMES, MALE_ROLE_WORDS

Lang = Literal["ru", "uz"]
Gender = Literal["male", "female"]
NARRATOR = "narrator"

# audio language -> locale whose texts are spoken (uz-Cyrl sessions hear the uz-Latn recording)
SOURCE_LOCALE: dict[Lang, str] = {"ru": "ru", "uz": "uz-Latn"}


@dataclass(frozen=True)
class Voice:
    id: str  # stable name, part of the line hash: changing a voice re-generates its lines
    model: str  # Silero package (app/tts/synth.py)
    speaker: str
    script: Literal["cyrl", "latn"]  # the only script the model can read


VOICES: dict[tuple[Lang, Gender], Voice] = {
    ("ru", "male"): Voice("ru-eugene", "v5_6_ru", "eugene", "cyrl"),
    ("ru", "female"): Voice("ru-xenia", "v5_6_ru", "xenia", "cyrl"),
    ("uz", "male"): Voice("uz-uzb_0", "v5_turkic", "uzb_0", "cyrl"),
    ("uz", "female"): Voice("uz-dilnavoz", "v4_uz", "dilnavoz", "latn"),
}


def lang_of(locale: str) -> Lang:
    return "uz" if locale.startswith("uz") else "ru"


# Bump when app/tts/text.py starts saying the same text differently (number words, transliteration):
# every line then gets a new hash, so the build re-synthesizes it and browsers fetch the new URL.
TEXT_PIPELINE_VERSION = 2


def line_hash(voice: Voice, text: str) -> str:
    """Identifies one recording: a new text, voice or text pipeline gives a new hash (and a new URL)."""
    return hashlib.sha256(f"{TEXT_PIPELINE_VERSION}\n{voice.id}\n{text}".encode()).hexdigest()[:12]


@dataclass(frozen=True)
class SpeakerVoice:
    gender: Gender
    reason: str  # voice | player | name | role | default | narrator | unknown_name


# "Малика Р.", "Sherzod N.", "Дилшод Каримов": two or more capitalized words = a person's name
_PERSON = re.compile(r"^\s*[A-ZА-ЯЁЎҚҒҲ]\S*\s+[A-ZА-ЯЁЎҚҒҲ]")
_FEMALE_SURNAME = re.compile(r"(ова|ева|ёва|ина|ая|ova|eva|yeva|ina)$")
_MALE_SURNAME = re.compile(r"(ов|ев|ёв|ин|ий|ой|ov|ev|yev|in)$")


def _first_word(text: str) -> str:
    m = re.match(r"\s*([^\s,.(]+)", text)
    return m.group(1).lower() if m else ""


def infer_speaker(loaded: LoadedScenario, speaker: str) -> SpeakerVoice:
    sc = loaded.scenario
    character = next((c for c in sc.characters if c.id == speaker), None)
    if character is None:
        return SpeakerVoice(sc.narrator_voice, "narrator")
    if character.voice:
        return SpeakerVoice(character.voice, "voice")
    if character.id == sc.intro.player_role.character_id:
        return SpeakerVoice("male", "player")

    looks_like_person = False
    for loc in ("ru", "uz-Latn", "uz-Cyrl"):
        name = loaded.texts.get(loc, {}).get(character.name_key, "")
        first = _first_word(name)
        if first in MALE_NAMES:
            return SpeakerVoice("male", "name")
        if first in FEMALE_NAMES:
            return SpeakerVoice("female", "name")
        if _PERSON.match(name):
            looks_like_person = True
            surname = name.split()[1].strip(".,").lower()
            if len(surname) > 3 and _FEMALE_SURNAME.search(surname):
                return SpeakerVoice("female", "name")
            if len(surname) > 3 and _MALE_SURNAME.search(surname):
                return SpeakerVoice("male", "name")

    for loc in ("ru", "uz-Latn"):
        role = loaded.texts.get(loc, {}).get(character.role_key, "")
        kin = {w.lower() for w in re.findall(r"\(([^)]*)\)", role) for w in w.split()}
        if kin & FEMALE_KIN:
            return SpeakerVoice("female", "role")
        if kin & MALE_KIN:
            return SpeakerVoice("male", "role")
        if loc == "ru":
            first = _first_word(role)
            if first in FEMALE_ROLE_WORDS:
                return SpeakerVoice("female", "role")
            if first in MALE_ROLE_WORDS:
                return SpeakerVoice("male", "role")

    # a personal name we do not know: the build tool refuses to guess
    return SpeakerVoice("male", "unknown_name" if looks_like_person else "default")


def voice_for(loaded: LoadedScenario, speaker: str, lang: Lang) -> Voice:
    return VOICES[(lang, infer_speaker(loaded, speaker).gender)]
