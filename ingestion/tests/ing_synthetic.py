"""Синтетические тестовые документы. Всё вымышленное, это не настоящее право."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

LANGS = ("ru", "uz-Latn", "uz-Cyrl")

_T: dict[str, dict[str, Any]] = {
    "ru": dict(
        title="Тестовый закон (вымышленный текст)",
        preamble="Это преамбула тестового закона. Текст вымышленный.",
        section="Раздел I. Общие положения",
        chapter1="Глава 1. Основные правила",
        chapter2="Глава 2. Длинные нормы",
        art="Статья {n}. {t}",
        t1="Первая статья", t2="Вторая статья", t2i="Вставная статья", t4="Длинная статья", t5="Новая статья",
        p1a="Первая часть первой статьи.", point="пункт первой части.", p1b="Вторая часть первой статьи.",
        p2="Текст второй статьи про возврат товара.", p2c="Изменённый текст второй статьи про возврат товара.",
        note="Примечание. Тестовое примечание ко второй статье.",
        p2i="Текст вставной статьи.", repealed="Утратила силу", p5="Текст новой статьи.",
        word="слово", long="Длинный пункт номер",
    ),
    "uz-Latn": dict(
        title="Test qonuni (xayoliy matn)",
        preamble="Bu test qonunining muqaddimasi. Matn xayoliy.",
        section="I-boʻlim. Umumiy qoidalar",
        chapter1="1-bob. Asosiy qoidalar",
        chapter2="2-bob. Uzun normalar",
        art="{n}-modda. {t}",
        t1="Birinchi modda", t2="Ikkinchi modda", t2i="Qoʻshilgan modda", t4="Uzun modda", t5="Yangi modda",
        p1a="Birinchi moddaning birinchi qismi.", point="birinchi qism bandi.", p1b="Birinchi moddaning ikkinchi qismi.",
        p2="Tovarni qaytarish haqida ikkinchi modda matni.", p2c="Tovarni qaytarish haqida oʻzgargan ikkinchi modda matni.",
        note="Izoh. Ikkinchi moddaga test izohi.",
        p2i="Qoʻshilgan modda matni.", repealed="Kuchini yoʻqotgan", p5="Yangi modda matni.",
        word="soʻz", long="Uzun band raqami",
    ),
    "uz-Cyrl": dict(
        title="Тест қонуни (хаёлий матн)",
        preamble="Бу тест қонунининг муқаддимаси. Матн хаёлий.",
        section="I-бўлим. Умумий қоидалар",
        chapter1="1-боб. Асосий қоидалар",
        chapter2="2-боб. Узун нормалар",
        art="{n}-модда. {t}",
        t1="Биринчи модда", t2="Иккинчи модда", t2i="Қўшилган модда", t4="Узун модда", t5="Янги модда",
        p1a="Биринчи моддaнинг биринчи қисми.", point="биринчи қисм банди.", p1b="Биринчи модданинг иккинчи қисми.",
        p2="Товарни қайтариш ҳақида иккинчи модда матни.", p2c="Товарни қайтариш ҳақида ўзгарган иккинчи модда матни.",
        note="Изоҳ. Иккинчи моддага тест изоҳи.",
        p2i="Қўшилган модда матни.", repealed="Кучини йўқотган", p5="Янги модда матни.",
        word="сўз", long="Узун банд рақами",
    ),
}
# ASCII-«a» в p1a для uz-Cyrl случайно латинская; заменяем, чтобы тест не зависел от опечатки
_T["uz-Cyrl"]["p1a"] = "Биринчи модданинг биринчи қисми."

LONG_PARTS = 12


def blocks(lang: str, variant: str = "v1") -> list[tuple[str, str]]:
    """[(вид, текст)], вид: h1 | h | p. Статьи: 1, 2, 2¹, 3 (утратила силу), 4 (длинная); v2 меняет 2 и добавляет 5."""
    t = _T[lang]
    art = lambda n, title: t["art"].format(n=n, t=title)  # noqa: E731
    out: list[tuple[str, str]] = [("h1", t["title"]), ("p", t["preamble"]), ("h", t["section"]), ("h", t["chapter1"])]
    out += [("h", art(1, t["t1"])), ("p", t["p1a"]), ("p", "1) " + t["point"]), ("p", t["p1b"])]
    if variant == "empty":
        out += [("h", art(2, t["t2"]))]
    else:
        out += [("h", art(2, t["t2"])), ("p", t["p2c"] if variant == "v2" else t["p2"]), ("p", t["note"])]
    out += [("h", art("2¹", t["t2i"])), ("p", t["p2i"])]
    if variant != "gap":
        out += [("h", art(3, t["repealed"]))]
    out += [("h", t["chapter2"]), ("h", art(4, t["t4"]))]
    out += [("p", f"{t['long']} {i}. " + " ".join([t["word"]] * 120)) for i in range(1, LONG_PARTS + 1)]
    if variant == "v2":
        out += [("h", art(5, t["t5"])), ("p", t["p5"])]
    return out


def html_doc(lang: str, variant: str = "v1") -> str:
    body = []
    for kind, text in blocks(lang, variant):
        text = text.replace(" ", "&nbsp;", 1)  # мусор, который normalize обязан убрать
        if kind == "h1":
            body.append(f"<h1>{text}</h1>")
        elif kind == "h":
            body.append(f"<p><b>{text}</b></p>")
        else:
            body.append(f"<p>{text}</p>")
    return (
        '<!doctype html><html><head><meta charset="utf-8"><title>site</title>'
        "<script>var tracker = 1;</script><style>p { color: red }</style></head><body>"
        "<header>Шапка сайта</header><nav><a href='/'>Меню сайта</a></nav><div class='menu'>Боковое меню</div>"
        '<main id="content">' + "".join(body) + "</main>"
        "<footer>Подвал сайта</footer><script>track()</script></body></html>"
    )


def write_docx(path: Path, lang: str, variant: str = "v1") -> None:
    import docx

    d = docx.Document()
    for kind, text in blocks(lang, variant):
        if kind == "h1":
            d.add_heading(text, level=1)
        elif kind == "h":
            d.add_paragraph().add_run(text).bold = True
        else:
            d.add_paragraph(text)
    d.save(str(path))


def write_source(legal_dir: Path, key: str, lang: str, eff: str, variant: str = "v1", fmt: str = "html") -> str:
    """Положить файл в legal_dir/raw, вернуть относительный путь для sources.yaml."""
    rel = f"raw/{key}_{lang}_{eff}.{fmt}"
    path = legal_dir / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "html":
        path.write_text(html_doc(lang, variant), encoding="utf-8")
    else:
        write_docx(path, lang, variant)
    return rel


def version_entry(key: str, lang: str, eff: str, rel: str, verified_by: str | None = "QA", official: bool | None = True) -> dict:
    return {
        "language": lang,
        "file": rel,
        "source_url": f"https://example.test/{key}/{lang}",
        "effective_from": date.fromisoformat(eff),
        "is_official_text": official,
        "retrieved_at": date(2026, 11, 1),
        "verified_by": verified_by,
    }


def document_entry(key: str, versions: list[dict], known_gaps: dict | None = None) -> dict:
    d = {
        "document_key": key,
        "title": {"ru": "Тестовый закон", "uz-Latn": "Test qonuni", "uz-Cyrl": "Тест қонуни"},
        "document_type": "law",
        "source_url": f"https://example.test/{key}",
        "status": "in_force",
        "versions": versions,
    }
    if known_gaps:
        d["known_gaps"] = known_gaps
    return d


def write_sources_yaml(legal_dir: Path, documents: list[dict]) -> Path:
    path = legal_dir / "sources.yaml"
    path.write_text(
        yaml.safe_dump({"terms_of_use": {"fetch_allowed": False}, "documents": documents}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return path
