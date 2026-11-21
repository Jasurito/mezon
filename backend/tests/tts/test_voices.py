"""Who speaks with which voice: name, surname, role grammar, player, narrator, override."""

import pytest

from app.tts.lines import spoken_lines
from app.tts.voices import VOICES, infer_speaker, line_hash, voice_for


def _set(loaded, name: str, role: str = "Свидетель") -> None:
    for loc in ("ru", "uz-Latn", "uz-Cyrl"):
        loaded.texts.setdefault(loc, {})
        loaded.texts[loc]["char.expert.name"] = name if loc == "ru" else ""
        loaded.texts[loc]["char.expert.role"] = role if loc == "ru" else ""


def test_fixture_cast(loaded):
    got = {s: infer_speaker(loaded, s) for s in ("judge", "plaintiff", "defendant_rep", "plaintiff_rep", "narrator")}
    assert (got["judge"].gender, got["judge"].reason) == ("male", "default")
    assert (got["plaintiff"].gender, got["plaintiff"].reason) == ("male", "name")  # Дилшод Каримов
    assert (got["defendant_rep"].gender, got["defendant_rep"].reason) == ("female", "name")  # Нодира Юсупова
    assert (got["plaintiff_rep"].gender, got["plaintiff_rep"].reason) == ("male", "player")
    assert (got["narrator"].gender, got["narrator"].reason) == ("female", "narrator")


@pytest.mark.parametrize(
    "name,role,gender,reason",
    [
        ("Малика Р.", "Истец", "female", "name"),
        ("Нилуфар А.", "Истица", "female", "name"),  # does not end in -а: found by the name list
        ("Sherzod N.", "x", "male", "name"),
        ("Гульсара Каримова", "x", "female", "name"),  # unknown first name, feminine surname
        ("Ботир Алиев", "x", "male", "name"),
        ("Фарход Х.", "Представитель ответчицы Зарины Х. (сын)", "male", "name"),
        ("Продавец", "Продавщица магазина", "female", "role"),
        ("Свидетель", "Истица, студентка", "female", "role"),
        ("Представитель", "Представитель ответчицы Зарины Х. (сын)", "male", "role"),
        ("Эксперт", "Судебный эксперт", "male", "default"),
        ("Зумрад Х.", "Свидетель", "male", "unknown_name"),  # build refuses to guess
    ],
)
def test_inference(loaded, name, role, gender, reason):
    _set(loaded, name, role)
    got = infer_speaker(loaded, "expert")
    assert (got.gender, got.reason) == (gender, reason)


def test_override_wins(loaded):
    loaded.scenario.characters[0].voice = "female"  # judge
    assert infer_speaker(loaded, "judge").reason == "voice"
    assert voice_for(loaded, "judge", "ru") == VOICES[("ru", "female")]
    assert voice_for(loaded, "judge", "uz") == VOICES[("uz", "female")]


def test_same_gender_in_both_languages(loaded):
    assert voice_for(loaded, "defendant_rep", "ru").speaker == "xenia"
    assert voice_for(loaded, "defendant_rep", "uz").speaker == "dilnavoz"
    assert voice_for(loaded, "judge", "ru").speaker == "eugene"
    assert voice_for(loaded, "judge", "uz").speaker == "uzb_0"


def test_hash_depends_on_voice_and_text():
    ru_m, ru_f = VOICES[("ru", "male")], VOICES[("ru", "female")]
    assert line_hash(ru_m, "a") == line_hash(ru_m, "a")
    assert line_hash(ru_m, "a") != line_hash(ru_f, "a")
    assert line_hash(ru_m, "a") != line_hash(ru_m, "b")


def test_spoken_lines_cover_say_and_scripted_npc_answers(loaded):
    lines = spoken_lines(loaded.scenario)
    keys = {(line.speaker, line.text_key) for line in lines}
    assert len(keys) == len(lines)  # no duplicates
    assert ("narrator", "line.intro.narrator") in keys
    for q in loaded.scenario.npc_questions:
        assert (q.character_id, q.answer_key) in keys
